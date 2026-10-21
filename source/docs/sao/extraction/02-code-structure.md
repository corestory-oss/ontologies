# Phase 2: Code Structure (Layer 3)

This phase populates SAO Layer 3 --- the direct structural representation of source code. It is the largest and most critical extraction phase: every subsequent phase depends on the code structure graph built here.

**Confidence level:** Deterministic. No inference is needed; this phase captures what the code literally says. AST parsing is the primary technique, achieving ~90% automation.

**Input:** Phase 1 outputs --- **StorageLocation**, **CodeContainer**, **ProgrammingLanguage** instances.

**Output:** **EncapsulationUnit**, **CallableUnit**, **DataStructure**, **DataElement**, **Parameter**, **TypeExpression**, **ControlFlow**, **DataFlow**, **DefinitionReference**, **CodeBlock**, **Statement**, **Annotation**, plus platform-specific extension classes.

---

## Containment hierarchy

Phase 2 builds the structural spine of the SAO model. Every element produced here lives within this containment hierarchy:

```
StorageLocation
  └── CodeContainer
        └── EncapsulationUnit
              ├── CallableUnit
              │     ├── Parameter
              │     ├── CodeBlock
              │     │     └── Statement
              │     ├── ControlFlow (edges)
              │     └── DataFlow (edges)
              ├── DataStructure
              │     └── DataElement
              │           └── TypeExpression
              ├── DataElement (unit-level fields)
              └── DefinitionReference
```

The extraction agent MUST process sub-phases in order (2a through 2h) because later sub-phases reference entities created in earlier ones.

---

## Sub-phase 2a: Encapsulation Units

Parse each **CodeContainer** using a language-appropriate AST parser and create an **EncapsulationUnit** for every class, module, program, package, trait, or interface found.

### Required attributes

| Attribute | Range | Rule |
|---|---|---|
| `encapsulation_type` | `EncapsulationType` | MUST set. See enum values below. |
| `qualified_name` | string | MUST set to the fully qualified name (e.g., `com.example.UserService`). |
| `visibility` | `VisibilityType` | SHOULD set when the language has visibility modifiers. |
| `is_abstract` | boolean | SHOULD set for abstract classes, interfaces, and traits. |
| `is_final` | boolean | SHOULD set when the language supports sealed/final. |
| `is_reusable` | boolean | MAY set if the unit is designed for reuse (libraries, shared modules). |
| `stereotype` | string | MAY set to indicate a pattern role (e.g., `Service`, `Repository`, `Controller`, `DTO`). |
| `line_start` / `line_end` | integer | SHOULD set for source-level traceability. |

### EncapsulationType enum (33 values)

**Object-oriented:**
- `class`
- `interface`
- `abstract_class`
- `trait`
- `enum_class`
- `record_class`
- `singleton`

**Procedural:**
- `program`
- `subprogram`
- `unit`

**Functional / organizational:**
- `module`
- `namespace`
- `package`
- `library`

**Component / pattern:**
- `object`
- `component`
- `service`
- `controller`
- `script`
- `composite`
- `other`

**Database:**
- `stored_procedure`
- `function_package`
- `trigger`
- `view`

**Mainframe:**
- `batch_program`
- `online_program`
- `copybook`
- `rpg_module`
- `rpg_service_program`
- `pli_procedure`
- `pli_package`
- `assembler_csect`

### Required relationships

| Relationship | Target | Rule |
|---|---|---|
| `defined_in_container` | **CodeContainer** | MUST link every unit to its source container. |
| `extends_units` | **EncapsulationUnit** | MUST set for inheritance (e.g., Java `extends`, Python base classes). |
| `implements_contracts` | **Contract** | MUST set for interface implementation (e.g., Java `implements`, Rust `impl Trait`). |
| `contains_callable_units` | **CallableUnit** | Populated in sub-phase 2b. |
| `contains_data_structures` | **DataStructure** | Populated in sub-phase 2c. |
| `contains_data_elements` | **DataElement** | For unit-level fields not inside a **DataStructure**. |
| `uses_definitions` | **DefinitionReference** | Populated in sub-phase 2d. |

### VisibilityType enum

- `public`
- `private`
- `protected`
- `internal`
- `package`

### Procedure

1. For each **CodeContainer**, invoke the AST parser for the container's language (determined via `written_in_language`).
2. Walk the top-level AST nodes. For each class/module/program/trait/interface/enum/record declaration, create an **EncapsulationUnit**.
3. For nested types (inner classes, companion objects), create a separate **EncapsulationUnit** and record the nesting relationship via a second `defined_in_container` link to the same **CodeContainer**.
4. Resolve inheritance: set `extends_units` to the parent **EncapsulationUnit** by matching qualified names. If the parent is in an external dependency, create a stub **EncapsulationUnit** with a `qualified_name` only.
5. Resolve interface implementation: set `implements_contracts` to the corresponding **Contract** instance. If no **Contract** exists yet, create one.

### Example

