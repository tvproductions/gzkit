# 14 CFR §§ 91.405, 91.409, 91.417, 119.65, 121.363, 121.368, 121.375, 121.377, 121.380a (verbatim)

- Source (official, primary): Electronic Code of Federal Regulations (eCFR), National Archives / GPO.
- Human URLs: https://www.ecfr.gov/current/title-14/section-<section> for each section listed
- Retrieved via eCFR API: https://www.ecfr.gov/api/versioner/v1/full/2026-10-15/title-14.xml?part=<part>&section=<section> for each section listed
- Retrieval date: 2026-10-26. eCFR Title 14 latest issue date (and latest amended on) 2026-10-15; eCFR states Title 14 up to date as of 2026-10-22 (from https://www.ecfr.gov/api/versioner/v1/titles.json).
- Scope of extract: each listed section in full with its amendment citation. Why each: 91.405 owner/operator maintenance duties, including repair or deferral of inoperative items and placarding under 91.213(d)(2); 91.409 inspections (annual, 100-hour, progressive, programs); 91.417 maintenance records; 119.65 management personnel required for Part 121 operations (Director of Maintenance, Chief Inspector); 121.363 responsibility for airworthiness; 121.368 contract maintenance; 121.375 maintenance and preventive maintenance training program; 121.377 maintenance and preventive maintenance personnel duty time limitations; 121.380a transfer of maintenance records.
- Not captured: Part 135 counterparts (e.g. §§ 135.411–135.443), § 119.67 (qualifications for the § 119.65 positions), and § 121.373 / § 121.374 (in `docs/rnd/renewing-vows/sources/us-gov-14cfr-121-subpart-L.md` only in part).

Verbatim-handling note: text converted mechanically from the eCFR XML returned by the API URL above (Python `xml.etree` `itertext()`); runs of whitespace collapsed to single spaces, subpart headings rendered as `##`, section and appendix headings as `###`, amendment citations rendered in italics, authority/source notes in bold. No words were added, removed, paraphrased or reordered within the extracted sections. Inline italics inside paragraphs (`<I>`) are not reproduced as italics. The API requires `Accept-Encoding` compression (it returns HTTP 406 otherwise); the request was sent with `curl --compressed`, which is a protocol requirement, not a workaround.

---

### § 91.405 Maintenance required.

Each owner or operator of an aircraft—

(a) Shall have that aircraft inspected as prescribed in subpart E of this part and shall between required inspections, except as provided in paragraph (c) of this section, have discrepancies repaired as prescribed in part 43 of this chapter;

(b) Shall ensure that maintenance personnel make appropriate entries in the aircraft maintenance records indicating the aircraft has been approved for return to service;

(c) Shall have any inoperative instrument or item of equipment, permitted to be inoperative by § 91.213(d)(2) of this part, repaired, replaced, removed, or inspected at the next required inspection; and

(d) When listed discrepancies include inoperative instruments or equipment, shall ensure that a placard has been installed as required by § 43.11 of this chapter.

### § 91.409 Inspections.

(a) Except as provided in paragraph (c) of this section, no person may operate an aircraft unless, within the preceding 12 calendar months, it has had—

(1) An annual inspection in accordance with part 43 of this chapter and has been approved for return to service by a person authorized by § 43.7 of this chapter; or

(2) An inspection for the issuance of an airworthiness certificate in accordance with part 21 of this chapter.

No inspection performed under paragraph (b) of this section may be substituted for any inspection required by this paragraph unless it is performed by a person authorized to perform annual inspections and is entered as an “annual” inspection in the required maintenance records.

(b) Except as provided in paragraph (c) of this section, no person may operate an aircraft carrying any person (other than a crewmember) for hire, and no person may give flight instruction for hire in an aircraft which that person provides, unless within the preceding 100 hours of time in service the aircraft has received an annual or 100-hour inspection and been approved for return to service in accordance with part 43 of this chapter or has received an inspection for the issuance of an airworthiness certificate in accordance with part 21 of this chapter. The 100-hour limitation may be exceeded by not more than 10 hours while en route to reach a place where the inspection can be done. The excess time used to reach a place where the inspection can be done must be included in computing the next 100 hours of time in service.

(c) Paragraphs (a) and (b) of this section do not apply to—

(1) An aircraft that carries a special flight permit, a current experimental airworthiness certificate, a special airworthiness certificate in the light-sport category, or provisional airworthiness certificate;

(2) An aircraft inspected in accordance with an approved aircraft inspection program under part 125 or 135 of this chapter and so identified by the registration number in the operations specifications of the certificate holder having the approved inspection program;

(3) An aircraft subject to the requirements of paragraph (d) or (e) of this section; or

(4) Turbine-powered rotorcraft when the operator elects to inspect that rotorcraft in accordance with paragraph (e) of this section.

(d) Progressive inspection. Each registered owner or operator of an aircraft desiring to use a progressive inspection program must submit a written request to the responsible Flight Standards office, and shall provide—

(1) A certificated mechanic holding an inspection authorization, a certificated airframe repair station, or the manufacturer of the aircraft to supervise or conduct the progressive inspection;

(2) A current inspection procedures manual available and readily understandable to pilot and maintenance personnel containing, in detail—

(i) An explanation of the progressive inspection, including the continuity of inspection responsibility, the making of reports, and the keeping of records and technical reference material;

(ii) An inspection schedule, specifying the intervals in hours or days when routine and detailed inspections will be performed and including instructions for exceeding an inspection interval by not more than 10 hours while en route and for changing an inspection interval because of service experience;

(iii) Sample routine and detailed inspection forms and instructions for their use; and

(iv) Sample reports and records and instructions for their use;

(3) Enough housing and equipment for necessary disassembly and proper inspection of the aircraft; and

(4) Appropriate current technical information for the aircraft.

The frequency and detail of the progressive inspection shall provide for the complete inspection of the aircraft within each 12 calendar months and be consistent with the manufacturer's recommendations, field service experience, and the kind of operation in which the aircraft is engaged. The progressive inspection schedule must ensure that the aircraft, at all times, will be airworthy and will conform to all applicable FAA aircraft specifications, type certificate data sheets, airworthiness directives, and other approved data. If the progressive inspection is discontinued, the owner or operator shall immediately notify the responsible Flight Standards office, in writing, of the discontinuance. After the discontinuance, the first annual inspection under § 91.409(a)(1) is due within 12 calendar months after the last complete inspection of the aircraft under the progressive inspection. The 100-hour inspection under § 91.409(b) is due within 100 hours after that complete inspection. A complete inspection of the aircraft, for the purpose of determining when the annual and 100-hour inspections are due, requires a detailed inspection of the aircraft and all its components in accordance with the progressive inspection. A routine inspection of the aircraft and a detailed inspection of several components is not considered to be a complete inspection.

(e) Large airplanes (to which part 125 is not applicable), turbojet multiengine airplanes, turbopropeller-powered multiengine airplanes, and turbine-powered rotorcraft. No person may operate a large airplane, turbojet multiengine airplane, turbopropeller-powered multiengine airplane, or turbine-powered rotorcraft unless the replacement times for life-limited parts specified in the aircraft specifications, type data sheets, or other documents approved by the Administrator are complied with and the airplane or turbine-powered rotorcraft, including the airframe, engines, propellers, rotors, appliances, survival equipment, and emergency equipment, is inspected in accordance with an inspection program selected under the provisions of paragraph (f) of this section, except that, the owner or operator of a turbine-powered rotorcraft may elect to use the inspection provisions of § 91.409(a), (b), (c), or (d) in lieu of an inspection option of § 91.409(f).

(f) Selection of inspection program under paragraph (e) of this section. The registered owner or operator of each airplane or turbine-powered rotorcraft described in paragraph (e) of this section must select, identify in the aircraft maintenance records, and use one of the following programs for the inspection of the aircraft:

(1) A continuous airworthiness inspection program that is part of a continuous airworthiness maintenance program currently in use by a person holding an air carrier operating certificate or an operating certificate issued under part 121 or 135 of this chapter and operating that make and model aircraft under part 121 of this chapter or operating that make and model under part 135 of this chapter and maintaining it under § 135.411(a)(2) of this chapter.

(2) An approved aircraft inspection program approved under § 135.419 of this chapter and currently in use by a person holding an operating certificate issued under part 135 of this chapter.

(3) A current inspection program recommended by the manufacturer.

(4) Any other inspection program established by the registered owner or operator of that airplane or turbine-powered rotorcraft and approved by the Administrator under paragraph (g) of this section. However, the Administrator may require revision of this inspection program in accordance with the provisions of § 91.415.

Each operator shall include in the selected program the name and address of the person responsible for scheduling the inspections required by the program and make a copy of that program available to the person performing inspections on the aircraft and, upon request, to the Administrator.

(g) Inspection program approved under paragraph (e) of this section. Each operator of an airplane or turbine-powered rotorcraft desiring to establish or change an approved inspection program under paragraph (f)(4) of this section must submit the program for approval to the responsible Flight Standards office. The program must be in writing and include at least the following information:

(1) Instructions and procedures for the conduct of inspections for the particular make and model airplane or turbine-powered rotorcraft, including necessary tests and checks. The instructions and procedures must set forth in detail the parts and areas of the airframe, engines, propellers, rotors, and appliances, including survival and emergency equipment required to be inspected.

(2) A schedule for performing the inspections that must be performed under the program expressed in terms of the time in service, calendar time, number of system operations, or any combination of these.

(h) Changes from one inspection program to another. When an operator changes from one inspection program under paragraph (f) of this section to another, the time in service, calendar times, or cycles of operation accumulated under the previous program must be applied in determining inspection due times under the new program.

(Approved by the Office of Management and Budget under control number 2120-0005)

*[Docket 18334, 54 FR 34311, Aug. 18, 1989; Amdt. 91-211, 54 FR 41211, Oct. 5, 1989; Amdt. 91-267, 66 FR 21066, Apr. 27, 2001; Amdt. 91-282, 69 FR 44882, July 27, 2004; Docket FAA-2018-0119, Amdt. 91-350, 83 FR 9171, Mar. 5, 2018; Docket FAA-2023-1377, Amdt. 91-381, 90 FR 35222, July 24, 2025]*

### § 91.417 Maintenance records.

(a) Except for work performed in accordance with §§ 91.411 and 91.413, each registered owner or operator shall keep the following records for the periods specified in paragraph (b) of this section:

(1) Records of the maintenance, preventive maintenance, and alteration and records of the 100-hour, annual, progressive, and other required or approved inspections, as appropriate, for each aircraft (including the airframe) and each engine, propeller, rotor, and appliance of an aircraft. The records must include—

(i) A description (or reference to data acceptable to the Administrator) of the work performed; and

(ii) The date of completion of the work performed; and

(iii) The signature, and certificate number of the person approving the aircraft for return to service.

(2) Records containing the following information:

(i) The total time in service of the airframe, each engine, each propeller, and each rotor.

(ii) The current status of life-limited parts of each airframe, engine, propeller, rotor, and appliance.

(iii) The time since last overhaul of all items installed on the aircraft which are required to be overhauled on a specified time basis.

(iv) The current inspection status of the aircraft, including the time since the last inspection required by the inspection program under which the aircraft and its appliances are maintained.

(v) The current status of applicable airworthiness directives (AD) including, for each, the method of compliance, the AD number and revision date. If the AD involves recurring action, the time and date when the next action is required.

(vi) Copies of the forms prescribed by § 43.9(d) of this chapter for each major alteration to the airframe and currently installed engines, rotors, propellers, and appliances.

(b) The owner or operator shall retain the following records for the periods prescribed:

(1) The records specified in paragraph (a)(1) of this section shall be retained until the work is repeated or superseded by other work or for 1 year after the work is performed.

(2) The records specified in paragraph (a)(2) of this section shall be retained and transferred with the aircraft at the time the aircraft is sold.

(3) A list of defects furnished to a registered owner or operator under § 43.11 of this chapter shall be retained until the defects are repaired and the aircraft is approved for return to service.

(c) The owner or operator shall make all maintenance records required to be kept by this section available for inspection by the Administrator or any authorized representative of the National Transportation Safety Board (NTSB). In addition, the owner or operator shall present Form 337 described in paragraph (d) of this section for inspection upon request of any law enforcement officer.

(d) When a fuel tank is installed within the passenger compartment or a baggage compartment pursuant to part 43 of this chapter, a copy of FAA Form 337 shall be kept on board the modified aircraft by the owner or operator.

(Approved by the Office of Management and Budget under control number 2120-0005)

*[Docket 18334, 54 FR 34311, Aug. 18, 1989, as amended by Amdt. 91-311, 75 FR 5223, Feb. 1, 2010; Amdt. 91-323, 76 FR 39260, July 6, 2011; Docket FAA-2023-1377, Amdt. 91-381, 90 FR 35222, July 24, 2025]*

### § 119.65 Management personnel required for operations conducted under part 121 of this chapter.

(a) Each certificate holder must have sufficient qualified management and technical personnel to ensure the highest degree of safety in its operations. The certificate holder must have qualified personnel serving full-time in the following or equivalent positions:

(1) Director of Safety.

(2) Director of Operations.

(3) Chief Pilot for each category of aircraft the certificate holder uses, as listed in § 61.5(b)(1) of this chapter.

(4) Director of Maintenance.

(5) Chief Inspector.

(b) The Administrator may approve positions or numbers of positions other than those listed in paragraph (a) of this section for a particular operation if the certificate holder shows that it can perform the operation with the highest degree of safety under the direction of fewer or different categories of management personnel due to—

(1) The kind of operation involved;

(2) The number and type of aircraft used; and

(3) The area of operations.

(c) The title of the positions required under paragraph (a) of this section or the title and number of equivalent positions approved under paragraph (b) of this section shall be set forth in the certificate holder's operations specifications.

(d) The individuals who serve in the positions required or approved under paragraph (a) or (b) of this section and anyone in a position to exercise control over operations conducted under the operating certificate must—

(1) Be qualified through training, experience, and expertise;

(2) To the extent of their responsibilities, have a full understanding of the following materials with respect to the certificate holder's operation—

(i) Aviation safety standards and safe operating practices;

(ii) 14 CFR Chapter I (Federal Aviation Regulations);

(iii) The certificate holder's operations specifications;

(iv) All appropriate maintenance and airworthiness requirements of this chapter (e.g., parts 1, 21, 23, 25, 43, 45, 47, 65, 91, and 121 of this chapter); and

(v) The manual required by § 121.133 of this chapter; and

(3) Discharge their duties to meet applicable legal requirements and to maintain safe operations.

(e) Each certificate holder must:

(1) State in the general policy provisions of the manual required by § 121.133 of this chapter, the duties, responsibilities, and authority of personnel required under paragraph (a) of this section;

(2) List in the manual the names and business addresses of the individuals assigned to those positions; and

(3) Notify the responsible Flight Standards office within 10 days of any change in personnel or any vacancy in any position listed.

*[Docket 28154, 60 FR 65913, Dec. 20, 1995, as amended by Docket FAA-2018-0119, Amdt. 119-19, 83 FR 9172, Mar. 5, 2018; Docket FAA-2022-1563, Amdt. 119-20, 88 FR 48089, July 26, 2023]*

### § 121.363 Responsibility for airworthiness.

(a) Each certificate holder is primarily responsible for—

(1) The airworthiness of its aircraft, including airframes, aircraft engines, propellers, appliances, and parts thereof; and

(2) The performance of the maintenance, preventive maintenance, and alteration of its aircraft, including airframes, aircraft engines, propellers, appliances, emergency equipment, and parts thereof, in accordance with its manual and the regulations of this chapter.

(b) A certificate holder may make arrangements with another person for the performance of any maintenance, preventive maintenance, or alterations. However, this does not relieve the certificate holder of the responsibility specified in paragraph (a) of this section.

*[Docket 6258, 29 FR 19210, Dec. 31, 1964, as amended by Amdt. 121-106, 38 FR 22378, Aug. 20, 1973]*

### § 121.368 Contract maintenance.

(a) A certificate holder may arrange with another person for the performance of maintenance, preventive maintenance, and alterations as authorized in § 121.379(a) only if the certificate holder has met all the requirements in this section. For purposes of this section—

(1) A maintenance provider is any person who performs maintenance, preventive maintenance, or an alteration for a certificate holder other than a person who is trained by and employed directly by that certificate holder.

(2) Covered work means any of the following:

(i) Essential maintenance that could result in a failure, malfunction, or defect endangering the safe operation of an aircraft if not performed properly or if improper parts or materials are used;

(ii) Regularly scheduled maintenance; or

(iii) A required inspection item on an aircraft.

(3) Directly in charge means having responsibility for covered work performed by a maintenance provider. A representative of the certificate holder directly in charge of covered work does not need to physically observe and direct each maintenance provider constantly, but must be available for consultation on matters requiring instruction or decision.

(b) Each certificate holder must be directly in charge of all covered work done for it by a maintenance provider.

(c) Each maintenance provider must perform all covered work in accordance with the certificate holder's maintenance manual.

(d) No maintenance provider may perform covered work unless that work is carried out under the supervision and control of the certificate holder.

(e) Each certificate holder who contracts for maintenance, preventive maintenance, or alterations must develop and implement policies, procedures, methods, and instructions for the accomplishment of all contracted maintenance, preventive maintenance, and alterations. These policies, procedures, methods, and instructions must provide for the maintenance, preventive maintenance, and alterations to be performed in accordance with the certificate holder's maintenance program and maintenance manual.

(f) Each certificate holder who contracts for maintenance, preventive maintenance, or alterations must ensure that its system for the continuing analysis and surveillance of the maintenance, preventive maintenance, and alterations carried out by the maintenance provider, as required by § 121.373(a), contains procedures for oversight of all contracted covered work.

(g) The policies, procedures, methods, and instructions required by paragraphs (e) and (f) of this section must be acceptable to the FAA and included in the certificate holder's maintenance manual as required by§ 121.369(b)(10).

(h) Each certificate holder who contracts for maintenance, preventive maintenance, or alterations must provide to its responsible Flight Standards office, in a format acceptable to the FAA, a list that includes the name and physical (street) address, or addresses, where the work is carried out for each maintenance provider that performs work for the certificate holder, and a description of the type of maintenance, preventive maintenance, or alteration that is to be performed at each location. The list must be updated with any changes, including additions or deletions, and the updated list provided to the FAA in a format acceptable to the FAA by the last day of each calendar month.

*[Docket FAA-2011-1136, Amdt. 121-371, 80 FR 11546, Mar. 4, 2015, as amended by Docket FAA-2018-0119, Amdt. 121-380, 83 FR 9173, Mar. 5, 2018]*

### § 121.375 Maintenance and preventive maintenance training program.

Each certificate holder or person performing maintenance or preventive maintenance functions for it shall have a training program to ensure that each person (including inspection personnel) who determines the adequacy of work done is fully informed about procedures and techniques and new equipment in use and is competent to perform his duties.

### § 121.377 Maintenance and preventive maintenance personnel duty time limitations.

Within the United States, each certificate holder (or person performing maintenance or preventive maintenance functions for it) shall relieve each person performing maintenance or preventive maintenance from duty for a period of at least 24 consecutive hours during any seven consecutive days, or the equivalent thereof within any one calendar month.

### § 121.380a Transfer of maintenance records.

Each certificate holder who sells a U.S. registered aircraft shall transfer to the purchaser, at the time of sale, the following records of that aircraft, in plain language form or in coded form at the election of the purchaser, if the coded form provides for the preservation and retrieval of information in a manner acceptable to the Administrator:

(a) The record specified in § 121.380(a)(2).

(b) The records specified in § 121.380(a)(1) which are not included in the records covered by paragraph (a) of this section, except that the purchaser may permit the seller to keep physical custody of such records. However, custody of records in the seller does not relieve the purchaser of his responsibility under § 121.380(c) to make the records available for inspection by the Administrator or any authorized representative of the National Transportation Safety Board (NTSB).

*[Docket 10658, 37 FR 15984, Aug. 9, 1972]*
