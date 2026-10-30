# Superpowers Backplane governance

Source file: `/Users/jeff/Documents/Code/superpowers-backplane/docs/superpowers-backplane/governance.md` (local repository; read in full, 283 lines). Access date: 2026-10-30. All excerpts **primary**. Quotations verbatim; source line wraps reflowed.

## Ownership

Source: § "Ownership and authority". Primary.

> | Work identity, scope, acceptance, hierarchy, dependencies, lifecycle | Native GitHub issue and relationships | Use repository plus issue URL/number; preserve full native intake. |
> | Design | Human-approved complete issue body for bounded work, or approved specification for a cross-cutting decision | Both paths are valid. Resolve conflicts with the approver. |
> | Execution | Current approved issue-bound Superpowers plan | Record consumed issue/design revisions and project verification seams. |
> | Criterion satisfaction | Accepted immutable project-owned evaluation evidence | Bind the verdict to exact approved criteria and delivery inputs. |

## Record kinds and codes

Source: § "Product identity and decomposition". Primary.

> A project supplies its code legend. For example, `INSTALL1` is a capability and `INSTALL1.1` is an outcome; these are invented mnemonic examples, not prescribed syntax, ordering, dates, or versions. Codes are unique within their declared namespace and remain stable when release targets or parentage change.

> Use record kinds `capability`, `outcome`, `gate`, and `external-boundary`. A grouping capability is not an implementation leaf. A small feature may itself be the bounded outcome; do not create redundant layers.

> | `Obligation Dispositions` | Parent obligation and governing revision, bounded child contributions or accepted evidence, owner, approved deferral/exclusion, unresolved gaps. |
> | `Coverage and Satisfaction` | Current criterion-to-requirement mappings and pointers to accepted evaluations, including changed-input and outstanding-contribution findings. |

## Obligations, coverage, and shared coverage

Source: § "Product identity and decomposition". Primary.

> Account for every approved parent obligation through bounded child outcomes, eligible existing satisfaction evidence, or an explicitly approved disposition. Reject omissions, unrelated additions, and ambiguous duplicated ownership. Shared coverage is valid when contribution boundaries and the owner accepting the combined result are explicit. Preserve the existing issue when it matches; classify proposed new work and unresolved questions separately. Decomposition approval alone authorizes no issue creation, selection, or readiness transition.

> Deferral/exclusion records identify their approver, governing revision, rationale, and revisit condition where applicable. They remain visible and do not count as delivered. A child closed as not planned does not satisfy its obligation; its parent needs approved alternative coverage or a scope disposition. Dependencies establish readiness, not priority. Parentage describes decomposition, not execution order. No priority is inferred from list order or codes.

Source: § "Coverage and satisfaction". Primary.

> A requirement reference includes its governing issue/document identity, stable criterion/statement key, approved revision, and wording. Retain a project's existing identifiers. Line numbers and checkbox positions are not durable keys. Many requirements may map to one outcome, and several issues/PRs may contribute to one criterion. State each contribution's scope and combined-result owner.

> The outcome issue owns the current mappings and latest accepted evaluation pointers. The evaluation is immutable evidence with exact inputs, method, observed result, delivery/integration identity, review/acceptance disposition, evidence identity/availability, and remaining obligations. Preserve historical evaluations against their original revisions. Parent summaries reference child results rather than maintaining independent verdict copies.

> | `SATISFIED` | Applicable obligations have accepted passing evidence against the exact reconciled current inputs. |
> | `UNSATISFIED` | Accepted evidence establishes an unmet applicable obligation. |
> | `UNKNOWN` | Execution, input matching, evidence, or acceptance is unavailable or unverified. |

> Deferral and exclusion are scope dispositions, separate from this result vocabulary. Missing evidence is UNKNOWN, not success or a fabricated failure. Feature satisfaction requires every applicable obligation to be satisfied, with approved excluded/deferred scope separately disclosed.

> A behavior-changing requirement or implementation delta makes affected current claims unsupported until evidence is reconciled/revalidated. A prior pass at commit B does not prove commit C.

## Release targets and release

Source: § "GitHub presentation". Primary.

> Use issue-backed items and four views: product/decomposition, execution, satisfaction, and release targets.

> Closed-child counts count closures, not satisfied obligations. A milestone groups targets; it does not authorize publication.

> Project drafts and Discussions may support preliminary deliberation; they are not approved executable work.

Source: § "Bridge operations and Superpowers sequence". Primary.

> 2. Consume an approved product/design result and assess complete decomposition.
> 3. Reconcile proposed/existing records and native relationships through an explicitly authorized intake operation.
> 4. Plan one bounded selected issue against current issue/design revisions, approved acceptance criteria, and project-owned verification seams.

> 8. Evaluate release inclusion/publication under separate release authority.

Source: § "PR contributions and completion". Primary.

> Review acceptance, merge, integrated verification, satisfaction, issue/parent completion, and release are distinct.

## Worked example

Source: § "Boundaries and worked example". Primary.

> Invented example: `INSTALL1` owns O1 source adoption, O2 discovery, and O3 preservation. Existing outcome `INSTALL1.1` covers O1. Two proposed outcomes split O2 into enumeration and invocation with an explicit combined-result owner; accepted E3 covers O3 at S1. An approved O2 deferral is a separate valid disposition, not delivery. The parent issue maintains those dispositions and native child links.

> A design PR establishes S1, a package PR contributes O1, and a verification PR contributes discovery. Partial delivery or accepted review alone cannot close the outcome.

## Shape as stated

Backplane's record kinds are `capability` (a grouping, not an implementation leaf), `outcome`, `gate`, and `external-boundary`, carried on native GitHub issues with native parent and dependency links. A parent capability holds **obligations**; each must be accounted for by bounded child outcomes, existing accepted evidence, or an approved deferral/exclusion disposition, and the parent issue keeps those dispositions. Requirements map many-to-one onto outcomes, and several issues/PRs may contribute to one criterion when a combined-result owner is named. Satisfaction is a per-obligation verdict (`SATISFIED`/`UNSATISFIED`/`UNKNOWN`) bound to immutable evaluations of exact inputs; "feature satisfaction requires every applicable obligation to be satisfied", with deferred/excluded scope disclosed. Dependencies set readiness only; parentage is decomposition, not order. Release targets are a view; a GitHub milestone "groups targets" but does not authorize publication; release inclusion is evaluated under separate release authority. The document names no separate value-bundle container beyond the capability-with-obligations, and no named prerequisite/enabler kind beyond dependency edges.