```yaml
# Java class with inheritance and interface implementation
order_service:
  a: EncapsulationUnit
  name: OrderService
  encapsulation_type: class
  visibility: public
  qualified_name: com.example.orders.OrderService
  is_abstract: false
  is_final: false
  stereotype: Service
  line_start: 15
  line_end: 280
  defined_in_container: order_service_file
  extends_units:
    - base_service
  implements_contracts:
    - order_operations_contract

# COBOL batch program
payroll_calc:
  a: EncapsulationUnit
  name: PAYROLL-CALC
  encapsulation_type: batch_program
  qualified_name: PAYROLL-CALC
  defined_in_container: payroll_calc_source
```

---

## Sub-phase 2b: Callable Units

For each **EncapsulationUnit**, extract every method, function, paragraph, procedure, or other invocable construct.

### Required attributes

| Attribute | Range | Rule |
|---|---|---|
| `callable_type` | `CallableType` | MUST set. See enum values below. |
| `visibility` | `VisibilityType` | SHOULD set when the language has visibility modifiers. |
| `return_type` | string | SHOULD set (use the source-level type name as-is). |
| `has_return_type` | **TypeExpression** | MAY set for structured type modeling (see sub-phase 2c). |
| `is_async` | boolean | MUST set to `true` for async/await functions. |
| `is_static` | boolean | MUST set to `true` for static/class methods. |
| `is_pure` | boolean | MAY set if determinable (no side effects). |
| `is_virtual` | boolean | SHOULD set for virtual/overridable methods. |
| `is_override` | boolean | SHOULD set for methods that override a parent. |
| `is_recursive` | boolean | MAY set if the callable calls itself. |
| `is_inline` | boolean | MAY set for inline functions. |
| `complexity_score` | integer | SHOULD compute cyclomatic complexity. |
| `entry_point_type` | `EntryPointType` | MUST set for program entry points. |
| `documentation` | string | MAY extract from docstrings/Javadoc. |
| `line_start` / `line_end` | integer | SHOULD set for source-level traceability. |

### CallableType enum (53 values)

**Object-oriented methods:**
- `method`
- `static_method`
- `constructor`
- `destructor`
- `property_getter`
- `property_setter`
- `operator_overload`
- `conversion_operator`
- `indexer`
- `abstract_method`
- `virtual_method`

**Procedural:**
- `function`
- `procedure`
- `subroutine`
- `paragraph`
- `section`
- `rpg_subprocedure`
- `pli_entry`
- `assembler_entry`
- `rpg_subroutine`

**Functional:**
- `lambda`
- `closure`
- `higher_order_function`
- `curried_function`
- `functor`

**Event handling:**
- `event_handler`
- `callback`
- `delegate`
- `signal_handler`

**Database:**
- `stored_procedure`
- `stored_function`
- `trigger_body`
- `cursor`

**Concurrency:**
- `coroutine`
- `generator`
- `async_function`
- `thread_entry`
- `task`

**Testing:**
- `test_case`
- `test_fixture`
- `mock`

**Other:**
- `macro`
- `template`
- `generic_method`
- `main_entry`
- `interrupt_handler`
- `exception_handler`
- `finalizer`
- `factory_method`
- `extension_method`
- `script_function`
- `command`
- `other`

### EntryPointType enum

- `main_program`
- `transaction_entry`
- `event_handler`
- `scheduled_entry`
- `api_endpoint`

### CallableCategory enum

The `callable_category` attribute classifies a callable's behavioral role:

- `normal`
- `operator`
- `main_entry`

### Required relationships

| Relationship | Target | Rule |
|---|---|---|
| `contained_in_unit` | **EncapsulationUnit** | MUST link every callable to its containing unit. |
| `has_parameters` | **Parameter** | Populated below. |
| `overrides_callable` | **CallableUnit** | MUST set when a method overrides a parent method. |
| `invokes_callables` | **CallableUnit** | Populated in sub-phase 2e. |
| `accesses_data_elements` | **DataElement** | Populated in sub-phase 2f. |
| `modifies_data_elements` | **DataElement** | Populated in sub-phase 2f. |

### Parameters

For each parameter of a **CallableUnit**, create a **Parameter** instance.

**Parameter** inherits from **DataElement** and adds:

| Attribute | Range | Rule |
|---|---|---|
| `direction` | `ParameterDirection` | SHOULD set. Values: `input`, `output`, `input_output`, `return`. |
| `position` | integer | MUST set (0-based or 1-based, be consistent). |
| `passing_mechanism` | `PassingMechanism` | SHOULD set. Values: `by_value`, `by_reference`, `by_name`, `by_result`. |
| `has_type` | **TypeExpression** | MAY set for structured type modeling. |
| `data_type` | string | SHOULD set (inherited from **DataElement**; use source-level type name). |
| `is_nullable` | boolean | SHOULD set when determinable. |
| `default_value` | string | SHOULD set when a default is declared. |

Link each **Parameter** back via `parameter_of` to its **CallableUnit**.

### Procedure

