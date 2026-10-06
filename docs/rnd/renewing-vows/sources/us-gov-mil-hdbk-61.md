# MIL-HDBK-61B w/Change 1, Configuration Management Guidance

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is source research, not a skill implementation or operator ruling. Public domain (US federal government work). Read live on this date at the URL(s) below.

## Bibliographic facts

- Issuing body: US Department of Defense. ASSIST lists the preparing activity as the Department of the Navy Standardization Office, DASN (RDT&E) (DepSO). Custodians: Army, US Army Combat Capabilities Development Command, Armaments Center; Navy, Department of the Navy Standardization Office; Air Force, Air Force Life Cycle Management Center - Aircraft Systems; Other, Director, Systems Engineering.
- Document: MIL-HDBK-61B w/CHANGE 1, "Department of Defense Handbook: Configuration Management Guidance", 15 August 2025, superseding MIL-HDBK-61B of 7 April 2020. Cover markings: "NOT MEASUREMENT SENSITIVE"; "AMSC N/A"; "AREA SESS"; Distribution Statement A.
- Status: Active (ASSIST QuickSearch, read 2026-10-06). ASSIST revision history: Revision B Change 1 (change incorporated), 15-AUG-2025, 82 pages; Revision B, 07-APR-2020, 84 pages; Revision A, 07-FEB-2001, 221 pages; Base Document, 30-SEP-1997, 207 pages. Next review due 14-AUG-2030.
- Nature: guidance, not a requirement. The cover says "This handbook is for guidance only. Do not cite this document as a requirement."
- Change 1 summary: the handbook's "Summary of Change 1 Modifications" lists paragraph 3.3 (Definitions) as "Deletion", among other modifications. The definitions below are those in the change-incorporated text.
- Official URLs read:
  - ASSIST QuickSearch document details: <https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=202239>
  - The Revision B Change 1 PDF, reached from that page's document link: <https://quicksearch.dla.mil/WMX/Default.aspx?token=5796547>. Every page carries the stamp "Source: https://assist.dla.mil -- Downloaded: 2026-10-06T10:16Z".
- Transcription: verbatim from page images of the official PDF. Underlined run-in headings are not reproduced, typographic apostrophes are normalized, and `[…]` marks an omission. Definitions-table rows are rendered as "Term: definition". Page references are the handbook's printed page numbers.

## Excerpts

### Cover (page i)

> NOT MEASUREMENT SENSITIVE
>
> MIL-HDBK-61B w/CHANGE 1 15 August 2025
>
> SUPERSEDING MIL-HDBK-61B 7 April 2020
>
> DEPARTMENT OF DEFENSE HANDBOOK
>
> CONFIGURATION MANAGEMENT GUIDANCE
>
> This handbook is for guidance only. Do not cite this document as a requirement.

### ¶ 1.1.2 CM functions (pages 1–2)

> 1.1.2 CM functions. The CM process is comprised of five CM functions and the underlying CM principles that together provide a flexible implementation structure. The CM process provides consistency among the various elements of product configuration information. The five CM functions are:
>
> a. Configuration Management and Planning
>
> b. Configuration Identification
>
> c. Configuration Control/Change Management
>
> d. Configuration Status Accounting
>
> e. Configuration Verification and Audit

### § 3.3 Definitions, selected entries (pages 6–11)

