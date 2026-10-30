# Manufacturing bills of material: kit, phantom, model/option class, configuration, planning bill

Access date for every source: 2026-10-30.

## Retrieval status

| Source | Status |
| --- | --- |
| ASCM/APICS *Dictionary* (definitions of kit, phantom bill, planning bill, modular bill) | **Not read**: commercial; no open copy. |
| Oracle E-Business Suite *Bills of Material User's Guide*, Release 12.1, chapter "Bills of Material", https://docs.oracle.com/cd/E18727_01/doc.121/e13688/T272930T275774.htm | **Read**. Primary (vendor product documentation). |
| Oracle Fusion Cloud SCM, "Plan for Pick-to-Order Kits" (26B), https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faspf/plan-for-pick-to-order-kits.html | **Read**. Primary (vendor product documentation). |

These are one vendor's definitions; the general manufacturing-dictionary definitions were not available.

## Bill types (Oracle EBS 12.1)

Source: Oracle *Bills of Material User's Guide* 12.1, "Bills of Material". Primary.

> Oracle Manufacturing and Oracle Order Management use bills of material to store lists of items that are associated with a parent item and information about how each item is related to its parent. Oracle Manufacturing supports standard, model, option class, and planning bills of material.

> **Standard Bill of Material**
> A standard bill of material is the most common type of bill and lists the mandatory components, the required quantity of each component, and information to control work in process, material planning, and other Oracle Manufacturing functions. Examples include bills for manufacturing assemblies, pick-to-order bills, kit bills, and phantoms.
>
> A configuration bill (a type of standard bill) is a set of option choices made from a model bill that comprise a buildable, sellable product. Configuration items and bills are automatically created from model bills after a customer chooses options on a sales order. Or, you can manually create configuration bills by choosing options directly from a model bill.

> **Model Bill of Material**
> A model bill of material defines the list of options and option classes you can choose in Oracle Order Management to order a configuration. A model bill also specifies mandatory components or included items that are required for each configuration of that model. You do not order or build the model itself: you order and build configurations of the model. A model bill can be either assemble-to-order or pick-to-order.

> **Option Class Bill of Material**
> An option class is an item that groups optional components on a bill. An option class is an item that becomes a level in your model bill of material. Option classes can also have mandatory components that apply for all of its options. For example, when you order a computer, the monitor is an option class, and the specific type of monitor you order is an option within that option class. An option class bill can be either assemble-to-order or pick-to-order.

> **Planning Bill of Material**
> A planning bill of material is a bill of material structure that includes a percentage distribution for its components. The percentages associated with the components on a planning bill of material do not need to add to 100%. You can define alternate and common planning bills, where the bill you reference as a common must be another planning bill.

## Phantoms (Oracle EBS 12.1)

Source: same chapter, "Phantoms". Primary.

> A phantom assembly is a non-stocked assembly that lets you group together material needed to produce a subassembly. When you create a bill of material for a parent item, you can specify whether a component is a phantom. One bill of material can represent a phantom subassembly for one parent item, and a stocked subassembly for another parent item.
>
> Oracle Work in Process explodes through a phantom subassembly to the components as if the components were tied directly to the parent assembly.

> In general, phantom assemblies behave like normal assemblies when they represent a top level assembly, such as when you master schedule them or manufacture them using a discrete job. As a subassembly, however, they lose their identity as distinct assemblies and are a collection of their components. The components of the phantom subassembly are included on the job and on the pick list of the job-not the phantom itself.

> When model or option class bills are components to another bill of material, the component supply type is phantom.

> The cost rollup treats phantom assemblies the same as regular assemblies. The phantom is treated as a distinct entity; the cost elements of the phantom (material, resource, and so on) are added to the cost elements of the higher assembly.

## Valid parent/component relationships (Oracle EBS 12.1)

Source: same chapter, table "Valid Parent/Component Relationships". Primary. (Table flattened from HTML.)

> Parent BOM Item Type — Component BOM Item Type
> Standard Item — Standard Item
> Model Item — Standard Item, Model Item, Option Class Item
> Option Class Item — Standard Item, Model Item, Option Class Item
> Planning Item — Standard Item, Model Item, Option Class, Planning Item

Source: same chapter, component attributes table. Primary. The attributes "Mutually Exclusive Options" and "Optional Flag" are marked "No" for standard and planning parents and "Yes" for model and option class parents. Validation rules include:

> You cannot add an optional component to a bill that is neither model or option class.

> You cannot add a component, whose planning percent is not equal to 100, to a standard bill.

Source: same chapter, "Referencing Common Bills and Routings". Primary.

> When you create a bill, it exists only in the current organization. To use a bill in another organization, you must either copy it or reference it as a common.

## Pick-to-order kit (Oracle Fusion Cloud SCM 26B)

Source: "Plan for Pick-to-Order Kits". Primary.

> A Pick-To-Order (PTO) kit consists of a predefined list of mandatory components or items commonly referred to as standard bill of materials. When processing a customer sales order, these components are picked, packed, and shipped together. An example of a PTO kit is a motor car maintenance kit that consists of essential tools such as wrenches and jack.
>
> A PTO kit shouldn’t be confused with a PTO model. PTO kit is defined as an item with fixed components that displays the item structure and doesn't have options and classes.

> When a sales order is created for a PTO kit, Oracle Order Management automatically generates sales order lines for all its components.

> The PTO kits are nonstockable and nontransactable and hence any existing supply created on PTO kit is ignored by supply planning.

## Shape as stated

Oracle's bills are parent-to-component lists. A **standard bill** lists mandatory components; kits, pick-to-order bills and phantoms are standard bills. A **kit** (PTO kit) is a fixed list of mandatory, non-selectable items picked and shipped together for an order; the kit itself is not stocked, and ordering it generates order lines for each component. A **phantom** is a non-stocked grouping that keeps its identity as a top-level item but, as a subassembly, "lose[s] [its] identity" and explodes into its components on the job; the same bill can be a phantom under one parent and stocked under another; its cost still rolls up as a distinct entity. A **model bill** lists the options and option classes from which an orderable **configuration** is chosen, plus mandatory "included items" required in every configuration; the model itself is never built. An **option class** groups optional components (with optional mutual exclusion) and may carry its own mandatory components. A **configuration bill** is the set of option choices made from a model for one order. A **planning bill** distributes demand by percentage across components (not required to total 100%) and is used for planning, not building. Bills can be shared across organizations by referencing a **common bill**. Prerequisite/enabling material is expressed only as mandatory components or included items; no separate prerequisite record appears.