1. For each **EncapsulationUnit**, walk the AST children that are callable declarations.
2. Create a **CallableUnit** for each, setting `callable_type` based on the AST node kind.
3. For each parameter in the callable's signature, create a **Parameter** and link via `has_parameters` / `parameter_of`.
4. Compute `complexity_score` if the AST parser supports control-flow analysis.
5. For `main` functions, `__init__` methods, or COBOL `PROCEDURE DIVISION`, set `entry_point_type`.

### Example

```yaml
# Java method with parameters
create_order:
  a: CallableUnit
  name: createOrder
  callable_type: method
  visibility: public
  return_type: Order
  is_async: false
  is_static: false
  complexity_score: 12
  line_start: 45
  line_end: 92
  contained_in_unit: order_service
  has_parameters:
    - create_order_request_param
    - create_order_user_param

create_order_request_param:
  a: Parameter
  name: request
  data_type: CreateOrderRequest
  direction: input
  position: 1
  passing_mechanism: by_value
  is_nullable: false
  parameter_of: create_order

create_order_user_param:
  a: Parameter
  name: currentUser
  data_type: User
  direction: input
  position: 2
  passing_mechanism: by_value
  is_nullable: false
  parameter_of: create_order

# COBOL paragraph
calc_totals:
  a: CallableUnit
  name: CALCULATE-TOTALS
  callable_type: paragraph
  contained_in_unit: payroll_calc
```

---

## Sub-phase 2c: Data Structures and Data Elements

Extract struct/record/group declarations and their fields from each **EncapsulationUnit**.

### DataStructure attributes

| Attribute | Range | Rule |
|---|---|---|
| `structure_type` | `DataStructureType` | MUST set. See enum values below. |
| `structure_category` | `DataStructureCategory` | SHOULD set. |
| `visibility` | `VisibilityType` | SHOULD set. |
| `is_mutable` | boolean | SHOULD set. |
| `is_serializable` | boolean | MAY set. |
| `is_nested` | boolean | MUST set to `true` for nested/inner structures. |
| `nesting_level` | integer | MUST set for COBOL group items (01, 05, 10, etc.). |
| `is_packed` | boolean | MAY set for packed structs. |
| `alignment` | integer | MAY set for explicit alignment. |
| `size_bytes` | integer | MAY set when determinable. |
| `persistence_type` | `PersistenceType` | MAY set (e.g., `transient`, `database`, `file`, `memory`, `cache`). |
| `line_start` / `line_end` | integer | SHOULD set. |

### DataStructureType enum (50 values)

**Object-oriented:**
- `class_data`
- `inner_class`
- `anonymous_class`

**Procedural:**
- `struct`
- `record`
- `union`

**COBOL / Mainframe:**
- `group_item`
- `copybook_structure`
- `commarea`
- `linkage_section`
- `rpg_data_structure`
- `pli_structure`
- `assembler_dsect`
- `cobol_file_descriptor`

**Functional:**
- `algebraic_data_type`
- `type_class`
- `product_type`
- `sum_type`

**Collections:**
- `array`
- `dynamic_array`
- `list`
- `dictionary`
- `set`
- `queue`
- `stack`
- `tree`
- `graph`

**Database:**
- `table_structure`
- `view_structure`
- `cursor_structure`
- `rowtype`

**DDD:**
- `value_object`
- `dto`

**Other:**
- `tuple`
- `pair`
- `enum`
- `flags`
- `configuration_object`
- `message`
- `event`
- `command`
- `json_schema`
- `xml_schema`
- `protobuf_message`
- `avro_record`
- `smart_pointer`
- `reference_wrapper`
- `opaque_type`
- `variant`
- `other`

### DataStructureCategory enum

- `composite`
- `collection`
- `hierarchical`
- `value_type`
- `reference_type`
- `union`

### DataStructure relationships

| Relationship | Target | Rule |
|---|---|---|
| `contained_in_unit` | **EncapsulationUnit** | MUST link to the containing unit. |
| `structure_contains_elements` | **DataElement** | Populated below. |
| `has_parent_structure` | **DataStructure** | MUST set for nested structures. |
| `has_child_structures` | **DataStructure** | Inverse of `has_parent_structure`. |

### DataElement attributes

For each field, variable, or constant within a **DataStructure** (or directly within an **EncapsulationUnit**), create a **DataElement**.

| Attribute | Range | Rule |
|---|---|---|
| `data_type` | string | MUST set (source-level type name). |
| `element_category` | `DataElementCategory` | SHOULD set. |
| `visibility` | `VisibilityType` | SHOULD set. |
| `is_constant` | boolean | MUST set to `true` for constants/finals. |
| `is_nullable` | boolean | SHOULD set when determinable. |
| `default_value` | string | SHOULD set when a default is declared. |
| `size_specification` | string | SHOULD set for COBOL PIC clauses or array dimensions. |
| `storage_class` | `StorageClass` | MAY set. Values: `automatic`, `static`, `heap`, `register`, `thread_local`, `external`. |
| `classification` | `DataClassificationType` | MAY set for data governance. |
| `line_number` | integer | SHOULD set. |

### DataElementCategory enum

