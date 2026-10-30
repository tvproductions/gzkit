# Release planning research: NRP, requirement interdependencies, EVOLVE, themes

Access date for every source: 2026-10-30.

## Retrieval status

| Work | Status |
| --- | --- |
| Bagnall, A. J., Rayward-Smith, V. J., Whittley, I. M. (2001). "The next release problem." *Information and Software Technology* 43(14), 883–890. DOI 10.1016/S0950-5849(01)00194-X | Full text **not read**: closed access (UEA repository: full text not available; Semantic Scholar: `CLOSED`). Abstract read from the UEA research portal (primary abstract). |
| Carlshamre, P., Sandahl, K., Lindvall, M., Regnell, B., Natt och Dag, J. (2001). "An industrial survey of requirements interdependencies in software product release planning." RE'01, 84–91. DOI 10.1109/ISRE.2001.948547 | **Not read**: closed access (Semantic Scholar: `CLOSED`; abstract elided by the publisher). Only secondary descriptions below. |
| Greer, D., Ruhe, G. (2004). "Software release planning: an evolutionary and iterative approach." *Information and Software Technology* 46(4), 243–253. DOI 10.1016/j.infsof.2003.07.002 | **Read** (author manuscript copy, 20 pp.) at https://wwwbroy.cs.tum.edu/lehre/vorlesungen/vse/WS2004/2004_Greer_Releases.pdf. Primary (author text; pagination differs from the journal). |
| Agarwal, N., Karimpour, R., Ruhe, G. (2014). "Theme-Based Product Release Planning: An Analytical Approach." HICSS 2014. DOI 10.1109/HICSS.2014.582 | **Refused**: Semantic Scholar lists a bronze open-access PDF at `https://ieeexplore.ieee.org/ielx7/6751593/6758592/06759184.pdf`; an automated GET returned HTTP 418 with an IEEE Xplore script page. Not worked around. Abstract elided in Crossref and Semantic Scholar. |
| Karim, M. R., Ruhe, G. (2014). "Bi-objective genetic search for release planning in support of themes." SSBSE 2014 (LNCS) | **Not read** (Springer; no open copy found). Only a secondary description below. |
| Ruhe, G., Saliu, M. O. (2005). "The art and science of software release planning." *IEEE Software* 22(6) | **Not read** (paywalled). |

## The Next Release Problem (Bagnall et al. 2001)

Source: https://research-portal.uea.ac.uk/en/publications/the-next-release-problem/ (abstract). Primary (authors' abstract).

> Companies developing and maintaining complex software systems need to determine the features that should be added to their system as part of the next release. They will wish to select these features to ensure the demands of their client base are satisfied as much as possible while at the same time ensuring that they themselves have the resources to undertake the necessary development. This situation is modelled in this paper and the problem of selecting an optimal next release is shown to be NP-hard. The use of various modern heuristics to find a high quality but possibly suboptimal solution is described. Comparative studies of these heuristics are given for various test cases.

Source: Chattopadhyay, A., Niu, N., Liu, H., Zhang, J. "Enhancing User-Feedback Driven Requirements Prioritization." arXiv:2603.28677v1. https://arxiv.org/html/2603.28677v1. **Secondary**.

> Bagnall et al. [3] were among the first to connect requirements prioritization with SBSE by defining the NRP, i.e., the problem of selecting an optimal set of requirements to be delivered in the software system’s next stable version. Here, optimality means satisfying the stakeholder demands as much as possible, and meanwhile ensuring that there are enough resources to undertake the necessary development.

> Bagnall et al. [3] defined the search objective to: Maximize ∑ x_i·value(r_i), subject to ∑ x_i·cost(r_i) ≤ B, where value(r_i) is the (weighted) sum of stakeholders’ values placed on r_i, cost(r_i) is the total resource estimates of implementing r_i, and B is some bound.

