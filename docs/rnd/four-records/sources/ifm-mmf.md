# Incremental Funding Method: MMF, AE, precedence (Denne and Cleland-Huang)

Access date for every source: 2026-10-30.

## Retrieval status of the primary texts

- Denne, M. and Cleland-Huang, J. (2004). "The incremental funding method: data-driven software development." *IEEE Software* 21(3), 39–47. DOI 10.1109/MS.2004.1293071. Crossref metadata confirmed (`https://api.crossref.org/works/10.1109/MS.2004.1293071`: title, volume 21, issue 3, pages 39-47; no abstract deposited). **Full text not read**: behind the IEEE paywall; no open copy found. Not a refusal of automated retrieval; simply not openly available.
- Denne, M. and Cleland-Huang, J. (2004). *Software by Numbers: Low-Risk, High-Return Development.* Prentice Hall PTR. ISBN 0-13-140728-7. **Full text not read** (commercial book). The publisher's table of contents was read (below).
- Cleland-Huang, J. and Denne, M. (2005). "Financially informed requirements prioritization." ICSE 2005, 710–711. DOI 10.1145/1062455.1062630. **Not read** (no open copy found).

Because the primary texts were not available, the definitional quotations below come from **secondary** sources, marked as such.

## Publisher's table of contents (publisher listing; primary as to the book's structure only)

Source: https://www.informit.com/store/software-by-numbers-low-risk-high-return-development-9780131407282. Publisher (Pearson/InformIT) listing.

> 3. Identifying and Valuing Marketable Features. Incremental Funding Methodology. Minimum Marketable Features. Candidate MMFs. Determining the Value of an MMF. Development and Delivery Precursors. The MMF Precedence Graph. Architectural Precursors. Summary. References.

> 4. Incremental Architecture. The Place of Architecture. Architecture versus Rules. The Problem with Architecture. Pieces of the Pattern. A Value-Driven Approach. The Codependency of Architecture. Taking Architecture in Easy Stages. A Different Decomposition. One-to-Many Dependencies in Architecture. Architectural Coherency. Multiple Inheritance in Architecture. Spiral Architecture. Summary. References.

> 5. IFM Sequencing Strategies. Delivering Valued Features. Cost versus Value Analysis. Cost-Benefit Analysis of an MMF Delivery Sequence. The Complexity of the Task. MMF Sequencing Strategies. The Greedy Approach. A Simple Look-Ahead Approach. The Weighted Look-Ahead Approach. Sequencing MMFs and AEs. Risk Mitigation. Iterating the Sequencing Decision. Summary. References.

> 7. Managing Intangibles. [...] Hybrid MMFs. [...]

> 9. IFM and Agile Development. The Challenges. Incremental Development the Agile Way. Clustering User Stories into MMFs. Release Planning: Bundling User Stories in Releases. Assessing the NPV of the Release Plan. Release Planning Meeting. The Architecture Question. Simplest versus Look-Ahead Solution. Other Agile Development Environments. SCRUM. Summary. References.

Same page, publisher description:

> This book introduces the Incremental Funding Methodology (IFM), an ROI-informed approach to software development in which software is developed and delivered in carefully prioritized chunks of customer valued functionality.

## MMF and AE definitions (secondary)

Source: Alencar, A. J., Schmitz, E. A., de Abreu, Ê. P., Fernandes, M. C., Ferreira, A. L. (2008). "Maximizing the Business Value of Software Projects: A Branch & Bound Approach." ICEIS 2008, 162–169. DOI 10.5220/0001685801620169. https://www.scitepress.org/Papers/2008/16858/16858.pdf. **Secondary** (cites Denne and Cleland-Huang 2004a, 2004b).