- `field`
- `static_field`
- `local_variable`
- `parameter`
- `constant`
- `global_variable`
- `computed`
- `temporary`

### DataElement relationships

| Relationship | Target | Rule |
|---|---|---|
| `contained_in_structure` | **DataStructure** | MUST link when element belongs to a structure. |
| `contained_in_unit` | **EncapsulationUnit** | MUST link when element is at the unit level. |
| `has_parent_element` | **DataElement** | MUST set for COBOL hierarchical data items. |
| `has_child_elements` | **DataElement** | Inverse of `has_parent_element`. |
| `declared_type` | **TypeExpression** | MAY set for structured type modeling. |

### TypeExpression

For complex types (generics, unions, optional wrappers, function types), create a **TypeExpression**.

| Attribute | Range | Rule |
|---|---|---|
| `type_kind` | `TypeKind` | MUST set. |
| `base_type` | string | MUST set (e.g., `List`, `int`, `String`). |
| `has_type_parameters` | **TypeExpression**[] | MUST set for generic types (recursive). |
| `type_constraints` | string[] | MAY set (e.g., `T: Comparable`). |
| `is_nullable` | boolean | SHOULD set. |
| `nullability_model` | string | MAY set (e.g., `option_type`, `nullable_annotation`). |
| `pointer_semantics` | string | MAY set for pointer types (e.g., `raw`, `smart`, `weak`). |

### TypeKind enum

- `primitive`
- `generic`
- `union`
- `intersection`
- `alias`
- `pointer`
- `reference`
- `array_of`
- `function_type`
- `tuple_type`
- `optional_type`
- `constrained`
- `opaque`

### Procedure

1. For each **EncapsulationUnit**, walk its AST children for struct/record/class-data/enum declarations.
2. Create a **DataStructure** for each, choosing `structure_type` based on the language construct.
3. For each field within the structure, create a **DataElement** and link via `structure_contains_elements` / `contained_in_structure`.
4. For fields at the unit level (e.g., Java class fields not inside an inner struct), link directly via `contains_data_elements` on the **EncapsulationUnit**.
5. For complex types, create a **TypeExpression** and link via `declared_type` on the **DataElement**.
6. For COBOL group items, preserve the level-number hierarchy using `has_parent_element` / `has_child_elements`.

### Example

```yaml
# Java DTO with fields and a generic type
order_data:
  a: DataStructure
  name: Order
  structure_type: class_data
  structure_category: composite
  visibility: public
  is_mutable: true
  contained_in_unit: order_entity
  structure_contains_elements:
    - order_id_field
    - order_items_field
    - order_total_field

order_id_field:
  a: DataElement
  name: id
  data_type: Long
  element_category: field
  visibility: private
  is_constant: false
  is_nullable: false
  contained_in_structure: order_data

order_items_field:
  a: DataElement
  name: items
  data_type: "List<OrderItem>"
  element_category: field
  visibility: private
  is_constant: false
  is_nullable: false
  contained_in_structure: order_data
  declared_type: list_of_order_item

list_of_order_item:
  a: TypeExpression
  name: "List<OrderItem>"
  type_kind: generic
  base_type: List
  type_parameters:
    - a: TypeExpression
      name: OrderItem
      type_kind: primitive
      base_type: OrderItem

order_total_field:
  a: DataElement
  name: total
  data_type: BigDecimal
  element_category: field
  visibility: private
  is_constant: false
  is_nullable: false
  default_value: "0.00"
  contained_in_structure: order_data

# COBOL group item with hierarchy
employee_record:
  a: DataStructure
  name: EMPLOYEE-RECORD
  structure_type: group_item
  nesting_level: 1
  contained_in_unit: payroll_calc

emp_name:
  a: DataElement
  name: EMP-NAME
  data_type: "PIC X(30)"
  element_category: field
  size_specification: "PIC X(30)"
  contained_in_structure: employee_record
  parent_element: null

emp_salary:
  a: DataElement
  name: EMP-SALARY
  data_type: "PIC 9(7)V99"
  element_category: field
  size_specification: "PIC 9(7)V99"
  contained_in_structure: employee_record
```

---

## Sub-phase 2d: Definition References

Create a **DefinitionReference** for each import, include, COPY, using, or require statement.

### Attributes

| Attribute | Range | Rule |
|---|---|---|
| `reference_type` | `ReferenceType` | MUST set. |
| `reference_path` | string | MUST set (the import path or module name as written in source). |
| `alias` | string | SHOULD set when an alias is used (e.g., Python `import x as y`). |
| `is_wildcard` | boolean | MUST set to `true` for wildcard imports (e.g., `import java.util.*`). |
| `scope` | string | MAY set to indicate the scope of the import. |

### ReferenceType enum

- `import_module`
- `import_symbol`
- `include_source`
- `inherit`
- `implement`

### Relationships

| Relationship | Target | Rule |
|---|---|---|
| `referencing_container` | **CodeContainer** | MUST link to the source file performing the import. |
| `referenced_container` | **CodeContainer** | SHOULD link to the target file being imported (when resolvable). |
| `imports_symbols` | **EncapsulationUnit** / **CallableUnit** / **DataStructure** | SHOULD set to the specific entities imported. |

