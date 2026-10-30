# Work breakdown structure, control account, work package, planning package

Access date for every source: 2026-10-30.

## Retrieval status

| Source | Status |
| --- | --- |
| PMI, *Practice Standard for Work Breakdown Structures* (3rd ed.) and *PMBOK Guide* | **Not read**: commercial standards; no open copy. |
| PMI article "Developing and elaborating work breakdown structures", https://www.pmi.org/learning/library/developing-elaborating-work-breakdown-structures-7241 (cited by FDAU) | **Refused**: automated GET returned HTTP 403. Not worked around. |
| U.S. DoD, *Earned Value Management System Interpretation Guide* (DoD EVMSIG), 14 March 2019 | **Read** (90 pp.). Copy obtained from https://www.humphreys-assoc.com/evms/evms-documents/dod/DoD_EVMSIG_14MAR2019.pdf, a third-party mirror of the government document. Primary text (a U.S. government guide interpreting EIA-748); mirror provenance noted. |
| NASA, *Work Breakdown Structure (WBS) Handbook*, NASA/SP-20210023927, November 2021 | **Read** from https://www.nasa.gov/wp-content/uploads/2023/08/nasa-work-breakdown-structure-handbook.pdf. Primary. |

Because the PMI texts were not read, PMI's own wording (including its "100% rule") is not quoted here.

## DoD EVMSIG (2019), glossary

Source: DoD EVMSIG, glossary, pp. 85–89. Primary.

> WORK BREAKDOWN STRUCTURE (WBS) — A hierarchical product-oriented division of program tasks depicting the breakdown of work scope for work authorization, tracking, and reporting purposes.

> WORK BREAKDOWN STRUCTURE (WBS) DICTIONARY — A listing of WBS elements with a description of the work scope content in each element. The work descriptions are normally summary level and provide for clear segregation of work for work authorization and accounting purposes.

> CONTROL ACCOUNT — The control account is the intersection of one WBS element and one organizational structure element representing a specific portion of program scope assigned to an individual manager. The control account is the minimum level where technical, schedule, and cost responsibility exists.

> CONTROL ACCOUNT PLAN — The documented representation of the time-phased integration of scope, schedule and resources for all control account authorized work.

> WORK PACKAGE (WP) — Natural subdivision of control accounts. A WP is simply a task/activity or grouping of work. A WP is the point at which work is planned, progress is measured, and earned value is computed.

> PLANNING PACKAGE (PP) — A logical aggregation of future work within a control account that cannot yet be planned in detail at the work package or task level.

> SUMMARY LEVEL PLANNING PACKAGE (SLPP) — An aggregation of work for far-term efforts that are not able to be identified at the control account level, but can be distributed to reporting level Work Breakdown Structure elements (and, therefore, are not “Undistributed Budget”).

> ROLLING WAVE — The continuous process of converting Summary Level Planning Packages into control accounts and control account planning packages into work packages.

> BLOCK PLANNING — The periodic process of converting Summary Level Planning Packages into control accounts and control account planning packages into work packages. The time period chosen reflects blocks of time from a specific contractual milestone to a subsequent specific contractual milestone.

## DoD EVMSIG (2019), Guideline 10 (work packages and planning packages)

Source: DoD EVMSIG, Guideline 10, pp. 27–29. Primary.

> Purpose of Guideline: To ensure control account work scope is partitioned into executable and measurable segments of work that are accomplished within the authorized control account period of performance (POP).

> Intent of Guideline: The control account is the management control point where program cost, schedule, and work scope requirements are integrated and managed. Control accounts are decomposed into work packages and planning packages, segregated by elements of cost. [...] Work packages reflect the expected way the work is to be done and are a distinguishable subdivision of a control account, assignable to a single program organizational element. This is where the work is planned, technical progress is measured, and earned value is determined. [...] A work package/planning package shall not have a budget without an assigned scope of work. Conversely, a work package/planning package shall not have authorized scope without an associated budget.

> Work packages have the following characteristics:
> o Represent the scope of work at the level where work is performed or aggregated.
> o Are distinguishable from all other work packages.
> o Are assigned to a single organizational element.
> o Include scheduled start and completion dates; and as applicable, interim milestones, all of which are representative of technical accomplishment.
> o Have a time-phased budget or value expressed in terms of dollars, labor hours, or other measurable units that is substantiated in terms of supporting project plans.
> o Have durations that are limited to a span of time that is practical for the work scope. Longer-duration work packages have interim objective measures, such as points of technical achievement, to enable accurate performance assessment.
> o Are identified within the Integrated Master Schedule (IMS) and other supporting schedules.

> This must also include a designated “freeze period” which supports forward planning discipline.

Source: DoD EVMSIG, Organization category introduction, p. 7. Primary.

> A structured approach for decomposing the program work into manageable segments creates the Work Breakdown Structure (WBS) (Guideline 1) wherein each WBS element contains a specific scope of work. The work is typically defined in the WBS Dictionary and includes a description of the technical content for each element.

## NASA WBS Handbook (2021)

Source: NASA/SP-20210023927, § 2. Primary.

> A WBS is a product-oriented family tree that identifies the hardware, software, services, and all other deliverables required to achieve an end project objective. The purpose of a WBS is to subdivide the project’s work content into manageable segments to facilitate planning and control of cost, schedule, and technical content. [...] It identifies the total project work to be performed, which includes not only all NASA in-house work content, but also all work content to be performed by contractors, international partners, universities, or any other performing entities. Work scope not contained in the project WBS should not be considered part of the project.

> The project WBS structure should encompass the entire project’s approved scope of work. It usually consists of multiple levels of products along with associated work content definitions that are contained in a companion document called the WBS Dictionary.

Source: NASA/SP-20210023927, § 3 (product and enabling content). Primary.

> As stated earlier, a project WBS, while being predominantly product-oriented, must also reflect all the effort that is in the approved scope of work. Because of this, common elements of work must be included that are not necessarily product-oriented. This effort is typically accomplished by “enabling organizations,” such as project management, safety and mission assurance, etc.

Source: NASA/SP-20210023927, pp. 25–26 (control accounts). Primary.

> A CA, if needed, may be subdivided further into Work Packages (WPs) and Planning Packages (PPs). A WP provides further detail on work content that is considered near-term, while a PP defines far-term work at a summary level.

> A CA generally consists of one or more WPs and may include one or more PPs. A WP is the unit of work required to complete a specific job such as a test, a report, a design, a set of drawings, fabrication of a piece of hardware, or a service. A planning package is a logical aggregation of work within a CA containing far-term effort which can be identified and budgeted in early baseline planning at a higher level, but cannot yet be adequately defined into a WP.

## Shape as stated

The **WBS** is a product-oriented hierarchy of all deliverables and work in the approved scope ("work scope not contained in the project WBS should not be considered part of the project"); it includes non-product "common" or **enabling** elements (project management, safety and mission assurance) alongside product elements. The **WBS dictionary** is the companion list describing each element's scope. A **control account** is the intersection of one WBS element with one organizational element under one manager, the lowest level of cost/schedule/technical responsibility. Each control account is fully divided into **work packages** (near-term, detail-planned, single owner, dated, budgeted, where progress and earned value are measured) and **planning packages** (far-term work budgeted but not yet detailed). Far-term work not yet assignable to a control account sits in **summary level planning packages**. **Rolling wave** or **block planning** converts SLPPs into control accounts and planning packages into work packages, with a "freeze period" for near-term planning. Scope and budget must always travel together in WPs and PPs. These sources define no value-grouping container and no release record; their grouping axis is product/deliverable decomposition and organizational responsibility.
