# Design by Contract — primary-source excerpts (Meyer / Eiffel Software)

Retrieved: 2026-10-26

**These are quoted excerpts, not full text.** Each passage is reproduced exactly
as served by the URL given, under the section heading named. Nothing here is a
paraphrase; editorial notes are marked "Note". The source pages are copyright
Eiffel Software (Interactive Software Engineering Inc.); consult the URLs for the
full text.

## Sources

| Key | Title | URL | Authorship as stated on the page |
|-----|-------|-----|----------------------------------|
| INTRO | Building bug-free O-O software: An Introduction to Design by Contract™ | <https://www.eiffel.com/values/design-by-contract/introduction/> (older copy: <https://archive.eiffel.com/doc/manuals/technology/contract/>) | Published by Eiffel Software; no author named on the page. The archive copy's reference list cites Meyer's works. |
| I2E | I2E: Design by Contract and Assertions (Invitation to Eiffel) | <https://www.eiffel.org/doc/eiffel/I2E-_Design_by_Contract_and_Assertions> | Bertrand Meyer, per <https://www.eiffel.org/doc/eiffel/I2E-_Invitation_to_Eiffel_Copyright> ("Title: Invitation to Eiffel, Eiffel Software Technical Report TR-EI-67/IV." … "Author / Bertrand Meyer"). |
| ET | ET: Design by Contract (tm), Assertions and Exceptions (Eiffel Tutorial) | <https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_%28tm%29%2C_Assertions_and_Exceptions> | Eiffel Software; copyright page (<https://www.eiffel.org/doc/eiffel/ET-_Eiffel_Tutorial_Copyright>) names "Interactive Software Engineering Inc. (Eiffel Software), 2001" and no individual author. |
| DBCA | Design by Contract and Assertions (eiffel.org Solutions) | <https://www.eiffel.org/doc/solutions/Design_by_Contract_and_Assertions> | Eiffel Software documentation; no author named. |
| OPTS | Assertion Options (EiffelStudio) | <https://www.eiffel.org/doc/eiffelstudio/Assertion_Options> | Eiffel Software documentation. |
| SETLVL | Setting the assertion level (EiffelStudio) | <https://www.eiffel.org/doc/eiffelstudio/Setting_the_assertion_level> | Eiffel Software documentation. |
| CFGCHG | Assertions checking configuration changes (EiffelStudio 5.0 notes) | <https://www.eiffel.org/doc/eiffelstudio/Assertions_checking_configuration_changes> | Eiffel Software documentation. |
| BLOG | Fine tuning assertion checking dynamically (eiffel.org blog, 2007) | <https://www.eiffel.org/blog/maverick/fine_tuning_assertion_checking_dynamically> | Post by Simon Hudon; the quoted reply is signed "Manu". Not Meyer; community material, included only for the run-time-change question. |

Refusals: none. Every host above returned HTTP 200 with the content; no block
page or login wall was met.

## 1. The contract: obligations and benefits of client and supplier

**INTRO, § 1 – Introduction**

> Under the Design by Contract theory, a software system is viewed as a set of communicating components whose interaction is based on precisely defined specifications of the mutual obligations — contracts.

**INTRO, § 3 – The notion of contract**

> In human affairs, contracts are written between two parties when one of them (the supplier) performs some task for the other (the client). Each party expects some benefits from the contract, and accepts some obligations in return. Usually, what one of the parties sees as an obligation is a benefit for the other. The aim of the contract document is to spell out these benefits and obligations.

> This contract governs the relations between the routine and any potential caller. It contains the most important information that can be given about the routine: what each party in the contract must guarantee for a correct call, and what each party is entitled to in return.

**ET, § Design by Contract™ basics**

> Note how the obligation for each of the parties maps onto a benefit for the other. This will be a general pattern.

**I2E, § Design by Contract™**

> Writing assertions amounts to spelling out the terms of the contract which governs the relationship between a routine and its callers. The precondition binds the callers; the postcondition binds the routine.

## 2. Precondition and postcondition

**ET, § Design by Contract™ basics**

> The client's obligation, which protects the supplier, is called a precondition. It states what the client must satisfy before requesting a certain service. The client's benefit, which describes what the supplier must do (assuming the precondition was satisfied), is called a postcondition.

**ET, § Preconditions**

> The routine does not guarantee anything for a call that does not satisfy the precondition. It is in fact part of the Eiffel method that a routine body should never test for the precondition, since it is the client's responsibility to ensure it.

**ET, § Postconditions**

> The postcondition of a routine expresses what the routine guaranteed to its clients for calls satisfying the precondition.

**INTRO, § 3 – The notion of contract**

> The require clause introduces an input condition, or precondition; the ensure clause introduces an output condition, or postcondition. Both of these conditions are examples of assertions, or logical conditions (contract clauses) associated with software elements.

## 3. Class invariant, and when it must hold

**INTRO, § 5 – Invariants**

> An assertion describing a property which holds of all instances of a class is called a class invariant.

> Viewed from the contract theory, an invariant is a general clause which applies to the entire set of contracts defining a class.

**I2E, § The role of assertions**

> A class invariant must be satisfied by every instance of the class whenever the instance is externally accessible: after creation, and after any call to an exported routine of the class.

**ET, § Class invariants**

> It must be satisfied on exit by any creation procedure, and is implicitly added to both the precondition and postcondition of every exported routine.

**DBCA, § Valid State for Instances**

> The name invariant implies that the assertion can never be false ... and that's true up to a point. It's really more like, "it must be true at times when it really counts".

> At runtime the invariant must be true for an instance at anytime that the instance is available to clients. In general, this means that the invariant must be true before and after the execution of every exported routine.

## 4. Violation: whose bug, exceptions, rescue and retry

**ET, § Run-time assertion monitoring**

> Rule -- Assertion Violation: A run-time assertion violation is the manifestation of a bug.

> A precondition violation signals a bug in the client, which did not observe its part of the deal.
>
> A postcondition (or invariant) violation signals a bug in the supplier -- the routine -- which did not do its job.

> An assertion violation, if detected at run time under one of these options other than the first, will cause an exception ( "Exception handling" ). Unless the software has an explicit "retry" plan as explained in the discussion of exceptions, the violation will produce an exception trace and cause termination (or, in EiffelStudio, a return to the environment's browsing and debugging facilities at the point of failure).

**INTRO, § 9 – Exception handling**

> An exception is the element's inability to fulfil its contract, for any reason: a hardware failure has occurred, a called routine has failed, a software bug makes it impossible to satisfy the contract.

> 1. Retrying: an alternative strategy is available. The routine will restore the invariant and and make another attempt, using the new strategy.
>
> 2. Organized panic: no such alternative is available. Restore the invariant, terminate, and report failure to the caller by triggering a new exception. (The caller will itself have to choose between the same three responses.)

Note: the duplicated "and and" is in the source.

**ET, § Exception handling**

> Behind Eiffel's exception handling scheme lies the principle -- at first an apparent platitude, but violated by many existing mechanisms -- that a routine should either succeed or fail. […] Otherwise it would be possible for a routine to miss its contract and yet return to its caller in a seemingly normal state. That is the worst possible way to handle an exception.

> Such a rescue clause should, before terminating, restore the invariant of the class so that the caller and possible subsequent retryattempts from higher up find the objects in a consistent state.

Note: "retryattempts" is run together in the source. "[…]" marks an elided sentence.

## 5. Assertion monitoring: levels, turning checking off and on

**ET, § Run-time assertion monitoring**

> Contracts in Eiffel are not just wishful thinking. They can be monitored at run time under the control of compilation options.

> That violations indicate bugs explains why it is legitimate to enable or disable assertion monitoring through mere compilation options: for a correct system -- one without bugs -- assertions will always hold, so the compilation option makes no difference to the semantics of the system.

> Hence the presence of the compilation options, which EiffelStudio lets you set separately for each class, with defaults at the system and cluster levels:
>
> no : assertions have no run-time effect.
>
> require : monitor preconditions only, on routine entry.
>
> ensure : preconditions on entry, postconditions on exit.
>
> invariant : same as ensure, plus class invariant on both entry and exit for qualified calls.
>
> all : same as invariant, plus check instructions, loop invariants and loop variants.

> When releasing the final version of a system, it is usually appropriate to turn off assertion monitoring, or bring it down to the require level. The exact policy depends on the circumstances; it is a trade off between efficiency considerations, the potential cost of mistakes, and how much the developers and quality assurance team trust the product. When developing the software, however, you should always assume -- to avoid loosening your guard -- that in the end monitoring will be turned off.

**INTRO, § 7 – Testing, debugging, quality assurance**

> Compilation options enable the developers, class by class, what effect assertions should have if any: no assertion checking (under which assertions have no effect at all, serving as a form of standardized comments), preconditions only (the default), preconditions and postconditions, all of the above plus class invariants, all assertions.

**I2E, § Contracts for testing and debugging**

> When monitoring is on, an assertion which evaluates to true has no further effect on the execution. An assertion that evaluates to false will trigger an exception, as described next; unless you have written an appropriate exception handler, the exception will cause an error message and termination with a precise message and a call trace.

**DBCA, § Contracts and Debugging**

> It is possible selectively to turn off and on the runtime checking of assertions by changing project settings.

> Based on this knowledge, we can say that it is most practical first to turn off runtime checking of postconditions and invariants as we gain confidence in a class.

**OPTS, § Assertion Options**

> Each assertion setting can be configured independently of the others.

> Setting Supplier Precondition to True is a convenient way of setting only precondition checking on libraries, while allowing your own software to be checked to whatever degree you've determined by adjusting the other assertion level settings.

**SETLVL, § Setting the assertion level**

> You must recompile your project for the changes to take effect.

**CFGCHG, § Assertions checking configuration changes**

> In 4.5, assertions of a certain type where checked if their level was below the requested level. […] Meaning that you could not just check one type of assertions. With 5.0 this is now possible and we changed the presentation to follow the cost to evaluate a given type of assertions, the first one being the less expensive:

> The default assertion level has changed too. Not specifying any assertion level used to be equivalent to selecting the 'require' level. This is not the case any more in 5.0 it will be not checking assertions.

Note: "where" (for "were") and the run-on last sentence are in the source. The
ET and INTRO pages give `require` as the default; CFGCHG records that from
EiffelStudio 5.0 an unspecified level means no checking. The sources disagree on
the default, and the disagreement is version-dependent.

**BLOG, reply signed "Manu" (2007)**

> The answer is that you can specify in the project settings of EiffelStudio which assertions will be monitored during execution, but once it is setup, you cannot change those settings during execution.