### Procedure

1. Walk each **CodeContainer**'s AST for import/include/COPY/using/require statements.
2. Create a **DefinitionReference** for each statement.
3. Resolve `referenced_container` by matching the import path to known **CodeContainer** instances from Phase 1.
4. If the import targets a specific symbol, set `imports_symbols` to the corresponding **EncapsulationUnit**, **CallableUnit**, or **DataStructure**.
5. Link the **DefinitionReference** to the containing **EncapsulationUnit** via `EncapsulationUnit.uses_definitions`.

### Example

```yaml
# Python import
import_order_model:
  a: DefinitionReference
  name: "from models.order import Order"
  reference_type: import_symbol
  reference_path: models.order
  is_wildcard: false
  referencing_container: order_service_file
  referenced_container: order_model_file
  imports_symbols:
    - order_entity

# COBOL COPY statement
copy_employee_record:
  a: DefinitionReference
  name: "COPY EMPREC"
  reference_type: include_source
  reference_path: EMPREC
  is_wildcard: false
  referencing_container: payroll_calc_source
  referenced_container: emprec_copybook

# Java wildcard import
import_java_util:
  a: DefinitionReference
  name: "import java.util.*"
  reference_type: import_module
  reference_path: java.util
  is_wildcard: true
  referencing_container: order_service_file
```

---

## Sub-phase 2e: Call Graph (ControlFlow)

For each **CallableUnit**, identify what it calls and build the call graph using **ControlFlow** edges.

### Attributes

| Attribute | Range | Rule |
|---|---|---|
| `flow_type` | `ControlFlowType` | MUST set. |
| `is_conditional` | boolean | SHOULD set to `true` if the call is inside a conditional branch. |
| `condition` | string | MAY set to the guard expression (e.g., `if user != null`). |

### ControlFlowType enum

- `call`
- `async_call`
- `branch`
- `jump`
- `return`
- `throw`
- `yield`

### Relationships

| Relationship | Target | Rule |
|---|---|---|
| `has_source_callable` | **CallableUnit** | MUST set (the caller). |
| `has_target_callable` | **CallableUnit** | MUST set (the callee). |
| `has_source_statement` | **Statement** | MAY set for statement-level precision. |
| `has_target_statement` | **Statement** | MAY set for statement-level precision. |

### Bidirectional call links

In addition to **ControlFlow** edge entities, the extraction agent MUST also populate:

- `CallableUnit.invokes_callables` --- the list of callables this one calls
- `CallableUnit.invoked_by_callables` --- the inverse (auto-populated if using LinkML inverse)

These provide direct navigation without querying **ControlFlow** entities.

### Procedure

1. For each **CallableUnit**, walk its AST body for call expressions, method invocations, and PERFORM statements.
2. Resolve each call target to a known **CallableUnit** by matching name and scope.
3. Create a **ControlFlow** edge with `flow_type: call` (or `async_call` for awaited calls).
4. Also append the target to `invokes_callables` on the source **CallableUnit**.
5. For unresolvable calls (external libraries, dynamic dispatch), create a stub **CallableUnit** with the name and mark it as external.

### Example

```yaml
# Direct method call
call_create_to_validate:
  a: ControlFlow
  name: createOrder_calls_validateOrder
  flow_type: call
  is_conditional: false
  source_callable: create_order
  target_callable: validate_order

# Conditional async call
call_notify_async:
  a: ControlFlow
  name: createOrder_calls_notifyAsync
  flow_type: async_call
  is_conditional: true
  condition: "order.requiresNotification()"
  source_callable: create_order
  target_callable: send_notification

# Update the source callable's invocation list
create_order:
  a: CallableUnit
  # ... (other attributes from sub-phase 2b)
  invokes_callables:
    - validate_order
    - calculate_total
    - save_order
    - send_notification
```

---

## Sub-phase 2f: Data Flow

For each **CallableUnit**, identify which **DataElements** it reads, writes, or transforms, and create **DataFlow** edges.

### Attributes

| Attribute | Range | Rule |
|---|---|---|
| `flow_type` | `DataFlowType` | MUST set. |

### DataFlowType enum

- `read`
- `write`
- `modify`
- `define`
- `use`

### Relationships

| Relationship | Target | Rule |
|---|---|---|
| `has_source_element` | **DataElement** | MUST set (the data being read from or defined). |
| `has_target_element` | **DataElement** | MUST set (the data being written to or consumed). |
| `has_through_callable` | **CallableUnit** | SHOULD set (the callable performing the flow). |
| `has_through_statement` | **Statement** | MAY set for statement-level precision. |

### Bidirectional data links

The extraction agent MUST also populate:

- `CallableUnit.accesses_data_elements` --- data elements the callable reads
- `CallableUnit.modifies_data_elements` --- data elements the callable writes

### Procedure