> The IFM groups requirements into self-contained interdependent software units that create value to business in one or several of the following areas:
> • Competitive Differentiation - the software unit allows the creation of service or product features that are valued by customers and that are different from anything else being offered in the market;
> • Revenue Generation - although the software unit does not provide any unique valuable features to customers, it does provide extra revenue by offering the same quality as other products in the market for a better price;
> • Cost Savings - the software unit allows business to save money by making one or more business processes cheaper to run;
> • Brand Projection - by building the software unit the business projects itself as being technologically advanced; and
> • Enhanced Customer Loyalty - the software unit influences customers to buy more, more frequently or both.

> The self-contained units in which the IFM partitions a software project are called Minimum Marketable Features, or MMF for short, indicating that they contain strongly-related software features that can be quickly delivered and that are valued by customers (Steindl, 2005; Denne and Cleland-Huang, 2004b).
>
> Although an MMF is a self-contained unit, it is often the case that an MMF can only be developed after other project parts have been completed. These project parts may be either other MMFs or the architectural infrastructure, i.e. the set of basic features that offers no direct value to customers, but that are required by the MMFs.
>
> The architecture itself can usually be decomposed into self-contained deliverable elements. These elements, called Architectural Elements or AEs for short, enables the architecture to be delivered according to demand, further reducing the initial investment needed to run a software project.

> After the MMFs and AEs have been identified, developers and business personnel collaborate to analyze for each MMFs and AEs their estimated cost and expected revenues over a window of opportunity.

> The development constraints between MMFs and AEs can be represented by a directed acyclic graph showing their precedence relationship.

> In formal terms a precedence graph of project units is a mathematical structure G(V, E) where:
> • V = {v1 , v2 , · · · , vn } is a set of MMFs and AEs, and
> • E is a set of ordered pairs, such that if (va , vb ) ∈ E, then vb depends on the completion of va .

Source: Poppendieck, M. (2004-02-20). "Incremental Funding." Lean Essays. https://www.leanessays.com/2004/02/incremental-funding.html. **Secondary** (book commentary).

> Software by Numbers recommends dividing a project into Minimum Marketable Features (MMF’s). These are small feature sets which deliver some identifiable value to the customer. Each MMF should have its own return on investment (ROI). By laying out the potential ROI’s of various feature sets, an optimal development sequence for the MMF’s can be determined.

> The book recommends that architectural elements which support each set of MMF’s should be developed with their respective MMF’s. In other words, architectural development should be sequenced using the same financially driven priorities as feature development. While there may be times where architectural coherency may dictate early development of features not immediately related to the current feature set, in general it is not only possible but also preferable to defer implementation of architectural elements until the features requiring these elements is being developed.

Source: JavaRanch Journal, Book Review of the Month (July 2004). https://javaranch.com/journal/200407/BookReviewOfTheMonth.html. **Secondary** (reader reviews).

> The authors describe an Incremental Funding Method (IFM) for scheduling incremental development of software which optimizes the Return on Investment (ROI) by having the requirements engineered into Minimum Marketable Features (MMF) with concrete, monetary value.

> They also describe the business case for incremental architecture and different strategies for sequencing MMFs and Architectural Elements (AE) for maximum ROI over the project's lifetime.

## Shape as stated

As reported by the secondary sources, IFM partitions a project into **Minimum Marketable Features (MMFs)**: self-contained units of "strongly-related software features" that return customer value when delivered and carry their own cost/revenue cash flow and ROI. Requirements are grouped ("engineered") into MMFs. Units that "offer no direct value to customers, but that are required by the MMFs" are **Architectural Elements (AEs)**, also self-contained and deliverable. MMFs and AEs are nodes of one **precedence graph** (a DAG; an edge means the later unit depends on completion of the earlier); an MMF may depend on other MMFs or on AEs. The method sequences MMFs and AEs to maximize NPV, and (per Poppendieck) prefers to deliver an AE together with the MMFs that need it rather than early. The book's table of contents also names "Development and Delivery Precursors", "Architectural Precursors", "Hybrid MMFs", "Clustering User Stories into MMFs" and "Release Planning: Bundling User Stories in Releases"; their text was not read. The relation between an MMF and a release (beyond the chapter title) is not established by the sources read.
