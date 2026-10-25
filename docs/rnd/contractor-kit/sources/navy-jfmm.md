# COMUSFLTFORCOMINST 4790.3, Joint Fleet Maintenance Manual (JFMM): retrieval record

- Document sought: COMUSFLTFORCOMINST 4790.3, *Joint Fleet Maintenance Manual*, current edition **Revision D Change 5, promulgation letter dated 13 June 2025** (edition named in search-index snippets of the NAVSEA SUBMEPP JFMM page; that page itself could not be read, see below).
- Retrieval date: 2026-10-25.
- **Result: the current JFMM (Rev D Chg 5) was NOT retrieved.** Its definitions of Ship's Force, Repair Activity, Naval Supervising Activity, Work Authorization Form / work control, Quality Assurance, Controlled Work Package (CWP), Formal Work Package (FWP), test and inspection, departure from specification, re-entry control and objective quality evidence (OQE) were **not read** in this run.
- What WAS read: a **secondary-host, superseded** HTML extract of the original JFMM (five volumes, pre-Revision A, c. 2000–2002) hosted by the Federation of American Scientists. Verbatim passages from it follow under § Secondary source. They are the original JFMM's words, not current canon; several terms changed since (for example the current manual uses "Naval Supervising Activity" and "Repair Activity" where this extract says "Supervising Authority" and "Industrial Activity" / "Fleet Maintenance Activity").

## Refusals (recorded, not worked around)

| URL | What it is | Result on 2026-10-25 |
|---|---|---|
| https://www.navsea.navy.mil/Home/SUBMEPP/Products/JFMM/ | NAVSEA SUBMEPP JFMM download page | HTTP 403 "Access Denied" (Akamai edgesuite), curl |
| https://www.navsea.navy.mil/Portals/103/Documents/SUBMEPP/JFMM/REV%20D%20CHG%205/Volume_V_D5.pdf | JFMM Rev D Chg 5, Volume V (Quality Maintenance); search snippets show its contents list with "2.2.3" Formal Work Package and "2.2.4 Controlled Work Package ... V-I-2-5" | HTTP 403 "Access Denied" (curl and WebFetch) |
| https://www.navsea.navy.mil/Portals/103/Documents/SUBMEPP/JFMM/REV%20D%20CHG%205/Volume_III_D5.pdf, .../Volume_IV_D5.pdf, .../Volume_Foreword_D5.pdf, .../00_JFMM.pdf | other Rev D Chg 5 volumes | Same host and path family; not separately fetched after the host returned 403 on every navsea.navy.mil URL tried |

## Secondary source: original JFMM extract (superseded edition, secondary host)