1. For each **CallableUnit**, perform a lightweight data-flow analysis on its AST body.
2. Identify variable reads (right-hand side of assignments, arguments to calls) and writes (left-hand side of assignments, output parameters).
3. Create a **DataFlow** edge for each read/write/modify relationship.
4. Populate `accesses_data_elements` and `modifies_data_elements` on the **CallableUnit**.

> **Note:** Full data-flow analysis (reaching definitions, def-use chains) is valuable but not required. At minimum, capture direct field reads and writes.

### Example

```yaml
# Reading a field
read_order_total:
  a: DataFlow
  name: createOrder_reads_total
  flow_type: read
  source_element: order_total_field
  target_element: invoice_amount_field
  through_callable: create_order

# Writing a field
write_order_status:
  a: DataFlow
  name: createOrder_writes_status
  flow_type: write
  source_element: status_pending_constant
  target_element: order_status_field
  through_callable: create_order

# Update the callable
create_order:
  a: CallableUnit
  # ... (other attributes)
  accesses_data_elements:
    - order_total_field
    - customer_id_field
  modifies_data_elements:
    - order_status_field
    - order_created_at_field
```

---

## Sub-phase 2g: Annotations

Extract decorators, attributes, annotations, and pragmas attached to code elements.

### Attributes

| Attribute | Range | Rule |
|---|---|---|
| `annotation_syntax` | string | SHOULD set (the raw syntax, e.g., `@Override`, `#[derive(Debug)]`). |
| `parameters` | string[] | SHOULD set for annotation parameters/arguments. |

### Relationships

**Annotation** uses two global (multi-domain) slots:

| Slot | Target | Rule |
|---|---|---|
| `annotates_element` | **EncapsulationUnit** / **CallableUnit** / **DataStructure** / **DataElement** | MUST link to the annotated entity. |
| `affects_behavior_of` | **EncapsulationUnit** / **CallableUnit** | MAY set when the annotation changes runtime behavior. |

The inverse slot on target entities is `annotated_by`.

### Procedure

1. For each **EncapsulationUnit**, **CallableUnit**, **DataStructure**, or **DataElement**, check the AST for attached annotations/decorators.
2. Create an **Annotation** for each, capturing the name and parameters.
3. Link via `annotates_element` to the annotated entity.
4. Mark behavior-affecting annotations (e.g., `@Transactional`, `@Cached`, `@Async`) via `affects_behavior_of`.

### Example

```yaml
# Java annotation
override_annotation:
  a: Annotation
  name: Override
  annotation_syntax: "@Override"
  annotates_element: create_order

# Python decorator with parameters
route_annotation:
  a: Annotation
  name: route
  annotation_syntax: '@app.route("/orders", methods=["POST"])'
  parameters:
    - '"/orders"'
    - 'methods=["POST"]'
  annotates_element: create_order_handler
  affects_behavior_of: create_order_handler

# Rust derive macro
derive_debug:
  a: Annotation
  name: derive
  annotation_syntax: "#[derive(Debug, Clone, Serialize)]"
  parameters:
    - Debug
    - Clone
    - Serialize
  annotates_element: order_struct
```

---

## Sub-phase 2h: Platform-Specific Extensions

This sub-phase is conditional. The extraction agent MUST determine which extensions apply based on the **ProgrammingLanguage** instances from Phase 1, then extract only the relevant ones.

### Decision tree

```
What language/platform?
│
├── COBOL, PL/I, RPG, Assembler (Mainframe)
│   ├── Extract FileDefinition, FileOperation
│   ├── Extract ScreenDefinition, ScreenField
│   ├── Extract JobDefinition, JobStep, DatasetAllocation
│   └── Extract IPCConnection
│
├── C / C++
│   ├── Extract PreprocessorDirective
│   ├── Extract MemoryModel
│   └── Extract OwnershipAnnotation (smart pointers)
│
├── Rust
│   ├── Extract MemoryModel
│   └── Extract OwnershipAnnotation (ownership/lifetimes)
│
├── Any language with macro/metaprogramming
│   └── Extract PreprocessorDirective
│
└── All languages
    ├── Extract ErrorModel (per-module error handling strategy)
    └── Extract ExceptionType (exception hierarchies)
```

### Mainframe extensions

#### FileDefinition and FileOperation

Extract for every COBOL SELECT clause, PL/I DECLARE FILE, or equivalent file declaration.

| Attribute | Description |
|---|---|
| `organization` | File organization: `sequential`, `indexed`, `relative`, `vsam_ksds`, `vsam_esds`, `vsam_rrds`, `partitioned_dataset`, `generation_data_group`, `line_sequential`, `heap` |
| `access_mode` | Access pattern: `sequential_access`, `random_access`, `dynamic_access` |
| `record_format` | Record format: `fixed`, `variable`, `undefined`, `spanned`, `stream` |
| `record_length` | Record length in bytes |
| `key_fields` | Key field names for indexed files |
| `file_status_field` | Variable receiving I/O status codes |
| `external_name` | DD name or physical file name |

Link `file_defined_in_container` to the **CodeContainer** and `used_by_callables` to the **CallableUnits** that perform I/O on the file.