> 3.3 Definitions. Definitions for CM terms used in this standard are consistent with Government terminology found in Defense Acquisition University (DAU) and SAE EIA-649-1.
>
> Allocated Baseline (ABL): Documentation that designates the CIs making up a system and then allocates the system function and performance requirements across the CIs. It includes all functional and interface characteristics that are allocated from those of a higher-level CI or from the system itself, derived requirements, interface requirements with other CIs, design restraints, and the verification required to demonstrate the achievement of specified functional and interface characteristics. The performance of each CI in the ABL is described in its item performance specification.
>
> […]
>
> Configuration Baseline (Baseline): a. An agreed-to description of the attributes of a product, at a point in time, which serves as a basis for defining change. b. An approved and released document, or a set of documents, each of a specific revision; the purpose of which is to provide a defined basis for managing change. c. The currently approved and released configuration documentation. d. A released set of files comprising a software version and associated configuration documentation. See also: Allocated Baseline (ABL), Functional Baseline (FBL), and Product Baseline (PBL).
>
> […]
>
> Configuration Status Accounting (CSA): The CM function that formalizes the recording and reporting of the established product configuration information (including historical information), the status of proposed changes, and the implementation of approved changes and changes occurring to product units due to operation and maintenance. CSA implementation includes assurances that the information is current, accurate, and retrievable.
>
> […]
>
> Functional Baseline (FBL): The approved functional requirements for a product or system describing the functional, performance, interoperability, interface, and verification requirements established at a specific point in time and documented in the functional configuration documentation.
>
> […]
>
> Functional Configuration Audit (FCA): The formal examination of functional characteristics of a CI or system to verify that the item has achieved the requirements specified in its FCD or ACD.
>
> […]
>
> Physical Configuration Audit (PCA): The physical examination is the actual configuration of the item being produced. It verifies that the related design documentation matches the item as specified in the contract. The system product baseline is finalized and validated at the PCA.
>
> Product Baseline (PBL): Documentation describing all of the necessary functional and physical characteristics of the CI, the selected functional and physical characteristics designated for production acceptance testing, and tests necessary for deployment/installation, operation, support, training, and disposal of the CI. The initial PBL is usually established and put under configuration control at each CI's critical design review (CDR), culminating in an initial PBL at the system-level CDR. The system PBL is finalized and validated at the PCA.

The PCA entry's first sentence is as printed. Per § 3.2, FCD is Functional Configuration Documentation and ACD is Allocated Configuration Documentation.

### ¶ 5.5.2 Major configuration baselines (page 28)

> 5.5.2 Major configuration baselines. Major configuration baselines known as the FBL, ABL, and PBLs, as well as the developmental configuration, are associated with milestones in the life cycle of a CI. Each of these major configuration baselines is designated when the given level of the CI's configuration documentation is deemed to be complete and correct and needs to be formally protected from unwarranted and uncontrolled change from that point forward in its life cycle. […]
>
> a. FBL: The approved configuration documentation describing a system's top-level CI's performance (functional, inter-operability, and interface characteristics) and the verification required to demonstrate the achievement of those specified characteristics.
>
> b. ABL: The current approved performance-oriented documentation for a CI to be developed which describes the functional and interface characteristics that are allocated from those of the higher-level CI and the verification required to demonstrate achievement of those specified characteristics.
>
> c. PBL: When used for re-procurement of a CI, the PBL documentation also includes the documentation describing the ABL (e.g., performance specifications, development specifications) to ensure that performance requirements are not compromised.
>
> […]
>
> 5.5.2.1 Incremental baselines. Each configuration baseline serves as a point of departure for future CI changes. The current approved configuration documentation constitutes the current configuration baseline. Incremental configuration baselines occur sequentially over the life cycle of a CI as each new change is approved. Each change from the previous baseline to the current baseline occurs through a configuration control process. The audit trail of the configuration control activity from the CI's original requirements documentation to the current baseline is maintained as part of CSA.

### § 7 Configuration status accounting (pages 38–40)

> 7.1 CSA activity. CSA is the process of creating and organizing the knowledge base necessary for the performance of CM. In addition to facilitating CM, the purpose of CSA is to provide a highly reliable source of configuration information to support all program/project activities including program management, systems engineering, manufacturing, software development and maintenance, logistic support, modification, and maintenance.

Figure 8, "Configuration status accounting tasks" (page 40). The task list is transcribed from the figure; the figure's numbered bullets are rendered (1)–(8).

