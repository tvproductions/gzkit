"""Cross-platform durability barriers for a committed on-disk change (GHI #952).

This module exists so the repository holds exactly ONE implementation of
"make this change survive a power loss". It is the same argument
:mod:`gzkit.file_lock` records for the OS lock, and the same one
``ownership.write_bytes_atomically`` states about its own ordering: two
implementations of a barrier drift apart, and the drift only manifests under
the one condition ordinary use does not exercise.

Three stores need it now. ``gzkit.content.ownership`` commits a declaration's
rename; ``gzkit.commands.content.unown`` commits a journal's REMOVAL before any
dependent is deleted; and :meth:`gzkit.ledger.Ledger.create` commits a newly
created ledger's directory entry, without which a first append reports success
on a file a crash can lose whole.

It lives at package level rather than under ``gzkit.content`` for the reason
that move made unavoidable: ``gzkit.content.ownership`` imports
``gzkit.ledger``, so the barrier could not travel the other way while it lived
there. Nothing about ``fsync`` on a directory descriptor is content-specific —
the home belonged to neither caller.

**A barrier is a filesystem flush boundary, not a proof against arbitrary
hardware faults.** It is subject to the filesystem and the storage honoring the
operation. Failures propagate; they are never swallowed, because a swallowed
barrier reports a durability claim the caller cannot check.
"""

from __future__ import annotations

import ctypes
import errno
import os
from pathlib import Path
from typing import Any

BARRIER_UNSUPPORTED_ERRNOS: frozenset[int] = frozenset(
    {errno.EINVAL, errno.ENOSYS, errno.ENOTSUP, errno.EOPNOTSUPP}
)
"""Directory-sync errors needing a capability remedy rather than an unchanged retry.

These report an unsupported or invalid operation at the attempted location;
the errno alone does not identify a particular filesystem. Classification
changes diagnostic guidance, never the requirement to establish the barrier.
Writers propagate these errors, and cleanup must preserve dependents and refuse.
"""


def commit_directory_entry(directory: Path) -> None:
    r"""Commit *directory*'s pending entry changes — the barrier, stated ONCE.

    A directory entry created by `os.replace` or destroyed by `Path.unlink` is
    buffered metadata on POSIX: the operation is atomic but NOT durable, so a
    power loss immediately afterwards can leave the directory still naming the
    old inode, or still naming an unlinked one. Syncing the parent directory is
    what commits the entry, and this store is the ONE artifact gating the
    unowned-byte ratchet.

    IT IS EXTRACTED RATHER THAN DUPLICATED BECAUSE THE REMOVAL SIDE NEEDS THE
    SAME BARRIER FOR A DIFFERENT INVARIANT. `write_bytes_atomically` needs it
    so a VISIBLE file is a DURABLE one -- one file's own durability, where a
    crash before the fsync and a crash before the rename are equally harmless.
    `commands/content/unown.py` needs it for CROSS-FILE ORDERING: the
    pending-transition journal gates replay of every dependent recovery file,
    so the journal's absence must be committed before any dependent is deleted
    or its path reused. Without the barrier between them, nothing forbids the
    dependents' entry removals committing while the journal's does not --
    journal back, retained source gone. That the two directories differ (the
    journal beside the declaration, the extract beside the surface) is exactly
    why the barrier is a function taking one: each entry is committed in the
    directory that holds it.

    POSIX syncs an open directory descriptor. Windows sends a normal native
    flush request through a writable directory handle; flags zero requests
    metadata and underlying-storage cache synchronization. Both paths require
    successful completion and propagate failures. These are filesystem flush
    boundaries, subject to the filesystem and storage honoring that operation,
    not an independent proof against arbitrary hardware or power-loss faults.
    """
    if os.name == "nt":
        _commit_windows_directory(directory)
        return
    if os.name != "posix":
        raise OSError(errno.ENOTSUP, "directory synchronization is unsupported", str(directory))
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


class _WindowsStatusOrPointer(ctypes.Union):
    """The native IO_STATUS_BLOCK union retains pointer-size alignment."""

    _fields_ = [("Status", ctypes.c_int32), ("Pointer", ctypes.c_void_p)]


class _WindowsIOStatusBlock(ctypes.Structure):
    """Windows NTSTATUS is 32 bits, even where a Python C long is 64 bits."""

    _anonymous_ = ("Result",)
    _fields_ = [("Result", _WindowsStatusOrPointer), ("Information", ctypes.c_size_t)]