For each I/O verb (READ, WRITE, REWRITE, DELETE, OPEN, CLOSE), create a **FileOperation** linked to the **FileDefinition** via `operates_on_file` and to the **CallableUnit** via `performed_in_callable`.

```yaml
customer_file:
  a: FileDefinition
  name: CUSTOMER-MASTER
  organization: vsam_ksds
  access_mode: random_access
  record_format: fixed
  record_length: 200
  key_fields: [CUSTOMER-ID]
  file_status_field: WS-FILE-STATUS
  external_name: CUSTMAST
  file_defined_in_container: customer_pgm_source

read_customer_op:
  a: FileOperation
  name: READ-CUSTOMER
  operation_type: read
  operates_on_file: customer_file
  performed_in_callable: process_customer_paragraph
```

#### ScreenDefinition and ScreenField

Extract for CICS BMS map definitions, RPG display files, and similar character-mode UIs.

| Attribute | Description |
|---|---|
| `screen_type` | Type of screen (e.g., `bms_map`, `display_file`) |
| `rows` / `columns` | Screen dimensions |
| `external_name` | External map or display file name |

For each field on the screen, create a **ScreenField** with `row`, `column`, `length`, `is_input`, `is_protected`, and `maps_to_data_element` linking to the corresponding **DataElement**.

Link the **ScreenDefinition** to its **EncapsulationUnit** via `program_uses_screens`.

```yaml
inquiry_screen:
  a: ScreenDefinition
  name: CUSTINQ
  screen_type: bms_map
  rows: 24
  columns: 80
  external_name: CUSTMAP
  program_uses_screens:
    - customer_inquiry_program

cust_name_field:
  a: ScreenField
  name: CUST-NAME
  row: 5
  column: 20
  length: 30
  is_input: false
  is_protected: true
  field_on_screen: inquiry_screen
  maps_to_data_element: ws_customer_name
```

#### JobDefinition, JobStep, DatasetAllocation

Extract from JCL members, scheduler definitions, or cron configurations.

- **JobDefinition**: one per JOB card. Set `job_class`, `priority`, `scheduling_info`.
- **JobStep**: one per EXEC statement. Set `step_type`, `program_name`, link `step_executes_program` to the **EncapsulationUnit**.
- **DatasetAllocation**: one per DD statement. Set `dd_name`, `dataset_name`, `disposition`, `record_format`. Link `maps_to_file_definition` to the corresponding **FileDefinition**.

```yaml
payroll_job:
  a: JobDefinition
  name: PAYROLLJ
  job_class: A
  priority: 10
  contains_job_steps:
    - payroll_step1

payroll_step1:
  a: JobStep
  name: CALC
  step_type: exec_pgm
  program_name: PAYROLL-CALC
  step_in_job: payroll_job
  step_executes_program: payroll_calc
  allocates_datasets:
    - emp_file_alloc

emp_file_alloc:
  a: DatasetAllocation
  name: EMPFILE-DD
  dd_name: EMPFILE
  dataset_name: PROD.EMPLOYEE.MASTER
  disposition: shr
  allocated_in_step: payroll_step1
  maps_to_file_definition: employee_master_file
```

#### IPCConnection

Extract for CICS LINK/XCTL, MQ calls, shared memory references, or any inter-program communication.

| Attribute | Description |
|---|---|
| `mechanism` | IPC mechanism (e.g., `cics_link`, `cics_xctl`, `mq_put`, `mq_get`, `shared_memory`, `pipe`, `rmi`, `corba`) |
| `is_synchronous` | Whether the call is synchronous |
| `transaction_scoped` | Whether the IPC participates in a transaction boundary |

Link `has_source_program` and `has_target_program` to **EncapsulationUnit** instances. Link `ipc_passes_data` to the **DataStructure** being exchanged (typically a COMMAREA or message structure).

```yaml
link_to_validation:
  a: IPCConnection
  name: CUSTPGM-LINK-VALPGM
  mechanism: cics_link
  is_synchronous: true
  transaction_scoped: true
  ipc_source_program: customer_inquiry_program
  ipc_target_program: validation_program
  ipc_passes_data:
    - customer_commarea
```

### C/C++ and Rust extensions

#### PreprocessorDirective

Extract for `#include`, `#define`, `#ifdef`, `#pragma`, and similar constructs. Also applies to languages with compile-time metaprogramming (Rust `macro_rules!`, Lisp macros, etc.).

| Attribute | Description |
|---|---|
| `directive_type` | Metaprogramming type (from `MetaprogrammingType` enum) |
| `condition` | Conditional compilation expression (e.g., `#ifdef DEBUG`) |
| `expansion` | Expanded text or transformation result |

Link `directive_defined_in_container` to the **CodeContainer** and `directive_affects_encapsulation_units` / `directive_affects_callables` to the affected entities.

```yaml
debug_guard:
  a: PreprocessorDirective
  name: DEBUG_IFDEF
  directive_type: conditional_compilation
  condition: "defined(DEBUG)"
  directive_defined_in_container: main_c_file
  directive_affects_callables:
    - debug_log_function
```

#### MemoryModel and OwnershipAnnotation