> (1) Record the current approved configuration documentation and configuration identifiers associated with each System/CI(s).
>
> (2) Record and report the status of proposed engineering changes from initiation to final approval to contractual implementation
>
> (3) Record and report the status of all critical and major requests for deviation which affect the configuration of a system/CI(s).
>
> (4) Record and report the results of configuration audits to include the status and final disposition of identified discrepancies and action items
>
> (5) Record and report implementation status of authorized changes
>
> (6) Provide the traceability of all changes from the original released configuration documentation of each System/CI(s)
>
> (7) Report the effectivity and installation status of configuration changes to all system/CI(s) at all locations, including design, production, modification, retrofit and maintenance changes
>
> (8) Record the digital data file(s)identifiers and document representations of all revisions/versions of each document and software which has been delivered, or made accessible electronically, in support of the contract.

### § 8 Configuration verification and audit (pages 43–46)

> 8.1.2 Configuration verification and audit activity completion. Successful completion of verification and audit activities results in a verified system/CI(s) and a documentation set that may be confidently considered a PBL. It also results in a validated process to maintain the continuing consistency of product to documentation.
>
> […]
>
> 8.2.2.2 FCA. The FCA is used to verify that the actual performance of the CI meets the requirements stated in its performance specification. […]
>
> 8.2.2.3 PCA. The PCA is used to examine the actual configuration of the CI that is representative of the product configuration in order to verify that the related design documentation matches the design of the deliverable CI. It is also used to validate many of the supporting processes that the contractor uses in the production of the CI. […]
>
> 8.2.2.5 Auditing in the performance-based acquisition environment. As discussed above, configuration audits address two major concerns:
>
> a. The ability of the developed design to meet the specified performance requirements. The FCA addresses this concern.
>
> b. The accuracy of the documentation reflecting the production design. This PCA addresses this concern.

## Claims checked

| Claim (from the record) | Verdict | Where in the text |
| --- | --- | --- |
| The current revision is MIL-HDBK-61B (record: "e.g. 61B — confirm"). | VERIFIED | ASSIST QuickSearch lists the document as Active, current issue "Revision B Change 1 (change incorporated)", 15-AUG-2025. The cover reads "MIL-HDBK-61B w/CHANGE 1 15 August 2025 SUPERSEDING MIL-HDBK-61B 7 April 2020". Cite it as MIL-HDBK-61B w/Change 1. |
| The handbook defines functional configuration audit (FCA). | VERIFIED | § 3.3, "Functional Configuration Audit (FCA)"; ¶ 8.2.2.2. |
| The handbook defines physical configuration audit (PCA). | VERIFIED | § 3.3, "Physical Configuration Audit (PCA)"; ¶ 8.2.2.3. |
| The handbook describes configuration status accounting (CSA). | VERIFIED | § 3.3, "Configuration Status Accounting (CSA)"; § 7 (¶ 7.1 and Figure 8); ¶ 1.1.2 d lists CSA as one of the five CM functions. |
| The handbook describes functional, allocated and product baselines. | VERIFIED | § 3.3 (Functional Baseline, Allocated Baseline, Product Baseline, Configuration Baseline); ¶ 5.5.2 a–c. |
| Mapping premise for the ledger as CSA: CSA is the recorded, retrievable history of a configuration and of every change to it. | VERIFIED | § 3.3 CSA, "recording and reporting of the established product configuration information (including historical information)" and "current, accurate, and retrievable"; ¶ 5.5.2.1, the audit trail "is maintained as part of CSA"; Figure 8, task (6). The text verifies the premise; the analogy is the record's. |
| Mapping premise for closeout as FCA/PCA: before a baseline is accepted, an FCA checks achieved performance against requirements and a PCA checks documentation against the item as built. | VERIFIED | ¶ 8.2.2.5 a–b; ¶ 8.1.2, "a documentation set that may be confidently considered a PBL"; § 3.3 PCA, "The system product baseline is finalized and validated at the PCA." The text verifies the premise; the analogy is the record's. |
