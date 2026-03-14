# Extended Modeling (Sections 18-28)

This document covers the extended modeling sections introduced in SAO v2.0.0. These sections extend the ontology to represent any software application -- legacy (COBOL, RPG, Assembler, PL/I), recent legacy (C#, Java), and modern (Python, Go, Rust).

> **v2.0 Note**: Sections 18-28 are entirely new in SAO v2.0.0. They introduce first-class modeling for type systems, error handling, file I/O, screen definitions, batch orchestration, inter-process communication, preprocessor constructs, memory models, domain relationships, database schema objects, and programming languages. Several of these sections deprecate older string-based attributes in favor of typed object references.

## Overview

The extended modeling sections address capabilities that were either implicit or absent in SAO v1.x:

1. **Type System Modeling** (Section 18) - Recursive type expressions for generics, unions, pointers, and function types
2. **Error Handling Model** (Section 19) - Language-level error handling paradigms
3. **File I/O Definitions** (Section 20) - File-based I/O for COBOL, VSAM, and general file processing
4. **Screen/Terminal Interaction** (Section 21) - Character-mode UI for CICS BMS maps, RPG display files, and TUI applications
5. **Job Control / Batch Orchestration** (Section 22) - JCL, schedulers, and batch workflows
6. **Inter-Process Communication** (Section 23) - CICS LINK/XCTL, shared memory, pipes, RMI, CORBA
7. **Preprocessor / Metaprogramming** (Section 24) - Preprocessor directives, macros, and metaprogramming constructs
8. **Memory / Ownership Model** (Section 25) - Rust ownership, garbage collection, manual memory management
9. **Domain Entity Relationships** (Section 26) - Named, typed relationships between domain entities
10. **Database Schema Objects** (Section 27) - Constraints and indexes for migration and impact analysis
11. **Programming Language as First-Class Entity** (Section 28) - Queryable language entity replacing bare strings

---

## Section 18: Type System Modeling

Provides recursive type modeling for expressing complex types across all languages.

### TypeExpression

**Definition**: A recursive type expression that models generics (`List<T>`), unions (`string | number`), pointers (`*int`), function types (`fn(int) -> bool`), and other composite types.

**Purpose**: Replaces flat `data_type` strings with structured, queryable type information. Enables cross-language type analysis and compatibility checking.

**Key Attributes**:
- Inherits from `NamedEntity`
- **type_kind** (TypeKind, required): The kind of type expression
- **base_type** (string): The base type name (e.g., `List`, `int`, `String`)
- **type_parameters** (TypeExpression[]): Self-referential list for generics (e.g., the `String` in `List<String>`)
- **type_constraints** (string[]): Constraints on the type (e.g., `T: Comparable`)
- **is_nullable** (boolean): Whether the type permits null values
- **nullability_model** (string): The nullability system (e.g., `option_type`, `nullable_annotation`, `implicit`)
- **pointer_semantics** (string): Pointer behavior (e.g., `raw`, `smart`, `weak`, `unique`)

**Relationships**:
- **type_of_data_elements** <-> `DataElement.declared_type`: Data elements that have this type
- **type_of_parameters** <-> `Parameter.parameter_type`: Parameters that have this type
- **return_type_of_callables** <-> `CallableUnit.return_type_expression`: Callables that return this type

**Deprecation Note**: For typed analysis, `TypeExpression` replaces the `data_type` (string) attribute on `DataElement` and `Parameter`. The string attribute is retained for backward compatibility but should not be used for new models.

**Example - Java Generic Type:**
```yaml
list_of_string:
  a: TypeExpression
  name: "List<String>"
  type_kind: generic
  base_type: List
  type_parameters:
    - a: TypeExpression
      name: String
      type_kind: primitive
      base_type: String
```

**Example - Rust Function Type:**
```yaml
predicate_fn:
  a: TypeExpression
  name: "fn(i32) -> bool"
  type_kind: function_type
  base_type: fn
  type_parameters:
    - a: TypeExpression
      name: i32
      type_kind: primitive
      base_type: i32
  is_nullable: false
```

**Example - TypeScript Union:**
```yaml
string_or_number:
  a: TypeExpression
  name: "string | number"
  type_kind: union
  type_parameters:
    - a: TypeExpression
      type_kind: primitive
      base_type: string
    - a: TypeExpression
      type_kind: primitive
      base_type: number
```

### TypeKind Enum

| Value | Description |
|---|---|
| `primitive` | Built-in scalar type (int, string, bool) |
| `generic` | Parameterized type (List<T>, Map<K,V>) |
| `union` | Union of types (string \| number) |
| `intersection` | Intersection of types (A & B) |
| `alias` | Named type alias |
| `pointer` | Pointer type (*int, &str) |
| `reference` | Reference type (&T, ref T) |
| `array_of` | Array of a base type |
| `function_type` | Function signature as a type |
| `tuple_type` | Tuple of types |
| `optional_type` | Optional/nullable wrapper (Option<T>, T?) |
| `constrained` | Type with constraints (T: Comparable) |
| `opaque` | Opaque/unknown type |

---

## Section 19: Error Handling Model

Models language-level error handling paradigms.

### ErrorModel

**Definition**: Describes how a module or language handles errors.

**Purpose**: Enables cross-language comparison of error handling strategies and identification of mixed paradigms within a codebase.

**Key Attributes**:
- Inherits from `NamedEntity`
- **strategy** (ErrorHandlingStrategy, required): The error handling paradigm used
- **checkedness** (ExceptionCheckedness): Whether exceptions are checked or unchecked

**Relationships**:
- **modules_using_error_model** <-> `EncapsulationUnit.error_model_for_module`: Modules that use this error model
- **error_model_for_languages** <-> `ProgrammingLanguage.default_error_model`: Languages that use this as their default error model

**Example:**
```yaml
java_error_model:
  a: ErrorModel
  name: JavaExceptionModel
  strategy: exception_based
  checkedness: checked

rust_error_model:
  a: ErrorModel
  name: RustResultModel
  strategy: return_value_based
  checkedness: not_applicable
```

---

### ExceptionType

**Definition**: A declared exception or error type with hierarchy support.

**Purpose**: Models exception class hierarchies and connects them to the callables that raise or handle them.

**Key Attributes**:
- Inherits from `NamedEntity`
- **qualified_name** (string): Fully qualified exception name (e.g., `java.io.IOException`)
- **is_checked** (boolean): Whether this is a checked exception
- **parent_exception** (ExceptionType, self-ref): Parent in the exception hierarchy
- **child_exceptions** (ExceptionType[], self-ref): Children in the exception hierarchy

**Relationships**:
- **raised_by_callables** <-> `CallableUnit.raises_exception_types`: Callables that may raise this exception
- **handled_by_callables** <-> `CallableUnit.handles_exception_types`: Callables that handle this exception

**Deprecation Note**: `ExceptionType` replaces the `raises_exceptions` (string[]) and `handles_exceptions` (string[]) attributes on `CallableUnit`.

**Example:**
```yaml
io_exception:
  a: ExceptionType
  name: IOException
  qualified_name: java.io.IOException
  is_checked: true
  parent_exception: java_exception

file_not_found:
  a: ExceptionType
  name: FileNotFoundException
  qualified_name: java.io.FileNotFoundException
  is_checked: true
  parent_exception: io_exception
```

### ErrorHandlingStrategy Enum

| Value | Description |
|---|---|
| `exception_based` | Try/catch exception handling (Java, Python, C#) |
| `return_value_based` | Result/Either return types (Rust, Go) |
| `condition_based` | Condition system (Common Lisp) |
| `error_code_based` | Numeric error codes (C, COBOL) |
| `panic_recover` | Panic and recover mechanism (Go) |
| `monadic` | Monadic error handling (Haskell) |

### ExceptionCheckedness Enum

| Value | Description |
|---|---|
| `checked` | Compiler-enforced handling (Java checked exceptions) |
| `unchecked` | Runtime-only, not enforced (Python, C#, Java unchecked) |
| `not_applicable` | Language does not use exception-based error handling |

---

## Section 20: File I/O Definitions

Models file-based I/O for COBOL, mainframe VSAM, and general file processing systems.

### FileDefinition

**Definition**: A file defined for I/O operations, corresponding to a COBOL SELECT clause, a C `fopen` target, or similar constructs.

**Purpose**: Captures the physical and logical characteristics of files used by programs, enabling impact analysis when file structures change.

**Key Attributes**:
- Inherits from `NamedEntity`
- **organization** (FileOrganization): Physical organization of the file
- **access_mode** (FileAccessMode): How the file is accessed
- **record_format** (RecordFormat): Record format
- **record_length** (int): Record length in bytes
- **block_size** (int): Block size in bytes
- **key_fields** (string[]): Key field names for indexed files
- **file_status_field** (string): Status field for error detection
- **external_name** (string): External/DD name or system filename

**Relationships**:
- **used_by_callables** <-> `CallableUnit`: Callables that perform I/O on this file
- **file_defined_in_container** <-> `CodeContainer`: Container where this file is defined
- **persisted_in_store** <-> `DataStore`: Data store backing this file
- **file_operations** <-> `FileOperation`: Operations performed on this file
- **mapped_from_dataset_allocations** <-> `DatasetAllocation`: JCL dataset allocations that map to this file

**Example - COBOL File:**
```yaml
customer_master:
  a: FileDefinition
  name: CUSTOMER-MASTER
  organization: vsam_ksds
  access_mode: random_access
  record_format: fixed
  record_length: 200
  key_fields: [CUSTOMER-ID]
  file_status_field: WS-FILE-STATUS
  external_name: CUSTMAST
  file_defined_in_container: customer_program_source
```

**Example - C File:**
```yaml
log_file:
  a: FileDefinition
  name: application_log
  organization: sequential
  access_mode: sequential_access
  record_format: stream
  external_name: /var/log/app.log
```

---

### FileOperation

**Definition**: An individual I/O operation performed on a file.

**Key Attributes**:
- Inherits from `NamedEntity`
- **operation_type** (FileOperationType, required): The type of I/O operation
- **condition_handling** (string): Error handling approach for this operation

**Relationships**:
- **operates_on_file** <-> `FileDefinition`: The file being operated on
- **performed_in_callable** <-> `CallableUnit`: The callable performing the operation

**Example:**
```yaml
read_customer:
  a: FileOperation
  name: READ-CUSTOMER-RECORD
  operation_type: read
  condition_handling: "AT END SET END-OF-FILE TO TRUE"
  operates_on_file: customer_master
  performed_in_callable: process_customers_paragraph
```

### FileOrganization Enum

| Value | Description |
|---|---|
| `sequential` | Sequential file |
| `indexed` | Indexed file (ISAM) |
| `relative` | Relative record file |
| `vsam_ksds` | VSAM Key-Sequenced Data Set |
| `vsam_esds` | VSAM Entry-Sequenced Data Set |
| `vsam_rrds` | VSAM Relative Record Data Set |
| `partitioned` | Partitioned Data Set (PDS/PDSE) |
| `line_sequential` | Line-sequential text file |
| `heap` | Heap/unstructured file |

### FileAccessMode Enum

| Value | Description |
|---|---|
| `sequential_access` | Records accessed in order |
| `random_access` | Records accessed by key or position |
| `dynamic_access` | Both sequential and random access |

### RecordFormat Enum

| Value | Description |
|---|---|
| `fixed` | Fixed-length records |
| `variable` | Variable-length records |
| `undefined` | Undefined record format |
| `spanned` | Spanned records (across blocks) |
| `stream` | Stream-oriented (no record boundaries) |

### FileOperationType Enum

| Value | Description |
|---|---|
| `read` | Read a record |
| `write` | Write a new record |
| `rewrite` | Update an existing record |
| `delete` | Delete a record |
| `start` | Position for sequential access |
| `open` | Open the file |
| `close` | Close the file |
| `sort` | Sort the file |
| `merge` | Merge files |

---

## Section 21: Screen/Terminal Interaction

Models character-mode UI definitions for CICS BMS maps, RPG display files, and TUI applications.

### ScreenDefinition

**Definition**: A screen or terminal map definition.

**Purpose**: Captures the layout and structure of character-mode user interfaces, enabling UI-to-program traceability and modernization analysis.

**Key Attributes**:
- Inherits from `NamedEntity`
- **screen_type** (ScreenType, required): The type of screen definition
- **rows** (int): Number of screen rows
- **columns** (int): Number of screen columns
- **external_name** (string): External map or display file name

**Relationships**:
- **contains_screen_fields** <-> `ScreenField`: Fields defined on this screen
- **program_uses_screens** <-> `EncapsulationUnit`: Programs that use this screen
- **screen_defined_in_container** <-> `CodeContainer`: Container where this screen is defined

**Example - CICS BMS Map:**
```yaml
customer_inquiry_map:
  a: ScreenDefinition
  name: CUSTINQ
  screen_type: bms_map
  rows: 24
  columns: 80
  external_name: CUSTMAP
```

---

### ScreenField

**Definition**: An individual field on a screen definition.

**Key Attributes**:
- Inherits from `NamedEntity`
- **row** (int): Row position on screen
- **column** (int): Column position on screen
- **length** (int): Field length in characters
- **is_input** (boolean): Whether the user can type into this field
- **is_protected** (boolean): Whether the field is protected from modification
- **attribute_byte** (string): Display attribute (e.g., bright, dark, reverse)
- **initial_value** (string): Default display value

**Relationships**:
- **field_on_screen** <-> `ScreenDefinition`: The screen this field belongs to
- **maps_to_data_element** <-> `DataElement`: Data element mapped to this field

**Example:**
```yaml
customer_name_field:
  a: ScreenField
  name: CUST-NAME
  row: 5
  column: 20
  length: 30
  is_input: false
  is_protected: true
  attribute_byte: bright
  field_on_screen: customer_inquiry_map
  maps_to_data_element: customer_name_element
```

### ScreenType Enum

| Value | Description |
|---|---|
| `bms_map` | CICS Basic Mapping Support map |
| `rpg_display_file` | RPG display file (AS/400) |
| `character_terminal` | Generic character terminal screen |
| `tui` | Text User Interface (ncurses, etc.) |
| `form_based` | Form-based terminal interaction |

---

## Section 22: Job Control / Batch Orchestration

Models batch job definitions for JCL, schedulers, and batch workflows.

### JobDefinition

**Definition**: A batch job definition, such as a JCL job or scheduler entry.

**Purpose**: Captures the structure and dependencies of batch workflows, enabling scheduling analysis and restart planning.

**Key Attributes**:
- Inherits from `NamedEntity`
- **job_class** (string): Job class or queue assignment
- **priority** (int): Execution priority
- **restart_point** (string): Step to restart from on failure
- **scheduling_info** (string): Scheduling metadata (cron, calendar, etc.)

**Relationships**:
- **contains_job_steps** <-> `JobStep`: Steps within this job
- **depends_on_jobs** (self-ref): Jobs that must complete before this one
- **depended_on_by_jobs** (self-ref): Jobs that depend on this one

**Example:**
```yaml
daily_payroll_job:
  a: JobDefinition
  name: PAYROLL
  job_class: A
  priority: 10
  restart_point: STEP030
  scheduling_info: "Daily 06:00 EST, business days only"
  depends_on_jobs: [hr_extract_job]
```

---

### JobStep

**Definition**: A single step within a batch job.

**Key Attributes**:
- Inherits from `NamedEntity`
- **step_type** (JobStepType, required): The type of step
- **program_name** (string): Name of the program to execute
- **condition_code** (string): Condition code expression for step execution
- **region_size** (string): Memory region allocation

**Relationships**:
- **step_in_job** <-> `JobDefinition`: The job containing this step
- **step_executes_program** <-> `EncapsulationUnit`: The program executed by this step
- **allocates_datasets** <-> `DatasetAllocation`: Datasets allocated for this step

**Example:**
```yaml
payroll_calc_step:
  a: JobStep
  name: STEP010
  step_type: exec_program
  program_name: PAYCALC
  condition_code: "COND=(4,LT)"
  region_size: 4M
  step_in_job: daily_payroll_job
  step_executes_program: payroll_calc_program
```

---

### DatasetAllocation

**Definition**: A dataset allocation within a job step (JCL DD statement or equivalent).

**Key Attributes**:
- Inherits from `NamedEntity`
- **dd_name** (string): DD name (logical file reference)
- **dataset_name** (string): Physical dataset name
- **disposition** (DatasetDisposition): Dataset disposition
- **space_primary** (string): Primary space allocation
- **space_secondary** (string): Secondary space allocation
- **record_format** (RecordFormat): Record format (shared enum with Section 20)

**Relationships**:
- **allocated_in_step** <-> `JobStep`: The step where this allocation occurs
- **maps_to_file_definition** <-> `FileDefinition`: The file definition this allocation maps to

**Example:**
```yaml
customer_file_alloc:
  a: DatasetAllocation
  name: CUSTDD
  dd_name: CUSTMAST
  dataset_name: PROD.CUSTOMER.MASTER
  disposition: old_dataset
  record_format: fixed
  allocated_in_step: payroll_calc_step
  maps_to_file_definition: customer_master
```

### JobStepType Enum

| Value | Description |
|---|---|
| `exec_program` | Execute a program |
| `exec_proc` | Execute a cataloged or in-stream procedure |
| `utility` | Execute a system utility |
| `sort` | Execute a sort operation |
| `file_transfer` | File transfer step |
| `conditional` | Conditional execution step |

### DatasetDisposition Enum

| Value | Description |
|---|---|
| `new_dataset` | Create a new dataset |
| `old_dataset` | Exclusive access to existing dataset |
| `shared` | Shared access to existing dataset |
| `modify` | Modify an existing dataset |
| `catalog` | Catalog the dataset after use |
| `delete_disp` | Delete the dataset after use |
| `pass` | Pass the dataset to the next step |

---

## Section 23: Inter-Process Communication

Models IPC mechanisms including CICS LINK/XCTL, shared memory, pipes, RMI, CORBA, and more.

### IPCConnection

**Definition**: A connection between two programs via an inter-process communication mechanism.

**Purpose**: Captures how programs communicate at runtime, enabling dependency analysis across process boundaries.

**Key Attributes**:
- Inherits from `NamedEntity`
- **mechanism** (IPCMechanism, required): The IPC mechanism used
- **is_synchronous** (boolean): Whether the communication is synchronous
- **transaction_scoped** (boolean): Whether the communication participates in a transaction

**Relationships**:
- **ipc_source_program** / **outgoing_ipc_connections** <-> `EncapsulationUnit`: The program initiating the communication
- **ipc_target_program** / **incoming_ipc_connections** <-> `EncapsulationUnit`: The program receiving the communication
- **ipc_passes_data** / **passed_via_ipc** <-> `DataStructure`: Data structures passed between programs

**Example - CICS Program Link:**
```yaml
cics_customer_lookup:
  a: IPCConnection
  name: CUSTLOOKUP-LINK
  mechanism: cics_link
  is_synchronous: true
  transaction_scoped: true
  ipc_source_program: order_entry_program
  ipc_target_program: customer_lookup_program
  ipc_passes_data: customer_commarea
```

**Example - Unix Pipe:**
```yaml
log_pipeline:
  a: IPCConnection
  name: log-filter-pipe
  mechanism: pipe
  is_synchronous: true
  transaction_scoped: false
  ipc_source_program: log_generator
  ipc_target_program: log_filter
```

### IPCMechanism Enum

| Value | Description |
|---|---|
| `cics_link` | CICS LINK (call with return) |
| `cics_xctl` | CICS XCTL (transfer control, no return) |
| `ims_schedule` | IMS message scheduling |
| `shared_memory` | Shared memory segment |
| `pipe` | Unix pipe |
| `rmi` | Java Remote Method Invocation |
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

## Section 24: Preprocessor / Metaprogramming

Models preprocessor directives, macros, and metaprogramming constructs.

### PreprocessorDirective

**Definition**: A preprocessor directive or metaprogramming construct that modifies code before or during compilation.

**Purpose**: Captures conditional compilation, macro expansion, and code generation constructs that affect program behavior and structure.

**Key Attributes**:
- Inherits from `NamedEntity`
- **directive_type** (MetaprogrammingType, required): The type of metaprogramming construct
- **condition** (string): Conditional expression (e.g., `#ifdef DEBUG`)
- **expansion** (string): The expanded or generated code

**Relationships**:
- **directive_defined_in_container** <-> `CodeContainer`: Container where this directive is defined
- **directive_affects_encapsulation_units** <-> `EncapsulationUnit`: Encapsulation units affected by this directive
- **directive_affects_callables** <-> `CallableUnit`: Callables affected by this directive

**Example - C Preprocessor:**
```yaml
debug_guard:
  a: PreprocessorDirective
  name: DEBUG_LOGGING
  directive_type: c_preprocessor
  condition: "#ifdef DEBUG"
  expansion: "printf(\"Debug: %s\\n\", msg);"
  directive_defined_in_container: logger_header
```

**Example - COBOL COPY REPLACING:**
```yaml
employee_copy:
  a: PreprocessorDirective
  name: EMPLOYEE-COPY
  directive_type: cobol_copy_replacing
  condition: "COPY EMPLOYEE REPLACING ==:PREFIX:== BY ==EMP-=="
  directive_defined_in_container: payroll_source
```

### MetaprogrammingType Enum

| Value | Description |
|---|---|
| `c_preprocessor` | C/C++ preprocessor (#define, #ifdef) |
| `rust_macro_declarative` | Rust declarative macros (macro_rules!) |
| `rust_macro_procedural` | Rust procedural macros (derive, attribute) |
| `cobol_copy_replacing` | COBOL COPY ... REPLACING |
| `template_metaprogramming` | C++ template metaprogramming |
| `python_metaclass` | Python metaclass |
| `lisp_macro` | Lisp macro |
| `java_annotation_processor` | Java annotation processor |
| `code_generator` | External code generator |

---

## Section 25: Memory / Ownership Model

Models memory management and ownership semantics.

### MemoryModel

**Definition**: Describes the memory management strategy for a module or language.

**Purpose**: Enables analysis of memory safety, ownership transfer, and resource management patterns across codebases.

**Key Attributes**:
- Inherits from `NamedEntity`
- **primary_model** (OwnershipModel, required): The primary memory management approach
- **gc_type** (string): Garbage collector type (e.g., `generational`, `reference_counting`, `mark_sweep`)
- **supports_unsafe** (boolean): Whether the language/module allows unsafe memory operations

**Relationships**:
- **modules_using_memory_model** <-> `EncapsulationUnit`: Modules that use this memory model
- **memory_model_for_languages** <-> `ProgrammingLanguage`: Languages that use this as their default memory model

**Example:**
```yaml
rust_ownership:
  a: MemoryModel
  name: RustOwnershipModel
  primary_model: owned
  supports_unsafe: true

java_gc:
  a: MemoryModel
  name: JavaGCModel
  primary_model: garbage_collected
  gc_type: generational
  supports_unsafe: false
```

---

### OwnershipAnnotation

**Definition**: An ownership or lifetime annotation on a specific data element.

**Purpose**: Captures fine-grained ownership and lifetime information, particularly for Rust and C++ codebases.

**Key Attributes**:
- Inherits from `NamedEntity`
- **ownership** (OwnershipModel, required): The ownership model for this element
- **lifetime** (LifetimeScope): The lifetime scope
- **lifetime_name** (string): Named lifetime identifier (e.g., `'a` in Rust)

**Relationships**:
- **annotates_data_element** <-> `DataElement`: The data element this annotation applies to

**Example:**
```yaml
borrowed_ref_annotation:
  a: OwnershipAnnotation
  name: borrowed_config_ref
  ownership: borrowed_shared
  lifetime: named_lifetime
  lifetime_name: "'a"
  annotates_data_element: config_reference
```

### OwnershipModel Enum

| Value | Description |
|---|---|
| `owned` | Exclusively owned (Rust owned value) |
| `borrowed_shared` | Shared immutable borrow (&T in Rust) |
| `borrowed_mutable` | Exclusive mutable borrow (&mut T in Rust) |
| `moved` | Value has been moved (ownership transferred) |
| `copied` | Value is copied (Copy trait in Rust) |
| `reference_counted` | Reference-counted (Rc, Arc in Rust; shared_ptr in C++) |
| `garbage_collected` | Managed by garbage collector |
| `manual` | Manual allocation/deallocation (C malloc/free) |
| `stack_allocated` | Stack-allocated with automatic cleanup |

### LifetimeScope Enum

| Value | Description |
|---|---|
| `static_lifetime` | Lives for the entire program duration ('static) |
| `function_scope` | Lives for the duration of a function call |
| `block_scope` | Lives for the duration of a block |
| `named_lifetime` | Has a named lifetime parameter ('a, 'b) |
| `heap_lifetime` | Lives on the heap until explicitly freed |

---

## Section 26: Domain Entity Relationships

Provides named, typed relationships between domain entities. Wires the previously orphaned `Cardinality` enum into the domain model.

### DomainRelationship

**Definition**: A named, typed relationship between two domain entities (e.g., "Order has many OrderLines", "User belongs to Organization").

**Purpose**: Explicitly models ER-style relationships with cardinality, navigability, and composition semantics. This section wires the `Cardinality` enum -- previously defined but unused -- into the domain model.

**Key Attributes**:
- Inherits from `NamedEntity`
- **cardinality** (Cardinality, required): The multiplicity of the relationship
- **is_navigable** (boolean): Whether the relationship is traversable from source to target
- **is_bidirectional** (boolean): Whether the relationship can be navigated in both directions
- **is_composition** (boolean): Whether this represents UML composition (strong ownership) vs aggregation
- **foreign_key_field** (string): The implementing field in the data layer
- **join_entity** (string): For many-to-many relationships, the join table or entity

**Relationships**:
- **source_entity** / **outgoing_relationships** <-> `DomainEntity`: The entity that owns or originates the relationship
- **target_entity** / **incoming_relationships** <-> `DomainEntity`: The entity referenced by the relationship

**Uses Existing Cardinality Enum**:

| Value | Description |
|---|---|
| `one_to_one` | One-to-one relationship |
| `one_to_many` | One-to-many relationship |
| `many_to_one` | Many-to-one relationship |
| `many_to_many` | Many-to-many relationship |

**Example:**
```yaml
order_has_line_items:
  a: DomainRelationship
  name: OrderHasLineItems
  source_entity: order_entity
  target_entity: order_line_item_entity
  cardinality: one_to_many
  is_composition: true
  is_navigable: true
  is_bidirectional: true
  foreign_key_field: order_id

student_enrolled_in_courses:
  a: DomainRelationship
  name: StudentEnrolledInCourses
  source_entity: student_entity
  target_entity: course_entity
  cardinality: many_to_many
  is_composition: false
  is_navigable: true
  is_bidirectional: true
  join_entity: Enrollment
```

---

## Section 27: Database Schema Objects

Models schema-level constraints and indexes for migration, performance, and impact analysis.

### DatabaseConstraint

**Definition**: A constraint on a database collection (table).

**Purpose**: Captures primary keys, foreign keys, unique constraints, and check constraints for schema analysis, migration planning, and impact assessment.

**Key Attributes**:
- Inherits from `NamedEntity`
- **constraint_type** (DatabaseConstraintType, required): The type of constraint
- **columns** (string[]): Columns involved in the constraint
- **reference_table** (string): Referenced table (for foreign keys)
- **reference_columns** (string[]): Referenced columns (for foreign keys)
- **expression** (string): Constraint expression (for check constraints)

**Relationships**:
- **constraint_on_collection** <-> `Collection.has_constraints`: The collection this constraint belongs to

**Deprecation Note**: `DatabaseConstraint` and `DatabaseIndex` together deprecate the `indexes` (string[]) attribute on `Collection` for index information.

**Example:**
```yaml
order_pk:
  a: DatabaseConstraint
  name: pk_orders
  constraint_type: primary_key
  columns: [order_id]
  constraint_on_collection: orders_table

order_customer_fk:
  a: DatabaseConstraint
  name: fk_orders_customer
  constraint_type: foreign_key
  columns: [customer_id]
  reference_table: customers
  reference_columns: [customer_id]
  constraint_on_collection: orders_table
```

---

### DatabaseIndex

**Definition**: An index on a database collection (table).

**Purpose**: Captures index definitions for performance analysis and schema management.

**Key Attributes**:
- Inherits from `NamedEntity`
- **index_type** (IndexType, required): The type of index
- **columns** (string[]): Columns included in the index
- **is_unique** (boolean): Whether the index enforces uniqueness
- **is_partial** (boolean): Whether the index is partial/filtered
- **filter_expression** (string): Filter expression for partial indexes

**Relationships**:
- **index_on_collection** <-> `Collection.has_indexes`: The collection this index belongs to

**Example:**
```yaml
customer_email_idx:
  a: DatabaseIndex
  name: idx_customers_email
  index_type: btree
  columns: [email]
  is_unique: true
  is_partial: false
  index_on_collection: customers_table

order_search_idx:
  a: DatabaseIndex
  name: idx_orders_fulltext
  index_type: fulltext
  columns: [description, notes]
  is_unique: false
  is_partial: false
  index_on_collection: orders_table
```

### DatabaseConstraintType Enum

| Value | Description |
|---|---|
| `primary_key` | Primary key constraint |
| `foreign_key` | Foreign key constraint |
| `unique` | Unique constraint |
| `check` | Check constraint (arbitrary expression) |
| `not_null` | Not-null constraint |

### IndexType Enum

| Value | Description |
|---|---|
| `btree` | B-tree index (default for most databases) |
| `hash` | Hash index |
| `gin` | GIN (Generalized Inverted Index, PostgreSQL) |
| `fulltext` | Full-text search index |

---

## Section 28: Programming Language as First-Class Entity

Replaces bare string fields with a queryable language entity.

### ProgrammingLanguage

**Definition**: A programming language modeled as a first-class entity.

**Purpose**: Enables structured cross-language analysis. Query "show me all Rust modules" without resorting to string matching on format or language fields.

**Key Attributes**:
- Inherits from `NamedEntity`
- **paradigms** (ProgrammingParadigm[]): Programming paradigms supported
- **type_discipline** (string): Type system discipline (e.g., `static_strong`, `dynamic_weak`)
- **has_preprocessor** (boolean): Whether the language has a preprocessor
- **has_gc** (boolean): Whether the language has garbage collection
- **year_introduced** (int): Year the language was first released

**Relationships**:
- **language_used_by_containers** <-> `CodeContainer.written_in_language`: Code containers written in this language
- **default_error_model** <-> `ErrorModel`: The default error handling model for this language
- **default_memory_model** <-> `MemoryModel`: The default memory management model for this language

**Deprecation Note**: `ProgrammingLanguage` replaces the `format` (string) attribute on `CodeContainer` and the `language` (string) attribute on `Component`.

**Example:**
```yaml
rust_language:
  a: ProgrammingLanguage
  name: Rust
  paradigms: [procedural, functional, multi_paradigm]
  type_discipline: static_strong
  has_preprocessor: false
  has_gc: false
  year_introduced: 2010
  default_error_model: rust_error_model
  default_memory_model: rust_ownership

cobol_language:
  a: ProgrammingLanguage
  name: COBOL
  paradigms: [procedural]
  type_discipline: static_strong
  has_preprocessor: true
  has_gc: false
  year_introduced: 1959

java_language:
  a: ProgrammingLanguage
  name: Java
  paradigms: [object_oriented, multi_paradigm]
  type_discipline: static_strong
  has_preprocessor: false
  has_gc: true
  year_introduced: 1995
  default_error_model: java_error_model
  default_memory_model: java_gc
```

### ProgrammingParadigm Enum

| Value | Description |
|---|---|
| `object_oriented` | Object-oriented programming |
| `procedural` | Procedural programming |
| `functional` | Functional programming |
| `logic` | Logic programming (Prolog) |
| `concatenative` | Concatenative programming (Forth, Factor) |
| `data_driven` | Data-driven programming |
| `multi_paradigm` | Supports multiple paradigms |

---

## Cross-Section Relationships

The following diagram summarizes how the new sections connect to existing SAO classes and to each other.

### Connections to Existing Classes

| New Class | Existing Class | Relationship |
|---|---|---|
| `TypeExpression` | `DataElement` | `type_of_data_elements` <-> `declared_type` |
| `TypeExpression` | `Parameter` | `type_of_parameters` <-> `parameter_type` |
| `TypeExpression` | `CallableUnit` | `return_type_of_callables` <-> `return_type_expression` |
| `ErrorModel` | `EncapsulationUnit` | `modules_using_error_model` <-> `error_model_for_module` |
| `ExceptionType` | `CallableUnit` | `raised_by_callables` <-> `raises_exception_types` |
| `ExceptionType` | `CallableUnit` | `handled_by_callables` <-> `handles_exception_types` |
| `FileDefinition` | `CallableUnit` | `used_by_callables` <-> `uses_file_definitions` |
| `FileDefinition` | `CodeContainer` | `file_defined_in_container` <-> `container_file_definitions` |
| `FileDefinition` | `DataStore` | `persisted_in_store` <-> `store_file_definitions` |
| `FileOperation` | `CallableUnit` | `performed_in_callable` <-> `callable_file_operations` |
| `ScreenDefinition` | `EncapsulationUnit` | `program_uses_screens` <-> `screen_used_by_programs` |
| `ScreenDefinition` | `CodeContainer` | `screen_defined_in_container` <-> `container_screen_definitions` |
| `ScreenField` | `DataElement` | `maps_to_data_element` |
| `JobStep` | `EncapsulationUnit` | `step_executes_program` <-> `executed_by_job_steps` |
| `DatasetAllocation` | `FileDefinition` | `maps_to_file_definition` <-> `mapped_from_dataset_allocations` |
| `IPCConnection` | `EncapsulationUnit` | `ipc_source_program` <-> `outgoing_ipc_connections` |
| `IPCConnection` | `EncapsulationUnit` | `ipc_target_program` <-> `incoming_ipc_connections` |
| `IPCConnection` | `DataStructure` | `ipc_passes_data` <-> `passed_via_ipc` |
| `PreprocessorDirective` | `CodeContainer` | `directive_defined_in_container` <-> `container_preprocessor_directives` |
| `PreprocessorDirective` | `EncapsulationUnit` | `directive_affects_encapsulation_units` <-> `affected_by_directives` |
| `PreprocessorDirective` | `CallableUnit` | `directive_affects_callables` <-> `callable_affected_by_directives` |
| `MemoryModel` | `EncapsulationUnit` | `modules_using_memory_model` <-> `memory_model_for_module` |
| `OwnershipAnnotation` | `DataElement` | `annotates_data_element` |
| `DomainRelationship` | `DomainEntity` | `source_entity` <-> `outgoing_relationships` |
| `DomainRelationship` | `DomainEntity` | `target_entity` <-> `incoming_relationships` |
| `DatabaseConstraint` | `Collection` | `constraint_on_collection` <-> `has_constraints` |
| `DatabaseIndex` | `Collection` | `index_on_collection` <-> `has_indexes` |
| `ProgrammingLanguage` | `CodeContainer` | `language_used_by_containers` <-> `written_in_language` |
| `ProgrammingLanguage` | `ErrorModel` | `default_error_model` |
| `ProgrammingLanguage` | `MemoryModel` | `default_memory_model` |

### Connections Between New Sections

| Source Section | Target Section | Relationship |
|---|---|---|
| Section 22 (DatasetAllocation) | Section 20 (FileDefinition) | `maps_to_file_definition` |
| Section 22 (DatasetAllocation) | Section 20 (RecordFormat) | Shared `RecordFormat` enum |
| Section 28 (ProgrammingLanguage) | Section 19 (ErrorModel) | `default_error_model` |
| Section 28 (ProgrammingLanguage) | Section 25 (MemoryModel) | `default_memory_model` |
| Section 20 (FileOperation) | Section 20 (FileDefinition) | `operates_on_file` |

---

## Deprecation Summary

The following table lists all attributes deprecated by Sections 18-28, along with their replacements.

| Deprecated Attribute | On Class | Replaced By | New Type | Section |
|---|---|---|---|---|
| `data_type` (string) | `DataElement` | `declared_type` | `TypeExpression` | 18 |
| `data_type` (string) | `Parameter` | `parameter_type` | `TypeExpression` | 18 |
| `raises_exceptions` (string[]) | `CallableUnit` | `raises_exception_types` | `ExceptionType[]` | 19 |
| `handles_exceptions` (string[]) | `CallableUnit` | `handles_exception_types` | `ExceptionType[]` | 19 |
| `indexes` (string[]) | `Collection` | `has_indexes` | `DatabaseIndex[]` | 27 |
| `format` (string) | `CodeContainer` | `written_in_language` | `ProgrammingLanguage` | 28 |
| `language` (string) | `Component` | `written_in_language` (via CodeContainer) | `ProgrammingLanguage` | 28 |

All deprecated attributes remain in the schema for backward compatibility. New models should use the replacement attributes exclusively.

---

## Usage Patterns

### Cross-Language Type Analysis

```sparql
# Find all data elements with generic types
SELECT ?element ?base_type WHERE {
  ?type a sao:TypeExpression ;
        sao:type_kind "generic" ;
        sao:base_type ?base_type .
  ?element sao:declared_type ?type .
}
```

### Batch Job Impact Analysis

```sparql
# Find all programs executed by a job and the files they use
SELECT ?job ?step ?program ?file WHERE {
  ?job a sao:JobDefinition ;
       sao:contains_job_steps ?step .
  ?step sao:step_executes_program ?program .
  ?program sao:uses_file_definitions ?file .
}
```

### IPC Dependency Graph

```sparql
# Find all inter-process communication paths
SELECT ?source ?mechanism ?target WHERE {
  ?ipc a sao:IPCConnection ;
       sao:mechanism ?mechanism ;
       sao:ipc_source_program ?source ;
       sao:ipc_target_program ?target .
}
```

### Language-Scoped Queries

```sparql
# Find all Rust modules and their memory models
SELECT ?module ?memory_model WHERE {
  :rust_language sao:language_used_by_containers ?container .
  ?module sao:defined_in_container ?container .
  ?module sao:memory_model_for_module ?memory_model .
}
```

---

## Best Practices

1. **Use TypeExpression for new models**: Do not rely on `data_type` strings when structured type information is needed.
2. **Model error handling explicitly**: Attach an `ErrorModel` to each `EncapsulationUnit` to enable cross-module error strategy analysis.
3. **Connect files to jobs**: Always link `FileDefinition` to `DatasetAllocation` via `maps_to_file_definition` for mainframe systems.
4. **Use ProgrammingLanguage over strings**: Replace bare `format` and `language` strings with `ProgrammingLanguage` entity references.
5. **Capture IPC dependencies**: Model all inter-process communication paths, even database-mediated ones, to get a complete dependency picture.
6. **Annotate ownership in Rust/C++**: Use `OwnershipAnnotation` to track borrow relationships and lifetime constraints on data elements.
7. **Define screen-to-data mappings**: Link `ScreenField` to `DataElement` to trace user input through the program.
8. **Model constraints and indexes as objects**: Use `DatabaseConstraint` and `DatabaseIndex` instead of string arrays to enable schema comparison and migration analysis.