Extract one **MemoryModel** per language or module to describe the memory management strategy.

| Attribute | Description |
|---|---|
| `primary_model` | Ownership model (e.g., `manual`, `garbage_collected`, `reference_counted`, `ownership_borrowing`) |
| `gc_type` | GC algorithm if applicable (e.g., `generational`, `mark_sweep`) |
| `supports_unsafe` | Whether unsafe/manual access is permitted |

For Rust and C++ smart pointers, create **OwnershipAnnotation** instances on individual **DataElements**:

| Attribute | Description |
|---|---|
| `ownership` | Ownership model for this element |
| `lifetime` | Lifetime scope (e.g., `static_lifetime`, `function_scope`, `block_scope`, `named`) |
| `lifetime_name` | Named lifetime identifier (e.g., `'a` in Rust) |

```yaml
rust_memory:
  a: MemoryModel
  name: RustOwnership
  primary_model: ownership_borrowing
  supports_unsafe: true
  modules_using_memory_model:
    - order_service_module

buffer_ownership:
  a: OwnershipAnnotation
  name: buffer_ref
  ownership: ownership_borrowing
  lifetime: named
  lifetime_name: "'a"
  annotates_data_element: buffer_data_element
```

### Error handling extensions (all languages)

#### ErrorModel

Create one **ErrorModel** per error handling paradigm observed in the codebase.

| Attribute | Description |
|---|---|
| `strategy` | Error handling paradigm: `exception_based`, `return_value_based`, `condition_based`, `error_code_based`, `panic_recover`, `monadic` |
| `checkedness` | Exception checkedness: `checked`, `unchecked`, `not_applicable` |

Link `modules_using_error_model` to the **EncapsulationUnit** instances that use this paradigm.

#### ExceptionType

Create an **ExceptionType** for each declared exception or error type in the codebase.

| Attribute | Description |
|---|---|
| `qualified_name` | Fully qualified exception name |
| `is_checked` | Whether this is a checked exception |
| `has_parent_exception` | Parent in the exception hierarchy |

Link `raised_by_callables` and `handled_by_callables` to the relevant **CallableUnit** instances.

```yaml
java_errors:
  a: ErrorModel
  name: JavaExceptions
  strategy: exception_based
  checkedness: checked
  modules_using_error_model:
    - order_service

order_not_found:
  a: ExceptionType
  name: OrderNotFoundException
  qualified_name: com.example.orders.OrderNotFoundException
  is_checked: false
  parent_exception: runtime_exception
  raised_by_callables:
    - find_order_by_id
  handled_by_callables:
    - create_order
```

---

## Phase 2 Checklist

Before proceeding to Phase 3, verify the following:

| Check | How to verify |
|---|---|
| Every **CodeContainer** has been parsed | Count of parsed containers equals count from Phase 1. |
| Every class/module/program has an **EncapsulationUnit** | No top-level AST declarations lack a corresponding unit. |
| Every method/function/paragraph has a **CallableUnit** | No callable AST nodes lack a corresponding unit. |
| Every field/variable has a **DataElement** | Spot-check representative classes for completeness. |
| Every parameter has a **Parameter** | Compare parameter counts against source signatures. |
| Import/include relationships are captured as **DefinitionReferences** | Count of references matches import statement count per container. |
| Call graph (**ControlFlow**) is built | Every **CallableUnit** with call expressions has `invokes_callables` populated. |
| Data flow edges are captured | At minimum, direct field reads/writes are recorded. |
| Annotations are extracted | Spot-check decorated/annotated elements for **Annotation** instances. |
| Platform-specific extensions are populated where applicable | Mainframe: file definitions, screens, JCL. C/C++/Rust: memory model. All: error model. |
| `encapsulation_type` is set on every **EncapsulationUnit** | No unit has a null or missing type. |
| `callable_type` is set on every **CallableUnit** | No callable has a null or missing type. |
| `structure_type` is set on every **DataStructure** | No structure has a null or missing type. |
| `data_type` is set on every **DataElement** | No element has a null or missing type. |

### Common pitfalls

- **Missing nested types.** Inner classes, companion objects, and anonymous classes are easily skipped. Ensure the AST walker recurses into nested type declarations.
- **Unresolved call targets.** Dynamic dispatch, reflection, and dependency injection make call graph construction incomplete. Create stub **CallableUnit** instances for unresolvable targets and annotate them.
- **COBOL hierarchy.** COBOL data items use level numbers (01, 05, 10, etc.) to express hierarchy. Map these to `has_parent_element` / `has_child_elements` rather than flattening.
- **Generic types.** Do not flatten `List<Map<String, Order>>` to a string. Use nested **TypeExpression** instances.
- **Visibility defaults.** Languages have different default visibilities (Java: `package`, Python: `public`, C++: `private` for class members). Apply the correct default when no modifier is present.

---

## Next phase

[Phase 3: Architecture (Layers 2/4)](03-architecture.md) --- infers **System**, **BoundedContext**, **Module**, **Component**, **Service**, and **Interface** from the code structure graph built here.