# Only an unexpectedly failed completion wait reaches this retention path.
# The kernel may still reference the output buffer, so keep it alive until
# process exit instead of letting error handling free pending native I/O memory.
_PENDING_DIRECTORY_FLUSHES: list[_WindowsIOStatusBlock] = []


def _windows_directory_apis() -> tuple[Any, Any]:
    """Bind the Windows calling convention and exact native argument widths."""
    try:
        # These APIs exist only on Windows; POSIX ctypes type stubs omit them.
        win_dll = getattr(ctypes, "WinDLL")  # noqa: B009 - platform-conditional ctypes API
        kernel32 = win_dll("kernel32", use_last_error=True)
        ntdll = win_dll("ntdll")
        kernel32.CreateFileW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        kernel32.CreateFileW.restype = ctypes.c_void_p
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int32
        kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel32.WaitForSingleObject.restype = ctypes.c_uint32
        ntdll.NtFlushBuffersFileEx.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(_WindowsIOStatusBlock),
        ]
        ntdll.NtFlushBuffersFileEx.restype = ctypes.c_int32
        ntdll.RtlNtStatusToDosError.argtypes = [ctypes.c_int32]
        ntdll.RtlNtStatusToDosError.restype = ctypes.c_uint32
    except AttributeError as exc:
        message = "native Windows directory synchronization is unavailable"
        raise OSError(errno.ENOSYS, message) from exc
    return kernel32, ntdll


def _windows_directory_error(directory: Path, code: int | None = None) -> OSError:
    """Keep Win32's errno mapping and the failing directory in the propagated error."""
    if code is None:
        # kernel32 is bound with `use_last_error=True`, so ctypes parks the
        # callee's GetLastError in a thread-local slot that only
        # `get_last_error()` reads back. A bare `WinError()` reads the LIVE
        # value, which is the PRE-call one; a stale or zero code maps to EINVAL,
        # and EINVAL sits in BARRIER_UNSUPPORTED_ERRNOS, so a transient sharing
        # fault would be reported with the capability remedy.
        code = getattr(ctypes, "get_last_error")()  # noqa: B009 - platform-conditional ctypes API
    error = getattr(ctypes, "WinError")(code)  # noqa: B009 - platform-conditional ctypes API
    error.filename = str(directory)
    return error


def _commit_windows_directory(directory: Path) -> None:
    """Flush directory metadata using the synchronous native Windows operation.

    CreateFileW's BACKUP_SEMANTICS flag permits opening a directory; no backup
    privilege or volume handle is requested. NtFlushBuffersFileEx flags zero
    requests data, metadata, and storage-cache synchronization. Its return is
    authoritative except for STATUS_PENDING, which requires a completed wait
    and the IO_STATUS_BLOCK result. See Microsoft's NtFlushBuffersFileEx and
    IO_STATUS_BLOCK contracts, not the weaker data-only flush flags.
    """
    kernel32, ntdll = _windows_directory_apis()
    # GENERIC_WRITE; share read/write/delete; OPEN_EXISTING; BACKUP_SEMANTICS.
    # Omitting FILE_FLAG_OVERLAPPED makes this an owned synchronous handle.
    handle = kernel32.CreateFileW(str(directory), 0x40000000, 7, None, 3, 0x02000000, None)
    if not handle or handle == ctypes.c_void_p(-1).value:
        raise _windows_directory_error(directory)
    status_block = _WindowsIOStatusBlock()
    status_block.Status = ctypes.c_int32(0xC0000001).value  # non-success until written
    try:
        status = ntdll.NtFlushBuffersFileEx(handle, 0, None, 0, ctypes.byref(status_block))
        if status == 0x103:  # STATUS_PENDING is not completed success.
            wait_result = kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
            if wait_result != 0:  # WAIT_OBJECT_0
                _PENDING_DIRECTORY_FLUSHES.append(status_block)
                if wait_result == 0xFFFFFFFF:  # WAIT_FAILED owns GetLastError.
                    raise _windows_directory_error(directory)
                message = f"Windows directory completion wait returned {wait_result:#x}"
                raise OSError(errno.EIO, message, str(directory))
            status = status_block.Status
            if status == 0x103:
                _PENDING_DIRECTORY_FLUSHES.append(status_block)
                raise OSError(errno.EIO, "Windows directory flush remains pending", str(directory))
        if status != 0:  # STATUS_SUCCESS; warnings cannot establish this boundary.
            raise _windows_directory_error(directory, ntdll.RtlNtStatusToDosError(status))
    finally:
        if not kernel32.CloseHandle(handle):
            raise _windows_directory_error(directory)