- Host: Federation of American Scientists, https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/index.html (HTTP 200). **Secondary host; not an official Navy copy.** The index page states: "These extracts cover primarily nuclear submarine activities. The full text is online @ Joint Fleet Maintenance Manual" (linking http://www.spear.navy.mil/JFMM/). Server `last-modified` of FORWARD.htm: Wed, 02 Sep 2026 19:17:51 GMT (a hosting timestamp, not an edition date).
- Edition: **not stated on the pages read.** The Foreword describes "five distinct volumes" with "Volume V - Quality Maintenance (formerly Quality Assurance)", cancels the separate TYCOM maintenance and QA manuals, and cites "CINCLANTFLT OPORD 2000" and "CINCLANTFLT/CINCPACFLTINST 4355.1", which places it as the original JFMM of about 2000–2002. Volume V is not in the extract.
- Verbatim handling: HTML tags stripped and whitespace runs collapsed; no words added, removed or reordered. In the glossaries the source HTML runs the two-column table (TERM / DEFINITION) together in single paragraphs, so where a term spans several table rows its words are interleaved with the definition in the source itself. Those rows are quoted exactly as the source has them, followed by a bracketed reading that separates term from definition; the bracketed reading is the only editorial text.

### Foreword, ¶ 2 and ¶ 5.2 (https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/FORWARD.htm)

> 2 VOLUME TOPICS. The Joint Fleet Maintenance Manual is made up of five distinct volumes.
> Volume I - New Construction
> Volume II - Integrated Fleet Maintenance
> Volume III - Deployed Maintenance
> Volume IV - Tests, Inspections and Special Application Maintenance Programs
> Volume V - Quality Maintenance (formerly Quality Assurance)

> 5.2 Maintenance Considerations. In the development of this manual, considerable effort was put forth to standardize work practices, incorporate accepted Regional Maintenance philosophies, and make allowances for future changes resulting from new Regional Maintenance policies. With respect to this, the term Intermediate Maintenance Activity (IMA) has been replaced by Fleet Maintenance Activity (FMA) to reflect the fact that under Regional Maintenance the responsibility for, and the management of, repair facilities has moved to the Fleet.

### Volume I, Chapter 1, Appendix D, Glossary of Terms (https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/vol1/CH_01.htm)

> Dock Trial Dock Trials are those ship trials conducted at the Industrial Activity to determine the ability of the ship, from a material standpoint, to conduct Sea Trials safely.

> Fast Cruise A period immediately prior to underway trials during which Ship's Force operates the ship for dockside training. Fast Cruise shall, as far as is practical, simulate at-sea operating conditions.

> Industrial Activity The activity responsible for accomplishing construction or repair of ships whether private or public. This includes Naval shipyards, private shipyards, shipbuilders, vendors, Naval Aviation Depots, Naval Ship Repair Facilities, and other Naval Repair/Technical Activities (i.e., Naval Underwater Weapons Center, Naval Ships Weapons Center, etc.).

> Supervising Authority The officer designated by NAVSEA to represent the Navy Department at an industrial activity; normally a Supervisor of Shipbuilding, Conversion and Repair or the Commander of a Naval Shipyard.

> Delivery The date the Navy accepts the ship from the shipbuilder. This requires a recommendation from the INSURV Board to accept/deliver the ship. Delivery of the ship is based on Acceptance Trials and satisfactory correction or resolution of deficiencies.

> Post Shakedown An industrial activity availability following Final Contract Trials/Guarantee
> Availability (PSA) Material Inspection assigned to correct deficiencies found during the shakedown period or to accomplish other authorized improvements.

[Reading: term "Post Shakedown Availability (PSA)"; definition "An industrial activity availability following Final Contract Trials/Guarantee Material Inspection assigned to correct deficiencies found during the shakedown period or to accomplish other authorized improvements."]

### Volume II, Chapter 1, Appendix B, Glossary of Terms (https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/vol2/CH_01.htm)

> Dock Trials Dock Trials are those ship trials conducted at the industrial activity to determine the ability of the ship, from a material standpoint, to conduct Sea Trials safely.

> Fleet Maintenance Activity Fleet Maintenance Activity, includes tenders, shore based maintenance activities (Shore Intermediate Maintenance Activities, Naval Ship Repair Facility, Submarine Base Repair Department, TRIDENT Refit Facilities, Weapons Repair Facilities) and supporting activities (port services, etc.). Regional Repair Centers (RRC) and Regional Maintenance Teams (RMT) are treated as Fleet Maintenance Activities. RRCs and RMTs are funded by the Fleet.

> Major Chief of Naval An availability of six months or greater duration performed by industrial activities Operations (CNO) under NAVSEA management or contract administration or as designated by the Maintenance Availability Type Commander or NAVSEA.

[Reading: term "Major Chief of Naval Operations (CNO) Maintenance Availability"; definition "An availability of six months or greater duration performed by industrial activities under NAVSEA management or contract administration or as designated by the Type Commander or NAVSEA."]

> Minor CNO MaintenanceAn availability of less than six months in duration scheduled by and under Type Availability Commander management.

[Reading: term "Minor CNO Maintenance Availability"; definition "An availability of less than six months in duration scheduled by and under Type Commander management."]

> Refurbishment Level The actions taken to return a component to "A" condition (like-new condition).
> Maintenance Normally done under rotatable pool (Advanced Equipment Repair Program, TRIDENT Planned Equipment Replacement, etc.) programs by Designated Overhaul Points. Designated Overhaul Points must be certified to have the industrial capability to meet the program requirements for performing quality work and have the capacity to meet established Refurbishment Turnaround Times.

[Reading: term "Refurbishment Level Maintenance".]

> Restoration Level The minimum planned inspection, maintenance and testing criteria to be applied
> Maintenance to ensure a component will function satisfactorily until the next planned accomplishment of the maintenance requirement.

[Reading: term "Restoration Level Maintenance"; definition "The minimum planned inspection, maintenance and testing criteria to be applied to ensure a component will function satisfactorily until the next planned accomplishment of the maintenance requirement."]

> Supervising AuthorityThe officer designated by NAVSEA to represent the Navy Department at an industrial activity; normally a Supervisor of Shipbuilding, Conversion and Repair or the Commander of a Naval Shipyard.

### Volume II, Chapter 3, CNO scheduled maintenance availabilities (https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/vol2/CH_03.htm)

> 3.4.3.1 Availability Work Package Content. The AWP includes all nuclear and non-nuclear authorized industrial work and associated Forces Afloat work for modernization, maintenance and repair during the availability. The work described is developed from NAVSEA and TYCOM instructions.

> 3.4.3.3 Availability Work Package Development. The five stages of AWP development include Baseline, Preliminary, Proposed, Approved, and Completed.

> a. Develop a Ship's Force concurrent Work Package that includes all major maintenance actions such as Planned Maintenance System (PMS), Reactor Plant PMS, repairs, PMRs, alterations, and testing to be conducted by Ship's Force during the availability, as applicable.

(from ¶ 3.4.2.1 Forces Afloat Work Package Preparations)

> k. Conduct a QA audit of Ship's Force and FMA Controlled Work Packages in accordance with Volume V, Part II, Chapter 8 of this manual.

(from ¶ 3.3.6 Responsibilities; the term "Controlled Work Packages" is used here but defined in Volume V, which the extract does not contain)

> l. (Submarines Only). Prior to Fast Cruise, the ISIC QA Officer shall conduct a formal audit of Ship's Force Re-Entry Control and Departure from Specification Records. [...]

(from ¶ 3.6.1 Responsibilities; "Re-Entry Control" and "Departure from Specification" are used, not defined, here)

> 3.6.8.3.7 Dock Trials. Dock Trials must, as a minimum, test those equipments/systems repaired or altered during the availability. The CO should use Appendix U of this chapter as a guide in preparing the Dock Trial Agenda.

> 3.6.8.3.8 Fast Cruise. Fast Cruise may commence immediately upon completion of Dock Trials and shall consist of at least 24 hours of uninterrupted operations. The requirement for a Fast Cruise longer than 24 hours will vary depending upon the length of the availability and the time since the crew last operated the ship at sea. Prior to the ship commencing Fast Cruise, the Supervising Authority shall report to the ship, by message, that all mandatory work approved for accomplishment during the availability is completed. When the ship is ready for sea with the exception of conducting Fast Cruise and after receipt of the SUBSAFE material certification report from the performing activity as required by references (u), (w) and Volume V of this manual, the ship will request permission from the ISIC by priority message to commence Fast Cruise. The ISIC will then, if satisfied with the state of crew training and material readiness, authorize the ship to commence Fast Cruise by message, information copy to CNO, FLTCINC, NAVSEA, and the TYCOM.

> 3.6.8.3.9 Sea Trials. Upon receipt of the report of successful completion of Fast Cruise from the ship, the ISIC authorizes the ship to get underway for Sea Trials. Sea Trials are required only as necessary to test work completed during the availability but must include those mandatory requirements identified in Appendix W of this chapter. The industrial activity shall include at least two days in the availability for conduct of Sea Trials. The industrial activity shall prepare a Sea Trial Agenda for Sea Trials conducted after an availability at the industrial activity. For an availability at a FMA, the submarine shall prepare the Sea Trial Agenda, assisted by the industrial activity. The submarine involved shall submit the Sea Trial Agenda to the ISIC for approval, with an information copy to the TYCOM. Extensions or reductions of the Sea Trial period may be granted where warranted by the scope of the work accomplished. Where extension of the Sea Trial period and a change in the availability schedule is required, requests for such extensions must be submitted by the industrial activity to the TYCOM as early as practical. All deficiencies resulting from Sea Trials will be satisfactorily resolved prior to the completion of the availability. If no Sea Trial deficiencies are found, the availability may be completed with TYCOM occurrence at the completion of Sea Trials.

### Volume I, Chapter 3, ¶ 3.3.12 In-Service division of responsibility (https://nuke.fas.org/guide/usa/doctrine/navy/jfmm/vol1/CH_03.htm)

> (1) Ship's Force. At In-Service, Ship's Force must have operational control of all systems in the ship and will stand all shipboard watches, making all security patrols of the ship, the moorings, and the immediate adjacent pier.

> (2) Industrial Activity. The industrial activity continues to perform all contract requirements until delivery. The industrial activity will support Ship's Force in the performance of those requirements assumed by Ship's Force as required.

> (3) Supervising Authority. During preparations for In-Service, conduct liaison between Ship's Force and the industrial activity to ensure that the above division of responsibility is understood and agreed to. Verify that a schedule of compartment/space and system turnover is prepared, mutually agreed to, and that a means to identify deficiencies in systems and spaces turned over to Ship's Force is executed.

## Not found in the extract

No definition of Ship's Force, Repair Activity, Naval Supervising Activity, Work Authorization Form, Quality Assurance, Controlled Work Package, Formal Work Package, test and inspection, departure from specification, re-entry control, or objective quality evidence appears in the pages read (Foreword; Vol I Ch 1–3; Vol II Ch 1, 3; Vol III Ch 1–2). Those terms are defined in the Volume V (Quality Maintenance) text, which the FAS extract omits and NAVSEA refused.
