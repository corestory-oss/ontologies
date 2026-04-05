# Layer 4: Code-Level Representation

This document defines the SAO v2.0 classes that correspond to **C4 Level 4 (Code)** -- a faithful, close-to-code representation of a software codebase **as written**: source files, their internal structure, and the relationships between code elements. It does not cover architectural abstractions (Components, BoundedContexts), runtime behavior (Deployments, Environments), or operational concerns (Observability, Compliance). The document covers 21 primary classes and 8 supporting classes (29 total).

Two profiles are defined: **Modern** (OOP, functional, and multi-paradigm languages) and **Legacy** (COBOL, RPG, PL/I, Assembler, and other procedural/mainframe languages). The profiles share a common core and diverge where the programming models differ.

---

## Summary

| # | Class | Definition | Modern | Legacy | SAO Section |
|---|---|---|---|---|---|
| 1 | CodeContainer | A physical container of source code -- a file, library member, or other storage unit | Yes | Yes | 12 |
| 2 | StorageLocation | A logical or physical location for storing code containers (directory, PDS library, package) | Yes | Yes | 12 |
| 3 | EncapsulationUnit | A logical boundary grouping related code and data (class, module, program, copybook) | Yes | Yes | 12 |
| 4 | CallableUnit | A named, invocable unit of code (method, function, paragraph, procedure, lambda) | Yes | Yes | 12 |
| 5 | DataStructure | A composite data type grouping related data elements (struct, record, group item, DTO) | Yes | Yes | 12 |
| 6 | DataElement | An individual data field, variable, or constant | Yes | Yes | 12 |
| 7 | Parameter | An input/output parameter for a callable unit | Yes | Yes | 12 |
| 8 | ControlFlow | Control flow between code elements -- calls, branches, jumps | Yes | Yes | 12 |
| 9 | DataFlow | Data flow between code elements -- reads, writes, assignments | Yes | Yes | 12 |
| 10 | TypeExpression | A recursive type model for complex types (generics, unions, pointers, function types) | Yes | -- | 18 |
| 11 | ExceptionType | A declared exception or error type with hierarchy support | Yes | -- | 19 |
| 12 | Operation | A named, invocable unit of behavior exposed via a component's interface (API endpoint) | Yes | -- | 6 |
| 13 | FileDefinition | A file defined for I/O in a program (COBOL SELECT/FD, VSAM dataset) | -- | Yes | 20 |
| 14 | FileOperation | An individual I/O operation on a file (READ, WRITE, REWRITE, DELETE) | -- | Yes | 20 |
| 15 | ScreenDefinition | A terminal screen or map definition (BMS map, RPG display file, MFS format) | -- | Yes | 21 |
| 16 | ScreenField | An individual field on a terminal screen with row/column position | -- | Yes | 21 |
| 17 | JobDefinition | A batch job definition (JCL JOB, scheduler entry) | -- | Yes | 22 |
| 18 | JobStep | A single step within a batch job (JCL EXEC statement) | -- | Yes | 22 |
| 19 | DatasetAllocation | A dataset allocation within a job step (JCL DD statement) | -- | Yes | 22 |
| 20 | IPCConnection | A communication link between two programs or processes (CICS LINK, shared memory, pipes) | -- | Yes | 23 |
| 21 | PreprocessorDirective | A preprocessor directive or metaprogramming construct (COPY REPLACING, #ifdef, macros) | -- | Yes | 24 |
| | **Supporting classes** | | | | |
| 22 | CodeBlock | A logical grouping of statements within a callable unit (conditional, loop, try-catch) | Yes | Yes | 12 |
| 23 | Statement | A single executable instruction or declaration with line number | Yes | Yes | 12 |
| 24 | ProgrammingLanguage | A programming language with paradigms, type discipline, and runtime characteristics | Yes | Yes | 28 |
| 25 | ErrorModel | Describes how a module or language handles errors (exceptions, error codes, monadic, etc.) | Yes | Yes | 19 |
| 26 | MemoryModel | Describes how a language or module manages memory (GC, manual, ownership) | Yes | Yes | 25 |
| 27 | OwnershipAnnotation | An ownership or lifetime annotation on a data element (Rust borrows, C++ smart pointers) | Yes | -- | 25 |
| 28 | PlatformExtension | Abstract base for platform-specific extensions | Yes | Yes | 12 |
| 29 | ExecutionEnvironmentDirective | Platform-specific execution directives (Docker Compose, K8s manifests, Makefiles) | Yes | Yes | 12 |

Primary classes: Modern 12, Legacy 18, Shared core 9. Supporting classes: 8 (shared across both profiles).

---

## Base Class: NamedEntity

All classes in this layer inherit from `NamedEntity`, which provides:

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (LinkML identifier) |
| `name` | string | **Yes** | Human-readable name |
| `description` | string | No | Free-text description |
| `tags` | string[] | No | Arbitrary tags for categorization |
| `metadata` | Metadata | No | Inline metadata (created_at, updated_at, created_by, version) |

`CodeContainer` additionally implements the `Versionable` mixin, which adds `version` (SemanticVersion), `effective_from`, `effective_to`, and `is_current`.

---

## Shared Core (9 classes)

These classes appear in both Modern and Legacy profiles.

### 1. CodeContainer

A physical container of source code -- a file, library member, or other storage unit.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `container_path` | string | **Yes** | Path or identifier for the container |
| `container_type` | CodeContainerType | No | Kind of container (see enum below) |
| `format` | string | No | **Deprecated** -- use `written_in_language` |
| `size_bytes` | integer | No | File size in bytes |
| `line_count` | integer | No | Number of source lines |
| `encoding` | string | No | Character encoding (UTF-8, EBCDIC, etc.) |
| `checksum` | string | No | Content hash for change detection |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_storage_location` | StorageLocation | No | `contains_containers` | Parent directory or library |
| `contains_encapsulation_units` | EncapsulationUnit | Yes | -- | Logical units defined in this file |
| `contains_code_elements` | EncapsulationUnit \| CallableUnit \| DataStructure | Yes | `defined_in_container` | All code elements (global slot) |
| `references_containers` | CodeContainer | Yes | `referenced_by_containers` | Containers this one references |
| `referenced_by_containers` | CodeContainer | Yes | `references_containers` | Containers that reference this one |
| `includes_definitions` | CodeContainer | Yes | `included_in_containers` | Included/copied definitions |
| `included_in_containers` | CodeContainer | Yes | `includes_definitions` | Containers that include this one |
| `has_references` | DefinitionReference | Yes | `referencing_container` | Import/include statements originating here |
| `referenced_via` | DefinitionReference | Yes | `referenced_container` | Import/include statements targeting here |
| `written_in_language` | ProgrammingLanguage | No | `language_used_by_containers` | Programming language |
| `implements_component` | Component | No | `implemented_by_code` | Architectural component (global slot, Layer 2+) |
| `container_file_definitions` | FileDefinition | Yes | `file_defined_in_container` | File I/O definitions (Legacy) |
| `container_screen_definitions` | ScreenDefinition | Yes | `screen_defined_in_container` | Screen definitions (Legacy) |
| `container_preprocessor_directives` | PreprocessorDirective | Yes | `directive_defined_in_container` | Preprocessor directives (Legacy) |

**CodeContainerType Enum:**

| Value | Description | Profile |
|---|---|---|
| `source_file` | Standard source code file | Modern |
| `library_member` | Member of a PDS or library | Legacy |
| `include_file` | Header or shared definitions file | Both |
| `script` | Executable script | Modern |
| `configuration` | Configuration file (Dockerfile, Terraform, CI YAML, etc.) | Modern |
| `schema_definition` | Database or API schema file | Both |
| `notebook_cell` | Jupyter notebook cell | Modern |
| `inline_code` | Embedded code (JS in HTML, SQL in app) | Modern |
| `jcl_member` | JCL member in a PDS | Legacy |
| `rpg_source` | RPG source member | Legacy |
| `pli_source` | PL/I source member | Legacy |
| `assembler_source` | Assembler source member | Legacy |
| `cl_source` | IBM CL (Control Language) source | Legacy |

---

### 2. StorageLocation

A logical or physical location for storing code containers.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `location_path` | string | **Yes** | Path or identifier |
| `location_type` | StorageLocationType | No | Kind of location |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `parent_location` | StorageLocation | No | `contains_locations` | Parent in hierarchy |
| `contains_locations` | StorageLocation | Yes | `parent_location` | Child locations |
| `contains_containers` | CodeContainer | Yes | `contained_in_storage_location` | Code containers in this location |
| `maps_to_module` | Module | No | `mapped_from_directory` | Architectural module (Layer 2+) |

**StorageLocationType Enum:**

| Value | Profile |
|---|---|
| `directory` | Modern |
| `library` | Legacy (PDS, partitioned dataset) |
| `package` | Modern |
| `namespace` | Modern |
| `module_path` | Modern |

---

### 3. EncapsulationUnit

A logical boundary that groups related code and data. This is the cornerstone of SAO's paradigm-agnostic design -- a single class represents Java classes, Python modules, COBOL programs, Haskell modules, and more.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `encapsulation_type` | EncapsulationType | **Yes** | Paradigm-specific type (see enum) |
| `visibility` | VisibilityType | No | Access level (public, private, etc.) |
| `qualified_name` | string | No | Fully qualified name (e.g., `com.example.UserService`) |
| `stereotype` | string | No | Pattern role (Service, Repository, DTO, Controller) |
| `is_abstract` | boolean | No | Whether abstract/incomplete |
| `is_final` | boolean | No | Whether extensible |
| `is_reusable` | boolean | No | Whether designed for reuse |
| `line_start` | integer | No | Starting line in source |
| `line_end` | integer | No | Ending line in source |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `defined_in_container` | CodeContainer | No | `contains_code_elements` | Source file (global slot) |
| `contains_callable_units` | CallableUnit | Yes | `contained_in_unit` | Methods, functions, paragraphs |
| `contains_data_structures` | DataStructure | Yes | -- | Data structures in this unit |
| `contains_data_elements` | DataElement | Yes | -- | Fields/variables (global slot) |
| `extends_units` | EncapsulationUnit | Yes | `extended_by_units` | Inheritance/extension |
| `extended_by_units` | EncapsulationUnit | Yes | `extends_units` | Subclasses |
| `implements_contracts` | Contract | Yes | `implemented_by_units` | Interface implementation |
| `uses_definitions` | DefinitionReference | Yes | -- | Imports/includes used |
| `implements_component` | Component | No | `implemented_by_code` | Architectural link (global slot, Layer 2+) |
| `annotated_by` | Annotation | Yes | `annotates_element` | Annotations/decorators (global slot) |
| `imported_via` | DefinitionReference | Yes | `imports_symbols` | How this unit is imported (global slot) |
| `error_model_for_module` | ErrorModel | No | `modules_using_error_model` | Error handling strategy |
| `memory_model_for_module` | MemoryModel | No | `modules_using_memory_model` | Memory management model |
| `screen_used_by_programs` | ScreenDefinition | Yes | `program_uses_screens` | Terminal screens (Legacy) |
| `outgoing_ipc_connections` | IPCConnection | Yes | `ipc_source_program` | Outbound IPC (Legacy) |
| `incoming_ipc_connections` | IPCConnection | Yes | `ipc_target_program` | Inbound IPC (Legacy) |
| `affected_by_directives` | PreprocessorDirective | Yes | `directive_affects_encapsulation_units` | Preprocessor (Legacy) |
| `executed_by_job_steps` | JobStep | Yes | `step_executes_program` | JCL execution (Legacy) |
| `encapsulation_unit_renders_ui` | UIComponent | No | `ui_implements_encapsulation_unit` | UI component link |

**EncapsulationType Enum (33 values):**

*Object-Oriented (Modern):*

| Value | Description |
|---|---|
| `class` | Standard OOP class |
| `interface` | Interface or contract |
| `abstract_class` | Abstract base class |
| `trait` | Trait (Rust, Scala) or mixin |
| `enum_class` | Enumeration class |
| `record_class` | Immutable record (Java records, C# records) |
| `singleton` | Singleton pattern |

*Procedural / Functional (Modern):*

| Value | Description |
|---|---|
| `program` | Standalone program |
| `subprogram` | Callable subprogram or subroutine library |
| `unit` | Pascal/Delphi unit |
| `module` | Functional module (Haskell, OCaml, F#) |
| `namespace` | Namespace grouping |
| `package` | Package (Ada, Go) |
| `library` | Library module |
| `object` | JavaScript/prototype-based object |

*Web / Application (Modern):*

| Value | Description |
|---|---|
| `component` | UI component (React, Angular, Vue) |
| `service` | Service class |
| `controller` | Controller (MVC pattern) |
| `script` | Script module |
| `composite` | Composite structure |

*Database:*

| Value | Description |
|---|---|
| `stored_procedure` | Database stored procedure package |
| `function_package` | PL/SQL or T-SQL function package |
| `trigger` | Database trigger |
| `view` | Database view definition |

*Mainframe / Legacy:*

| Value | Description |
|---|---|
| `batch_program` | Batch processing program |
| `online_program` | Online transaction program (CICS, IMS) |
| `copybook` | COBOL copybook or include file |
| `rpg_module` | RPG module |
| `rpg_service_program` | RPG service program |
| `pli_procedure` | PL/I external procedure |
| `pli_package` | PL/I package |
| `assembler_csect` | Assembler control section (CSECT) |

| `other` | Catch-all |

---

### 4. CallableUnit

A named, invocable unit of code. Paradigm-agnostic representation of methods, functions, paragraphs, procedures, lambdas, and more.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `callable_type` | CallableType | **Yes** | Paradigm-specific type (see enum) |
| `visibility` | VisibilityType | No | Access level |
| `callable_category` | CallableCategory | No | `normal`, `operator`, or `main_entry` |
| `return_type` | string | No | Return type as string |
| `is_async` | boolean | No | Asynchronous |
| `is_pure` | boolean | No | Pure function (no side effects) |
| `is_static` | boolean | No | Static/class-level |
| `is_virtual` | boolean | No | Virtual/overridable |
| `is_override` | boolean | No | Overrides parent |
| `is_recursive` | boolean | No | Self-referencing |
| `is_inline` | boolean | No | Inline expansion |
| `calling_convention` | string | No | ABI calling convention |
| `line_start` | integer | No | Starting line |
| `line_end` | integer | No | Ending line |
| `entry_point_type` | EntryPointType | No | If this is a program entry point |
| `documentation` | string | No | Docstring or comment |
| `complexity_score` | integer | No | Cyclomatic complexity or similar metric |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_unit` | EncapsulationUnit | No | `contains_callable_units` | Parent unit (global slot) |
| `defined_in_container` | CodeContainer | No | `contains_code_elements` | Source file (global slot) |
| `has_parameters` | Parameter | Yes | `parameter_of` | Parameters |
| `invokes_callables` | CallableUnit | Yes | `invoked_by_callables` | Outbound calls |
| `invoked_by_callables` | CallableUnit | Yes | `invokes_callables` | Inbound callers |
| `accesses_data_elements` | DataElement | Yes | -- | Data read |
| `modifies_data_elements` | DataElement | Yes | -- | Data written |
| `overrides_callable` | CallableUnit | No | `overridden_by_callables` | Overridden parent |
| `overridden_by_callables` | CallableUnit | Yes | `overrides_callable` | Overriding children |
| `contains_blocks` | CodeBlock | Yes | `contained_in_callable` | Nested code blocks |
| `tested_by_cases` | TestCase | Yes | `tests_callable` | Test cases |
| `uses_concurrency_primitives` | ConcurrencyPrimitive | Yes | `used_by_callables` | Locks, semaphores, etc. |
| `annotated_by` | Annotation | Yes | `annotates_element` | Annotations (global slot) |
| `imported_via` | DefinitionReference | Yes | `imports_symbols` | Import reference (global slot) |
| `implements_operation` | Operation | No | `implemented_by_callables` | API operation (Modern) |
| `raises_exception_types` | ExceptionType | Yes | `raised_by_callables` | Exceptions thrown (Modern) |
| `handles_exception_types` | ExceptionType | Yes | `handled_by_callables` | Exceptions caught (Modern) |
| `return_type_expression` | TypeExpression | No | `return_type_of_callables` | Structured return type (Modern) |
| `uses_file_definitions` | FileDefinition | Yes | `used_by_callables` | Files used (Legacy) |
| `callable_file_operations` | FileOperation | Yes | `performed_in_callable` | I/O operations (Legacy) |
| `callable_affected_by_directives` | PreprocessorDirective | Yes | `directive_affects_callables` | Preprocessor (Legacy) |

**CallableType Enum (53 values):**

*Object-Oriented:*

| Value | Description |
|---|---|
| `method` | Instance method |
| `static_method` | Static/class method |
| `constructor` | Object constructor |
| `destructor` | Object destructor |
| `property_getter` | Property getter |
| `property_setter` | Property setter |
| `operator_overload` | Operator overloading |
| `conversion_operator` | Type conversion |
| `indexer` | Indexer/subscript |
| `abstract_method` | Abstract method |
| `virtual_method` | Virtual/overridable method |

*Procedural:*

| Value | Description |
|---|---|
| `function` | Function |
| `procedure` | Procedure/subroutine |
| `subroutine` | Subroutine |
| `paragraph` | COBOL paragraph |
| `section` | COBOL section |
| `rpg_subprocedure` | RPG subprocedure |
| `rpg_subroutine` | RPG subroutine |
| `pli_entry` | PL/I entry point |
| `assembler_entry` | Assembler entry point |

*Functional:*

| Value | Description |
|---|---|
| `lambda` | Anonymous lambda |
| `closure` | Closure |
| `higher_order_function` | Higher-order function |
| `curried_function` | Curried function |
| `functor` | Functor |

*Event Handling:*

| Value | Description |
|---|---|
| `event_handler` | Event handler |
| `callback` | Callback function |
| `delegate` | Delegate |
| `signal_handler` | Signal handler |

*Database:*

| Value | Description |
|---|---|
| `stored_procedure` | Database stored procedure |
| `stored_function` | Database function |
| `trigger_body` | Trigger implementation |
| `cursor` | Database cursor |

*Concurrency:*

| Value | Description |
|---|---|
| `coroutine` | Coroutine |
| `generator` | Generator function |
| `async_function` | Async function |
| `thread_entry` | Thread entry point |
| `task` | Task/future |

*Testing:*

| Value | Description |
|---|---|
| `test_case` | Test case |
| `test_fixture` | Test fixture/setup |
| `mock` | Mock function |

*Other:*

| Value | Description |
|---|---|
| `macro` | Preprocessor macro |
| `template` | Template function (C++) |
| `generic_method` | Generic method |
| `main_entry` | Main entry point |
| `interrupt_handler` | Interrupt handler |
| `exception_handler` | Exception handler |
| `finalizer` | Finalizer/cleanup |
| `factory_method` | Factory method |
| `extension_method` | Extension method |
| `script_function` | Script function |
| `command` | Command/action |
| `other` | Catch-all |

**EntryPointType Enum:**

| Value | Description |
|---|---|
| `main_program` | Main program entry |
| `transaction_entry` | Online transaction entry (CICS) |
| `event_handler` | Event-driven entry |
| `scheduled_entry` | Scheduled/cron entry |
| `api_endpoint` | API endpoint handler |

---

### 5. DataStructure

A composite data type grouping related data elements.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `structure_type` | DataStructureType | **Yes** | Paradigm-specific type (see enum) |
| `structure_category` | DataStructureCategory | No | `composite`, `collection`, `hierarchical`, `value_type`, `reference_type`, `union` |
| `visibility` | VisibilityType | No | Access level |
| `is_mutable` | boolean | No | Mutable or immutable |
| `is_nested` | boolean | No | Whether nested inside another structure |
| `nesting_level` | integer | No | Depth (especially for COBOL level numbers) |
| `is_packed` | boolean | No | Packed/compressed layout |
| `alignment` | integer | No | Memory alignment in bytes |
| `size_bytes` | integer | No | Total size |
| `is_serializable` | boolean | No | Whether serializable |
| `persistence_type` | PersistenceType | No | How persisted (transient, database, file, etc.) |
| `line_start` | integer | No | Starting line |
| `line_end` | integer | No | Ending line |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_unit` | EncapsulationUnit | No | `contains_data_structures` | Parent unit (global slot) |
| `defined_in_container` | CodeContainer | No | `contains_code_elements` | Source file (global slot) |
| `structure_contains_elements` | DataElement | Yes | `contained_in_structure` | Fields in this structure |
| `contains_data_elements` | DataElement | Yes | -- | Fields (global slot) |
| `parent_structure` | DataStructure | No | `child_structures` | Parent (nested structures) |
| `child_structures` | DataStructure | Yes | `parent_structure` | Children (nested structures) |
| `maps_to_domain_entity` | DomainEntity | No | `mapped_from_structure` | Domain entity link (Layer 2+) |
| `maps_to_value_object` | ValueObject | No | `mapped_from_structure_vo` | Value object link (Layer 2+) |
| `persisted_in_collection` | Collection | No | `persists_structures` | Database collection (Layer 2+) |
| `annotated_by` | Annotation | Yes | `annotates_element` | Annotations (global slot) |
| `imported_via` | DefinitionReference | Yes | `imports_symbols` | Import reference (global slot) |
| `passed_via_ipc` | IPCConnection | Yes | `ipc_passes_data` | IPC data passing (Legacy) |

**DataStructureType Enum (50 values):**

*Object-Oriented:*
`class_data`, `inner_class`, `anonymous_class`

*Procedural:*
`struct`, `record`, `union`

*COBOL / Mainframe:*
`group_item`, `copybook_structure`, `commarea`, `linkage_section`, `cobol_file_descriptor`, `rpg_data_structure`, `pli_structure`, `assembler_dsect`

*Functional:*
`algebraic_data_type`, `type_class`, `product_type`, `sum_type`

*Collections:*
`array`, `dynamic_array`, `list`, `dictionary`, `set`, `queue`, `stack`, `tree`, `graph`

*Database:*
`table_structure`, `view_structure`, `cursor_structure`, `rowtype`

*DDD:*
`value_object`, `dto`

*Serialization:*
`json_schema`, `xml_schema`, `protobuf_message`, `avro_record`

*Other:*
`tuple`, `pair`, `enum`, `flags`, `configuration_object`, `message`, `event`, `command`, `smart_pointer`, `reference_wrapper`, `opaque_type`, `variant`, `other`

---

### 6. DataElement

An individual data field, variable, or constant.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `data_type` | string | **Yes** | Data type as string. **Deprecated for typed analysis** -- use `declared_type` |
| `element_category` | DataElementCategory | No | `field`, `static_field`, `local_variable`, `parameter`, `constant`, `global_variable`, `computed`, `temporary` |
| `visibility` | VisibilityType | No | Access level |
| `is_constant` | boolean | No | Constant/final |
| `is_nullable` | boolean | No | Nullable |
| `default_value` | string | No | Default value |
| `size_specification` | string | No | Size/length (e.g., COBOL PIC, array dims) |
| `storage_class` | StorageClass | No | Storage class |
| `classification` | DataClassificationType | No | Data sensitivity (PII, PHI, PCI, etc.) |
| `line_number` | integer | No | Source line number |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_unit` | EncapsulationUnit | No | -- | Parent unit (global slot) |
| `contained_in_structure` | DataStructure | No | `structure_contains_elements` | Parent structure |
| `parent_element` | DataElement | No | `child_elements` | Parent (nested fields) |
| `child_elements` | DataElement | Yes | `parent_element` | Children (nested fields) |
| `maps_to_attribute` | Attribute | No | `mapped_from_element` | Domain attribute (Layer 2+) |
| `annotated_by` | Annotation | Yes | `annotates_element` | Annotations (global slot) |
| `declared_type` | TypeExpression | No | `type_of_data_elements` | Structured type (Modern) |
| `ownership_annotations` | OwnershipAnnotation | Yes | `annotates_data_element` | Ownership (Rust/C++) |
| `mapped_from_screen_fields` | ScreenField | Yes | `maps_to_data_element` | Screen field mapping (Legacy) |
| `protected_by_primitive` | ConcurrencyPrimitive | Yes | `protects_data_elements` | Concurrency guards |

---

### 7. Parameter

An input/output parameter for a callable unit. Inherits from `DataElement` (all DataElement attributes and relationships apply).

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `direction` | ParameterDirection | No | `input`, `output`, `input_output`, `return` |
| `position` | integer | No | Ordinal position in parameter list |
| `passing_mechanism` | PassingMechanism | No | `by_value`, `by_reference`, `by_name`, `by_result` |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `parameter_of` | CallableUnit | No | `has_parameters` | Owning callable |
| `parameter_type` | TypeExpression | No | `type_of_parameters` | Structured type (Modern) |

---

### 8. ControlFlow

Control flow between code elements -- calls, branches, jumps.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `flow_type` | ControlFlowType | No | `call`, `async_call`, `branch`, `jump`, `return`, `throw`, `yield` |
| `is_conditional` | boolean | No | Whether flow depends on a condition |
| `condition` | string | No | Condition expression |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `source_callable` | CallableUnit | No | -- | Calling callable |
| `target_callable` | CallableUnit | No | -- | Called callable |
| `source_statement` | Statement | No | -- | Source statement (fine-grained) |
| `target_statement` | Statement | No | -- | Target statement (fine-grained) |

---

### 9. DataFlow

Data flow between code elements -- reads, writes, assignments.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `flow_type` | DataFlowType | No | `read`, `write`, `modify`, `define`, `use` |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `source_element` | DataElement | No | -- | Data source |
| `target_element` | DataElement | No | -- | Data target |
| `through_callable` | CallableUnit | No | -- | Callable where flow occurs |
| `through_statement` | Statement | No | -- | Statement where flow occurs |

---

## Modern-Only Classes (3 classes)

These classes are included in the Modern profile but not the Legacy profile.

### 10. TypeExpression

A recursive type model for expressing complex types (generics, unions, pointers, function types) across all languages. Replaces flat `data_type` strings.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `type_kind` | TypeKind | **Yes** | Kind of type expression |
| `base_type` | string | No | Base type name (e.g., `List`, `int`, `String`) |
| `type_parameters` | TypeExpression[] | No | Recursive generic parameters (e.g., `T` in `List<T>`) |
| `type_constraints` | string[] | No | Constraints (e.g., `T: Comparable`) |
| `is_nullable` | boolean | No | Whether type permits null |
| `nullability_model` | string | No | How nullability is expressed (`optional`, `nullable`, `Option<T>`) |
| `pointer_semantics` | string | No | Pointer behavior (`raw`, `smart`, `weak`, `unique`) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `type_of_data_elements` | DataElement | Yes | `declared_type` | Elements with this type |
| `type_of_parameters` | Parameter | Yes | `parameter_type` | Parameters with this type |
| `return_type_of_callables` | CallableUnit | Yes | `return_type_expression` | Callables returning this type |

**TypeKind Enum:**

| Value | Description |
|---|---|
| `primitive` | Built-in scalar (int, string, bool) |
| `generic` | Parameterized (List\<T>, Map\<K,V>) |
| `union` | Union (string \| number) |
| `intersection` | Intersection (A & B) |
| `alias` | Named type alias |
| `pointer` | Pointer type (*int, &str) |
| `reference` | Reference type (&T) |
| `array_of` | Array of base type |
| `function_type` | Function signature as type |
| `tuple_type` | Tuple of types |
| `optional_type` | Optional wrapper (Option\<T>, T?) |
| `constrained` | Type with constraints |
| `opaque` | Opaque/unknown |

---

### 11. ExceptionType

A declared exception or error type with hierarchy support.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `qualified_name` | string | No | Fully qualified type name (e.g., `java.io.IOException`) |
| `is_checked` | boolean | No | Whether compiler-enforced |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `parent_exception` | ExceptionType | No | `child_exceptions` | Parent in hierarchy |
| `child_exceptions` | ExceptionType | Yes | `parent_exception` | Children in hierarchy |
| `raised_by_callables` | CallableUnit | Yes | `raises_exception_types` | Callables that throw this |
| `handled_by_callables` | CallableUnit | Yes | `handles_exception_types` | Callables that catch this |

---

### 12. Operation

A named, invocable unit of behavior exposed via an interface. This bridges the code layer to the API surface -- it marks a `CallableUnit` as an externally visible endpoint.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `errors` | string[] | No | Possible error responses |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `exposed_by_component` | Component | No | `exposes_operations` | Component (Layer 2+) |
| `executes_operation_actions` | Action | Yes | `executed_by_operation` | Actions performed (Layer 2+) |
| `accepts_input_schema` | Schema | No | `defines_operation_input` | Input schema |
| `produces_output_schema` | Schema | No | `defines_operation_output` | Output schema |
| `implemented_by_callables` | CallableUnit | Yes | `implements_operation` | Code implementations |
| `offered_on_screens` | Screen | Yes | `offers_operations` | Screens offering this operation |
| `operation_tested_by_cases` | TestCase | Yes | `tests_operation` | Tests |

---

## Legacy-Only Classes (9 classes)

These classes are included in the Legacy profile but not the Modern profile. They model file I/O, terminal screens, batch job control, inter-process communication, and preprocessor constructs that are central to mainframe and procedural codebases.

### 13. FileDefinition

A file defined for I/O in a program -- corresponds to a COBOL `SELECT`/`FD`, VSAM dataset definition, or similar construct.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `organization` | FileOrganization | No | Physical file organization |
| `access_mode` | FileAccessMode | No | How the file is accessed |
| `record_format` | RecordFormat | No | Record format |
| `record_length` | integer | No | Record length in bytes |
| `block_size` | integer | No | Block size in bytes |
| `key_fields` | string[] | No | Key field names (indexed files) |
| `file_status_field` | string | No | Status variable for I/O error detection |
| `external_name` | string | No | External/DD name or system filename |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `used_by_callables` | CallableUnit | Yes | `uses_file_definitions` | Callables that do I/O on this file |
| `file_defined_in_container` | CodeContainer | No | `container_file_definitions` | Source file where defined |
| `persisted_in_store` | DataStore | No | `store_file_definitions` | Backing data store (Layer 2+) |
| `file_operations` | FileOperation | Yes | `operates_on_file` | I/O operations on this file |
| `mapped_from_dataset_allocations` | DatasetAllocation | Yes | `maps_to_file_definition` | JCL DD mappings |

**FileOrganization Enum:**

| Value | Description |
|---|---|
| `sequential` | Sequential file |
| `indexed` | Indexed file (ISAM) |
| `relative` | Relative record file |
| `vsam_ksds` | VSAM Key-Sequenced Data Set |
| `vsam_esds` | VSAM Entry-Sequenced Data Set |
| `vsam_rrds` | VSAM Relative Record Data Set |
| `partitioned_dataset` | Partitioned Data Set (PDS/PDSE) |
| `line_sequential` | Line-sequential text file |
| `generation_data_group` | Generation data group (GDG) |
| `heap` | Heap/unstructured file |

**FileAccessMode Enum:**

| Value | Description |
|---|---|
| `sequential_access` | Records accessed in order |
| `random_access` | Records accessed by key/position |
| `dynamic_access` | Both sequential and random |

**RecordFormat Enum:**

| Value | Description |
|---|---|
| `fixed` | Fixed-length records |
| `variable` | Variable-length records |
| `undefined` | Undefined format |
| `spanned` | Spanned records (across blocks) |
| `stream` | Stream-oriented (no record boundaries) |

---

### 14. FileOperation

An individual I/O operation on a file definition -- a single READ, WRITE, REWRITE, DELETE, etc.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `operation_type` | FileOperationType | **Yes** | The I/O verb |
| `condition_handling` | string | No | Error handling (e.g., `AT END SET EOF TO TRUE`) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `operates_on_file` | FileDefinition | No | `file_operations` | Target file |
| `performed_in_callable` | CallableUnit | No | `callable_file_operations` | Callable performing the I/O |

**FileOperationType Enum:**

| Value | Description |
|---|---|
| `read` | Read a record |
| `write` | Write a new record |
| `rewrite` | Update existing record |
| `delete` | Delete a record |
| `start` | Position for sequential access |
| `open` | Open the file |
| `close` | Close the file |
| `sort` | Sort the file |
| `merge` | Merge files |

---

### 15. ScreenDefinition

A terminal screen or map definition -- BMS maps (CICS), RPG display files, MFS formats, or TUI screens.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `screen_type` | ScreenType | **Yes** | Kind of screen |
| `rows` | integer | No | Number of screen rows |
| `columns` | integer | No | Number of screen columns |
| `external_name` | string | No | External map or display file name |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contains_screen_fields` | ScreenField | Yes | `field_on_screen` | Fields on this screen |
| `program_uses_screens` | EncapsulationUnit | Yes | `screen_used_by_programs` | Programs using this screen |
| `screen_defined_in_container` | CodeContainer | No | `container_screen_definitions` | Source container |

**ScreenType Enum:**

| Value | Description |
|---|---|
| `bms_map` | CICS Basic Mapping Support map |
| `rpg_display_file` | RPG display file (AS/400) |
| `character_terminal` | Generic character terminal |
| `tui` | Text UI (ncurses, etc.) |
| `form_based` | Form-based terminal interaction |

---

### 16. ScreenField

An individual field on a terminal screen definition.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `row` | integer | No | Row position |
| `column` | integer | No | Column position |
| `length` | integer | No | Field length in characters |
| `is_input` | boolean | No | Whether user can type into this field |
| `is_protected` | boolean | No | Whether field is protected from modification |
| `attribute_byte` | string | No | Display attribute (bright, dark, reverse, etc.) |
| `initial_value` | string | No | Default display value |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `field_on_screen` | ScreenDefinition | No | `contains_screen_fields` | Parent screen |
| `maps_to_data_element` | DataElement | No | `mapped_from_screen_fields` | Data element this field maps to |

---

### 17. JobDefinition

A batch job definition -- JCL JOB statement, scheduler entry, or cron job.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `job_class` | string | No | Job class or queue assignment |
| `priority` | integer | No | Execution priority |
| `restart_point` | string | No | Step or checkpoint for restart |
| `scheduling_info` | string | No | Schedule or trigger criteria |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contains_job_steps` | JobStep | Yes | `step_in_job` | Steps within this job |
| `depends_on_jobs` | JobDefinition | Yes | `depended_on_by_jobs` | Upstream job dependencies |
| `depended_on_by_jobs` | JobDefinition | Yes | `depends_on_jobs` | Downstream dependents |

---

### 18. JobStep

A single step within a batch job -- JCL EXEC statement or equivalent.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `step_type` | JobStepType | **Yes** | Kind of step |
| `program_name` | string | No | Program to execute |
| `condition_code` | string | No | Condition code expression (e.g., `COND=(4,LT)`) |
| `region_size` | string | No | Memory region allocation |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `step_in_job` | JobDefinition | No | `contains_job_steps` | Parent job |
| `step_executes_program` | EncapsulationUnit | No | `executed_by_job_steps` | Program executed |
| `allocates_datasets` | DatasetAllocation | Yes | `allocated_in_step` | Dataset allocations (DD statements) |

**JobStepType Enum:**

| Value | Description |
|---|---|
| `exec_program` | Execute a program |
| `exec_proc` | Execute a cataloged or in-stream procedure |
| `utility` | Execute a system utility |
| `sort` | Execute a sort operation |
| `file_transfer` | File transfer step |
| `conditional` | Conditional execution step |

---

### 19. DatasetAllocation

A dataset allocation within a job step -- JCL DD statement or equivalent.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `dd_name` | string | No | DD name (logical file reference) |
| `dataset_name` | string | No | Physical dataset name (DSN) |
| `disposition` | DatasetDisposition | No | Dataset disposition |
| `space_primary` | string | No | Primary space allocation |
| `space_secondary` | string | No | Secondary space allocation |
| `record_format` | RecordFormat | No | Record format (shared enum with FileDefinition) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `allocated_in_step` | JobStep | No | `allocates_datasets` | Parent step |
| `maps_to_file_definition` | FileDefinition | No | `mapped_from_dataset_allocations` | Logical file this DD maps to |

**DatasetDisposition Enum:**

| Value | Description |
|---|---|
| `new_dataset` | Create new |
| `old_dataset` | Exclusive access to existing |
| `shared` | Shared access to existing |
| `modify` | Modify existing |
| `catalog` | Catalog after use |
| `delete_disp` | Delete after use |
| `pass` | Pass to next step |

---

### 20. IPCConnection

A communication link between two programs or processes at runtime.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `mechanism` | IPCMechanism | **Yes** | IPC mechanism used |
| `is_synchronous` | boolean | No | Synchronous or async |
| `transaction_scoped` | boolean | No | Whether IPC participates in a transaction boundary |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `ipc_source_program` | EncapsulationUnit | No | `outgoing_ipc_connections` | Calling program |
| `ipc_target_program` | EncapsulationUnit | No | `incoming_ipc_connections` | Called program |
| `ipc_passes_data` | DataStructure | Yes | `passed_via_ipc` | Data structures passed |

**IPCMechanism Enum:**

| Value | Description |
|---|---|
| `cics_link` | CICS LINK (call with return) |
| `cics_xctl` | CICS XCTL (transfer, no return) |
| `ims_schedule` | IMS message scheduling |
| `shared_memory` | Shared memory segment |
| `pipe` | Unix pipe |
| `rmi` | Java RMI |
| `corba` | CORBA IIOP |
| `database_mediated` | Communication via shared database |
| `message_queue` | Message queue (MQ Series, etc.) |
| `socket` | TCP/UDP socket |
| `named_pipe` | Named pipe / FIFO |
| `signal` | Unix signal |
| `semaphore` | Semaphore-based synchronization |
| `dcom` | Distributed COM |
| `rest_call` | REST API call between processes |

---

### 21. PreprocessorDirective

A preprocessor directive, macro, or metaprogramming construct that modifies code before or during compilation.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `directive_type` | MetaprogrammingType | **Yes** | Kind of directive |
| `condition` | string | No | Conditional expression (e.g., `#ifdef DEBUG`) |
| `expansion` | string | No | Expanded or generated code |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `directive_defined_in_container` | CodeContainer | No | `container_preprocessor_directives` | Source container |
| `directive_affects_encapsulation_units` | EncapsulationUnit | Yes | `affected_by_directives` | Units affected |
| `directive_affects_callables` | CallableUnit | Yes | `callable_affected_by_directives` | Callables affected |

**MetaprogrammingType Enum:**

| Value | Description |
|---|---|
| `c_preprocessor` | C/C++ preprocessor (#define, #ifdef) |
| `rust_macro_declarative` | Rust macro_rules! |
| `rust_macro_procedural` | Rust procedural macros (derive, attribute) |
| `cobol_copy_replacing` | COBOL COPY ... REPLACING |
| `template_metaprogramming` | C++ template metaprogramming |
| `python_metaclass` | Python metaclass |
| `lisp_macro` | Lisp macro |
| `java_annotation_processor` | Java annotation processor |
| `code_generator` | External code generator |

---

## Shared Supporting Enums

These enums are used across both profiles.

**VisibilityType:** `public`, `private`, `protected`, `internal`, `package`

**CallableCategory:** `normal`, `operator`, `main_entry`

**DataElementCategory:** `field`, `static_field`, `local_variable`, `parameter`, `constant`, `global_variable`, `computed`, `temporary`

**ParameterDirection:** `input`, `output`, `input_output`, `return`

**PassingMechanism:** `by_value`, `by_reference`, `by_name`, `by_result`

**ControlFlowType:** `call`, `async_call`, `branch`, `jump`, `return`, `throw`, `yield`

**DataFlowType:** `read`, `write`, `modify`, `define`, `use`

**CodeBlockType:** `sequential`, `conditional`, `loop`, `try_catch`, `transaction`, `critical_section`, `scope`

**StatementCategory:** `declaration`, `assignment`, `invocation`, `control_transfer`, `io_operation`, `data_manipulation`, `transaction_control`, `exception_handling`

**ReferenceType:** `import_module`, `import_symbol`, `include_source`, `inherit`, `implement`

---

## Relationship Map

The following diagram summarizes how the 21 classes in this layer connect to each other. Arrows indicate the direction of the relationship; labels are the attribute name on the source class.

```
StorageLocation
  └── contains_containers ──> CodeContainer
                                 ├── contains_code_elements ──> EncapsulationUnit
                                 │                                 ├── contains_callable_units ──> CallableUnit
                                 │                                 │     ├── has_parameters ──> Parameter
                                 │                                 │     ├── invokes_callables ──> CallableUnit
                                 │                                 │     ├── accesses_data_elements ──> DataElement
                                 │                                 │     ├── modifies_data_elements ──> DataElement
                                 │                                 │     ├── implements_operation ──> Operation [Modern]
                                 │                                 │     ├── raises_exception_types ──> ExceptionType [Modern]
                                 │                                 │     ├── handles_exception_types ──> ExceptionType [Modern]
                                 │                                 │     ├── return_type_expression ──> TypeExpression [Modern]
                                 │                                 │     ├── uses_file_definitions ──> FileDefinition [Legacy]
                                 │                                 │     └── callable_file_operations ──> FileOperation [Legacy]
                                 │                                 │
                                 │                                 ├── contains_data_structures ──> DataStructure
                                 │                                 │     ├── structure_contains_elements ──> DataElement
                                 │                                 │     │     ├── declared_type ──> TypeExpression [Modern]
                                 │                                 │     │     └── mapped_from_screen_fields ──> ScreenField [Legacy]
                                 │                                 │     └── passed_via_ipc ──> IPCConnection [Legacy]
                                 │                                 │
                                 │                                 ├── screen_used_by_programs ──> ScreenDefinition [Legacy]
                                 │                                 │     └── contains_screen_fields ──> ScreenField [Legacy]
                                 │                                 │
                                 │                                 ├── outgoing_ipc_connections ──> IPCConnection [Legacy]
                                 │                                 ├── affected_by_directives ──> PreprocessorDirective [Legacy]
                                 │                                 └── executed_by_job_steps ──> JobStep [Legacy]
                                 │
                                 ├── container_file_definitions ──> FileDefinition [Legacy]
                                 │     ├── file_operations ──> FileOperation [Legacy]
                                 │     └── mapped_from_dataset_allocations ──> DatasetAllocation [Legacy]
                                 │
                                 ├── container_screen_definitions ──> ScreenDefinition [Legacy]
                                 ├── container_preprocessor_directives ──> PreprocessorDirective [Legacy]
                                 └── written_in_language ──> ProgrammingLanguage

ControlFlow
  ├── source_callable ──> CallableUnit
  └── target_callable ──> CallableUnit

DataFlow
  ├── source_element ──> DataElement
  ├── target_element ──> DataElement
  └── through_callable ──> CallableUnit

JobDefinition [Legacy]
  ├── contains_job_steps ──> JobStep
  │     ├── step_executes_program ──> EncapsulationUnit
  │     └── allocates_datasets ──> DatasetAllocation
  │           └── maps_to_file_definition ──> FileDefinition
  └── depends_on_jobs ──> JobDefinition
```

---

## Supporting Classes (8 classes)

These classes support the primary Layer 4 classes but were not included in the original minimal set. They provide code semantics (blocks, statements), language metadata, error/memory models, and platform extensions.

### 22. CodeBlock

A logical grouping of statements within a callable unit -- conditionals, loops, try-catch blocks, synchronized sections.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `block_type` | CodeBlockType | No | Kind of block |
| `line_start` | integer | No | Starting line |
| `line_end` | integer | No | Ending line |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_callable` | CallableUnit | No | `contains_blocks` | Parent callable |
| `contains_statements` | Statement | Yes | `contained_in_block` | Statements in this block |
| `parent_block` | CodeBlock | No | `child_blocks` | Parent block (nesting) |
| `child_blocks` | CodeBlock | Yes | `parent_block` | Child blocks (nesting) |

**CodeBlockType Enum:** `sequential`, `conditional`, `loop`, `try_catch`, `transaction`, `critical_section`, `scope`

---

### 23. Statement

A single executable instruction or declaration.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `statement_category` | StatementCategory | No | Kind of statement |
| `line_number` | integer | No | Source line number |
| `is_conditional` | boolean | No | Whether conditional |
| `text` | string | No | Source text of statement |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_block` | CodeBlock | No | `contains_statements` | Parent block |
| `operates_on_elements` | DataElement | Yes | -- | Data elements operated on |
| `invokes_callable` | CallableUnit | No | -- | Callable invoked |
| `transfers_control_to` | Statement | No | -- | Control transfer target |

**StatementCategory Enum:** `declaration`, `assignment`, `invocation`, `control_transfer`, `io_operation`, `data_manipulation`, `transaction_control`, `exception_handling`

---

### 24. ProgrammingLanguage

A programming language modeled as a first-class entity, replacing bare string fields. Enables structured cross-language analysis.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `paradigms` | ProgrammingParadigm[] | No | Supported paradigms |
| `type_discipline` | string | No | Type system (e.g., `static_strong`, `dynamic_weak`) |
| `has_preprocessor` | boolean | No | Whether the language has a preprocessor |
| `has_gc` | boolean | No | Whether the language has garbage collection |
| `year_introduced` | integer | No | Year first released |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `language_used_by_containers` | CodeContainer | Yes | `written_in_language` | Code containers written in this language |
| `default_error_model` | ErrorModel | No | `error_model_for_languages` | Default error handling model |
| `default_memory_model` | MemoryModel | No | `memory_model_for_languages` | Default memory management model |

**ProgrammingParadigm Enum:** `object_oriented`, `procedural`, `functional`, `logic`, `concatenative`, `data_driven`, `multi_paradigm`

---

### 25. ErrorModel

Describes how a module or language handles errors.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `strategy` | ErrorHandlingStrategy | **Yes** | Error handling paradigm |
| `checkedness` | ExceptionCheckedness | No | Whether exceptions are checked or unchecked |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `modules_using_error_model` | EncapsulationUnit | Yes | `error_model_for_module` | Modules using this model |
| `error_model_for_languages` | ProgrammingLanguage | Yes | `default_error_model` | Languages using this as default |

**ErrorHandlingStrategy Enum:** `exception_based`, `return_value_based`, `condition_based`, `error_code_based`, `panic_recover`, `monadic`

**ExceptionCheckedness Enum:** `checked`, `unchecked`, `not_applicable`

---

### 26. MemoryModel

Describes the memory management strategy for a module or language.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `primary_model` | OwnershipModel | **Yes** | Primary memory management approach |
| `gc_type` | string | No | GC algorithm (e.g., `generational`, `mark-sweep`) |
| `supports_unsafe` | boolean | No | Whether unsafe/manual memory access is allowed |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `modules_using_memory_model` | EncapsulationUnit | Yes | `memory_model_for_module` | Modules using this model |
| `memory_model_for_languages` | ProgrammingLanguage | Yes | `default_memory_model` | Languages using this as default |

**OwnershipModel Enum:** `owned`, `borrowed_shared`, `borrowed_mutable`, `moved`, `copied`, `reference_counted`, `garbage_collected`, `manual`, `stack_allocated`

---

### 27. OwnershipAnnotation

An ownership or lifetime annotation on a specific data element. Primarily for Rust and C++ codebases.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `ownership` | OwnershipModel | **Yes** | Ownership model for this element |
| `lifetime` | LifetimeScope | No | Lifetime scope |
| `lifetime_name` | string | No | Named lifetime identifier (e.g., `'a` in Rust) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `annotates_data_element` | DataElement | No | `ownership_annotations` | Data element this applies to |

**LifetimeScope Enum:** `static_lifetime`, `function_scope`, `block_scope`, `named_lifetime`, `heap_lifetime`

---

### 28. PlatformExtension (abstract)

Abstract base class for platform-specific extensions.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `platform` | string | No | Platform identifier |

---

### 29. ExecutionEnvironmentDirective

Platform-specific execution directives -- Docker Compose, Kubernetes manifests, Makefiles, shell scripts, and build files.

**Inherits from:** PlatformExtension (adds `platform` attribute)

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `directive_type` | string | No | Type of directive |
| `configuration` | string | No | Configuration content |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `orchestrates_units` | EncapsulationUnit | Yes | -- | Units orchestrated |
| `defines_execution_order` | CallableUnit | Yes | -- | Execution ordering |
| `allocates_resources` | Infrastructure | Yes | -- | Resources allocated (Layer 2) |
