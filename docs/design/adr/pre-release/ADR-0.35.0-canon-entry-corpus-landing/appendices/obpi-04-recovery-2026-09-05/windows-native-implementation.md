# Windows directory barrier implementation — 2026-09-05

Scope: `src/gzkit/content/ownership.py` and `tests/content/test_ownership.py` only. No commit, CI, ledger, lock, or pipeline mutation was performed by this implementer.

## Implemented behavior

- `commit_directory_entry` now sends Windows requests through a native directory flush; POSIX retains the existing directory-descriptor `fsync`.
- Native binding uses stdlib `ctypes`, Windows calling convention, 32-bit NTSTATUS/ULONG/BOOL, pointer-sized handles and an aligned IO_STATUS_BLOCK.
- `CreateFileW` requests GENERIC_WRITE, read/write/delete sharing, OPEN_EXISTING and BACKUP_SEMANTICS. No overlapped flag, backup privilege, volume handle, dependency, or alternative mechanism is introduced.
- `NtFlushBuffersFileEx` uses flags zero. The ordinary return is authoritative; STATUS_PENDING requires a completed wait followed by the IO_STATUS_BLOCK status. Warning/error status, failed open/close/wait, missing API and unsupported host all propagate OSError instead of success.
- Owned handles are closed in `finally`. If an unexpected pending operation cannot be observed complete, its small output buffer is retained until process exit to avoid freeing kernel-referenced memory; the operation still raises. The test doubles remove only their own artificial retained buffers.
- Native success tests transparently observe actual DLL calls. `GetFinalPathNameByHandleW` and `os.path.samefile` establish the opened handle's actual directory, then real native flushes must complete after the atomic replacement and after unlink. The identical assertion rejects both a no-op barrier and a real handle opened on another directory.

## Observed local evidence

- `windows-barrier-red.log`: the existing Windows no-op produced **one assertion failure, zero errors** because unavailable native synchronization returned success.
- `windows-barrier-green.log`: the same test passed after implementation.
- `windows-ownership-green.log`: **83 tests OK, 3 skips**. The skips are the three real Windows native tests on this macOS host; they remain required on Windows CI.
- `windows-barrier-mutations.json`: **6/6 in-memory mutations rejected by assertions, zero errors** — Windows no-op, ignored flush status, accepting pending without completion, ignored close failure, wrong NTSTATUS width, unknown-platform no-op. These are bounded local negative controls, not the final OBPI mutation sweep.
- Scoped ruff, ruff format check, ty and C/C/C xenon all exited 0. `git diff --check` passed.
- Combined initial run (`windows-barrier-scoped.log`) ran 203 tests with 3 Windows skips and one failure in root's concurrent landed-barrier diagnostic correction. That failure was reported to root; it is not claimed as a green result.

Hashes at handoff:

- ownership.py: `cbd93539fb5c262b19a26f242b7ad12a33e5dc674bc7524067e2a1f550849057`
- test_ownership.py: `5f3c6646169197620d845efbe979c01df91a33e268478576e91956759c4c74db`

## Evidence still required

The standalone candidate previously completed on an actual Windows runner (root's run 33972482837). **This integrated production implementation has not yet run on Windows.** Root must run its three real native tests and the normal Windows scoped suite; local native-call doubles do not substitute.

This establishes an operative filesystem flush boundary under the operating system/storage contract, not an independently demonstrated power-cut or arbitrary faulty-hardware guarantee. It does not change the declared ledger exceptions or platform requirements.

API references used:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntflushbuffersfileex
- https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_status_block
- CreateFileW's directory-handle behavior and the actual candidate mechanism were supplied by the previously completed Windows capability investigation.