(The formula is transcribed from the HTML's MathML alt-text, with the duplicated LaTeX rendering removed.)

## Requirement interdependencies (Carlshamre et al. 2001), secondary only

Source: arXiv:2603.28677v1 (as above). **Secondary**.

> Carlshamre et al. [6] observed several relation types, such as “AND” and “requires”. The distinction is that “AND” suggests a requires-relation in both ways whereas “requires” indicates the relation in only one way. For example, a printer requires a driver to function, and the driver also requires the printer to function [6]. This is an instance of “AND” relation.
>
> In contrast, emailing a scanned document requires a network connection, but not the other way around [6]. Here, a “requires” relation exists between the pair of requirements.

Source: Mougouei, D., Powers, D. M. W. (2017). "Dependency-Aware Software Release Planning through Mining User Preferences." arXiv:1702.05592v1. https://arxiv.org/pdf/1702.05592. **Secondary**.

> Such influences have been described in the literature as value-related dependencies [8], [25], CVALUE dependencies [8], increases/decreases value of dependencies [10], [53], and positive/negative value dependencies [21].

> Value-related dependencies are known to be of the most common types of dependencies among features (requirements) of software projects [8].

(Reference [8] in that paper is Carlshamre et al. 2001.)

## EVOLVE (Greer and Ruhe 2004)

Source: Greer and Ruhe 2004, author manuscript (URL above). Primary.

Abstract:

> In adopting this process, requirements are delivered in releases and so a decision has to be made on which requirements should be delivered in which release. Three main considerations that need to be taken account of are the technical precedences inherent in the requirements, the typically conflicting priorities as determined by the representative stakeholders, as well as the balance between required and available effort. The technical precedence constraints relate to situations where one requirement cannot be implemented until another is completed or where one requirement is implemented in the same increment as another one.

§ 2.1:

> Typically each increment is a complete system that is of value to the client.

> Some requirements may have mandatory precedences over other requirements or a condition that they are delivered in the same release.
> Release planning for incremental software development includes the assignment of requirements to releases such that all technical and budget constraints are fulfilled.

§ 2.3 "Evolution of Increments":

> As result of the planning process, different increments will be composed out of the given set of requirements. These increments are planned up-front but the possibility of re-planning after any increment is allowed. This re-planning may involve changing some requirements, priorities and constraints and/or introducing new ones. It necessitates a reassignment of requirements (not already implemented in former releases) to increments. Throughout the paper, we assume that the number of releases is not fixed upfront.

> The output is a definition of increments Inck, Inck+1, Inck+2, … with Inct ⊂ Rk for all t = k, k+1, k+2, …
> The different increments are disjoint, i.e., Incs ∩ Inct = ∅ for all s,t ∈ {k, k+1, k+2, …}.

§ 2.4 "Effort Constraints":

> Typically project releases are planned for certain dates. This introduces a size constraint Sizek in terms of available effort of any released increment Inck.

§ 2.5 "Precedence and Other Dependency Constraints":

> In a typical real world project, it is likely that some requirements must be implemented before others. There might be logical, technical or resource related reasons that the realization of one requirement must be in place before the realization of another.

> With similar arguments as above there might be logical, technical or resource related reasons that the realization of one requirement must be in place in the same increment as another one.

§ 2.6 problem statement, constraint labels:

> (1) Σ r(i) ∈ Inc(m) effort(ri, Rk) ≤ Sizem for m = k,k+1,… (Effort constraints)
> (2) ω*(ri) ≤ ω*(rj) for all pairs (ri. rj) ∈ Ψk (Precedence constraints)
> (3) ω*(ri) = ω*(rj) for all pairs (ri. rj) ∈ ξk (Coupling constraints)

## Themes (Karim and Ruhe; Agarwal, Karimpour and Ruhe), secondary only

Source: arXiv:2603.28677v1 (as above). **Secondary**.

> Karim and Ruhe [15], for instance, introduced “theme” where the requirements within a theme would be preferably delivered or postponed together. Aydemir et al. [2] further extended it to goal modeling, e.g., by including all the leaf goals of a theme in the next release or excluding them altogether. While theme models a “requires” relation symmetrically (i.e., “req1 requires req2, and req2 requires req1”) [6], the asymmetric “requires” is more common and practically influential to prioritization.

> Karim and Ruhe [15] showed that maximizing individual requirement’s value and theme-based coherence are conflicting objectives.

## Shape as stated

The NRP (Bagnall et al.) models a single **next release** as a selection of features/requirements that maximizes stakeholder (client) value within a resource bound; the abstract names no grouping container between the requirement and the release. EVOLVE (Greer and Ruhe) assigns each requirement in the current set R_k to exactly one **increment** (= release); increments are disjoint, effort-bounded, re-planned after each increment, open in number, and "each increment is a complete system that is of value to the client". Its inter-requirement relations are **precedence** (one before another: same or earlier increment) and **coupling** (must be in the same increment). Carlshamre et al., as reported secondarily, distinguish two-way "AND", one-way "requires", and value-related (CVALUE) dependencies, finding value-related dependencies common. The **theme** (Karim and Ruhe; Agarwal, Karimpour and Ruhe), as reported secondarily, is a set of requirements "preferably delivered or postponed together", treated as a soft objective (theme coherence) that conflicts with maximizing individual requirement value. The HICSS theme paper's own text was refused, so how themes are defined or detected there is not established by a source read. None of the read sources defines a container that carries a version apart from the increment/release itself.
