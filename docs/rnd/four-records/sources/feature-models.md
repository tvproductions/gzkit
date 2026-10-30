# Software product-line feature models: FODA (Kang et al. 1990)

Source: Kang, K. C., Cohen, S. G., Hess, J. A., Novak, W. E., Peterson, A. S. (1990). *Feature-Oriented Domain Analysis (FODA) Feasibility Study.* Technical Report CMU/SEI-90-TR-21, Software Engineering Institute, Carnegie Mellon University, November 1990.

Access date: 2026-10-30.

## Retrieval status

- DTIC copy, https://apps.dtic.mil/sti/pdfs/ADA235785.pdf: **refused** (HTTP 403 to an automated GET). Not worked around.
- SEI library record, https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/, linking to https://www.sei.cmu.edu/documents/1011/1990_005_001_15872.pdf: **read** (full report, text-extracted). **Primary.**

## Feature and the purpose of the method

Source: CMU/SEI-90-TR-21, Abstract/Executive summary. Primary.

> The primary focus of the method is the identification of prominent or distinctive features of software systems in a domain. These features are user-visible aspects or characteristics of the domain. They lead to the creation of a set of products that define the domain and also give the method its name: Feature-Oriented Domain Analysis (FODA). The features define both common aspects of the domain as well as differences between related systems in the domain. Features are also used to define the domain in terms of the mandatory, optional, or alternative characteristics of these related systems.

Source: CMU/SEI-90-TR-21, glossary. Primary.

> Feature: A prominent or distinctive user-visible aspect, quality, or characteristic of a software system or systems [American 85].

## The feature model

Source: CMU/SEI-90-TR-21, § 5.1. Primary.

> Customers need to know the essential capabilities of the application that satisfy their needs. These capabilities might include features such as:
> 1. services provided by the application,
> 2. performance of the application,
> 3. hardware platform required by the application,
> 4. cost,
> 5. others

> Since the primary interest is in the commonality of a family of applications, the feature model should capture the common features and differences of the applications in the domain. The features in the feature model will be used to generalize and parameterize other models.

Source: CMU/SEI-90-TR-21, § 5.1.2 "Model Description", pp. 35–36. Primary.

> Features are the attributes of a system that directly affect end-users. The end-users have to make decisions regarding the availability of features in the system, and they have to understand the meaning of the features in order to use the system.

> A feature model represents the standard features of a family of systems in the domain and relationships between them. The structural relationship consists of, which represents a logical grouping of features, is of interest. Alternative or optional features of each grouping must be indicated in the feature model. For example, the automatic and manual features are alternatives and the air-conditioning feature is optional, as indicated in Figure 5-1 by small arcs and circles, respectively. Each feature must be named distinctively and the definition should be included in the domain terminology dictionary.

> Alternative features can be thought of as specializations of a more general category. [...] The term "alternative features" is used (rather than "specialization features") to indicate that no more than one specialization can be made for a system. However, the attributes of (i.e., the description made for) a general feature are inherited by all its specializations.

> Composition rules define the semantics existing between features that are not expressed in the feature diagram. All optional and alternative features that cannot be selected when the named feature is selected must be stated using the "mutually exclusive with" statement. All optional and alternative features that must be selected when the named feature is selected must be defined using the "requires" statement.

Figure 5-1 ("Example Showing Features of a Car") labels, as extracted: "Car"; "Mandatory features": Transmission, Horsepower; "Optional feature": Air conditioning; "Alternative features": Manual, Automatic; "Rationale: Manual more fuel efficient"; "Composition rule: Air conditioning requires Horsepower > 100".

> Selection of optional or alternative features is not made arbitrarily. It is usually made based on a number of objectives or concerns that the end-user (and customer) has.

> A set of issues and alternative decisions in the selection of optional and alternative features is captured using the form in Appendix A.5.

> One of the fundamental trade-offs a system architect makes is deciding when to "bind" or fix the value of a feature, as this will have an impact on the final architecture. For the purpose of generalization and parameterization of the software architecture, alternative and optional features are grouped into three classes based on when the binding of those features (i.e., instantiation of software) is done, as depicted in Figure 5-2.

## Shape as stated

FODA's unit is the **feature**: a user-visible aspect, quality or characteristic of systems in a domain. The **feature model** is a tree whose structural relation is "consists of" ("a logical grouping of features"), with each child marked **mandatory**, **optional**, or **alternative** (at most one alternative per grouping in a given system). **Composition rules** outside the tree state cross-tree constraints: "requires" and "mutually exclusive with". Each feature is named and defined in the domain terminology dictionary; the rationale for choosing among optional/alternative features is recorded as issues and decisions. Features have a **binding time** (when the choice is fixed). The model describes a family of systems; one product is a selection of features consistent with the tree and composition rules. FODA has no work, release or version record; its containers describe what a product can consist of, not when it is delivered.
