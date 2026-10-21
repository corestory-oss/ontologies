# Code Structure

The Code Structure layer provides a paradigm-agnostic framework for modeling software systems at the implementation level. This layer bridges the gap between architectural concepts (Components, Operations) and the actual source code that implements them, supporting both modern and legacy systems.

> **v2.0 Note:** In SAO v2.0, all single-use relationship slots have been inlined as class attributes on their owning classes. Only approximately 20 multi-domain slots remain as global relationships: `defined_in_container`, `contained_in_unit`, `contains_data_elements`, `implements_component`, `implemented_by_code`, `annotates_element`, `annotated_by`, `affects_behavior_of`, `imports_symbols`, and `imported_via`.

## Overview

The code structure model consists of three main levels:

1. **Physical Structure** - Storage and organization of code files
2. **Logical Structure** - Encapsulation units, callable units, and data structures
3. **Semantic Structure** - Control flow, data flow, and code semantics

This design principle ensures that a single ontology can represent:
- Modern object-oriented systems (Java, Python, C#)
- Procedural systems (C, Pascal, Fortran)
- Functional systems (Haskell, OCaml, F#)
- Mainframe systems (COBOL, PL/I, Assembler)
- Database systems (SQL stored procedures, triggers)

## Design Philosophy: Paradigm Agnosticism

Rather than creating separate classes for each programming paradigm (e.g., `Class`, `Program`, `Module`), this ontology uses **type-based polymorphism**:

- A single class (`EncapsulationUnit`) represents all forms of code grouping
- The `encapsulation_type` attribute specifies the paradigm-specific type
- Enumerations provide comprehensive coverage across all paradigms

### Example Mappings

```yaml
# Java class
my_service:
  a: EncapsulationUnit
  name: UserService
  encapsulation_type: class
  visibility: public

# COBOL program
batch_job:
  a: EncapsulationUnit
  name: PAYROLL
  encapsulation_type: batch_program
  
# Haskell module
utils:
  a: EncapsulationUnit
  name: Utils
  encapsulation_type: module
```

## Physical Code Structure

### CodeContainer

Represents the physical storage of source code - files, library members, or other storage units.

**Key Attributes:**
- `container_path` - Path or identifier for the container
- `container_type` - Type of container (source_file, library_member, copybook, script, etc.)
- `format` - ~~Language or format (COBOL, Java, Python, SQL, etc.)~~ **Deprecated in v2.0** — use `written_in_language` (range: ProgrammingLanguage) instead
- `written_in_language` - **(v2.0)** ProgrammingLanguage relationship replacing `format`
- `size_bytes` - Size in bytes
- `line_count` - Number of lines
- `encoding` - Character encoding
- `checksum` - Content hash for version tracking
- `has_file_definitions` - **(v2.0)** FileDefinition[] associated with this container
- `has_screen_definitions` - **(v2.0)** ScreenDefinition[] associated with this container
- `has_preprocessor_directives` - **(v2.0)** PreprocessorDirective[] associated with this container

**Container Types:**
- `source_file` - Standard source code file
- `library_member` - Member of a partitioned dataset or library (mainframe)
- `include_file` - Header or include file
- `script` - Executable script
- `configuration` - Configuration file
- `schema_definition` - Database or API schema
- `notebook_cell` - Jupyter notebook cell
- `inline_code` - Embedded code (JavaScript in HTML, SQL in application)
- `jcl_member` - **(v2.0)** JCL member
- `rpg_source` - **(v2.0)** RPG source member
- `pli_source` - **(v2.0)** PL/I source member
- `assembler_source` - **(v2.0)** Assembler source member
- `cl_source` - **(v2.0)** CL (Control Language) source member

**Example:**
```yaml
user_service_file:
  a: CodeContainer
  container_path: /src/services/UserService.java
  container_type: source_file
  format: Java
  line_count: 450
  encoding: UTF-8
```

### StorageLocation

Represents a logical or physical location for storing code containers.

**Key Attributes:**
- `location_path` - Path or identifier
- `location_type` - Type (directory, library, package, namespace, module_path)

**Location Types:**
- `directory` - Filesystem directory
- `library` - Partitioned dataset (mainframe) or static library
- `package` - Language package or module
- `namespace` - Logical namespace
- `module_path` - Module search path

**Relationships:**
- `has_parent_location` - Parent storage location (hierarchical)
- `contains_locations` - Child storage locations
- `contains_containers` - Code containers in this location
- `maps_to_module` - Corresponding architectural Module

**Example:**
```yaml
services_directory:
  a: StorageLocation
  location_path: /src/services
  location_type: directory
  maps_to_module: user_management_module

cobol_library:
  a: StorageLocation
  location_path: SYS1.COBLIB
  location_type: library
```

## Logical Code Structure

### EncapsulationUnit

A logical boundary that groups related code and data. This is the cornerstone of the paradigm-agnostic design.

**Key Attributes:**
- `encapsulation_type` - **Required.** The paradigm-specific type (see EncapsulationType enum)
- `visibility` - Visibility level (public, private, protected, internal, package)
- `qualified_name` - Fully qualified name (e.g., com.example.UserService)
- `stereotype` - Additional stereotype (Service, Repository, DTO, Controller, etc.)
- `is_abstract` - Whether this is abstract/incomplete
- `is_final` - Whether this can be extended
- `error_model_for_module` - **(v2.0)** ErrorModel associated with this unit
- `screen_used_by_programs` - **(v2.0)** ScreenDefinition[] used by this unit
- `has_outgoing_ipc_connections` - **(v2.0)** IPCConnection[] originating from this unit
- `has_incoming_ipc_connections` - **(v2.0)** IPCConnection[] targeting this unit
- `affected_by_directives` - **(v2.0)** PreprocessorDirective[] affecting this unit
- `memory_model_for_module` - **(v2.0)** MemoryModel associated with this unit
- `executed_by_job_steps` - **(v2.0)** JobStep[] that execute this unit

**EncapsulationType Values** (33 total):

**Object-Oriented:**
- `class` - Standard OOP class
- `interface` - Interface/contract definition
- `abstract_class` - Abstract base class
- `trait` - Trait (Rust, Scala) or mixin
- `enum_class` - Enumeration class
- `record_class` - Immutable record (Java, C#)
- `singleton` - Singleton pattern

**Procedural:**
- `program` - Standalone program
- `subprogram` - Subprogram or subroutine module
- `unit` - Pascal/Ada unit

**Functional:**
- `module` - Functional module (Haskell, OCaml, F#)
- `namespace` - Namespace grouping
- `package` - Package grouping
- `library` - Library module

**Mainframe:**
- `batch_program` - Batch processing program
- `online_program` - Online transaction program (CICS, IMS)
- `copybook` - COBOL copybook
- `rpg_module` - **(v2.0)** RPG module
- `rpg_service_program` - **(v2.0)** RPG service program
- `pli_procedure` - **(v2.0)** PL/I external procedure
- `pli_package` - **(v2.0)** PL/I package
- `assembler_csect` - **(v2.0)** Assembler control section (CSECT)

**Database:**
- `stored_procedure` - Database stored procedure package
- `function_package` - Function package (Oracle)
- `trigger` - Database trigger
- `view` - Database view

**Other:**
- `object` - JavaScript/prototype-based object
- `component` - Component definition
- `service` - Service class
- `controller` - Controller class
- `script` - Script module
- `composite` - Composite structure
- `other` - Other types

**Relationships:**
- `defined_in_container` - Code container where this is defined
- `contains_callable_units` - Callable units (methods, functions, etc.) in this unit
- `contains_data_structures` - Data structures in this unit
- `contains_data_elements` - Data elements (fields, variables) in this unit
- `extends_units` - Units this extends/inherits from
- `implements_contracts` - Contracts (interfaces) this implements
- `uses_definitions` - Definition references (imports, includes) used
- `implements_component` - Architectural Component this implements

**Example - Java Class:**
```yaml
user_service:
  a: EncapsulationUnit
  name: UserService
  encapsulation_type: class
  visibility: public
  stereotype: Service
  qualified_name: com.example.services.UserService
  implements_component: user_management_component
```

**Example - COBOL Program:**
```yaml
payroll_batch:
  a: EncapsulationUnit
  name: PAYROLL
  encapsulation_type: batch_program
  qualified_name: PAYROLL
  defined_in_container: payroll_source
```

### CallableUnit

A named, invocable unit of code - the paradigm-agnostic representation of functions, methods, procedures, etc.

**Key Attributes:**
- `callable_type` - **Required.** The paradigm-specific type (see CallableType enum)
- `visibility` - Visibility level
- `return_type` - Return type (if applicable)
- `is_async` - Whether this is asynchronous
- `is_pure` - Whether this is a pure function (no side effects)
- `is_static` - Whether this is static
- `is_virtual` - Whether this is virtual/overridable
- `complexity_score` - Cyclomatic complexity or similar metric
- `entry_point_type` - If this is an entry point (main, constructor, handler, etc.)
- `has_return_type` - **(v2.0)** TypeExpression for the return type
- `uses_file_definitions` - **(v2.0)** FileDefinition[] used by this callable
- `has_file_operations` - **(v2.0)** FileOperation[] performed by this callable
- `callable_affected_by_directives` - **(v2.0)** PreprocessorDirective[] affecting this callable

**CallableType Values** (53 total):

**Object-Oriented Methods:**
- `method` - Instance method
- `static_method` - Static/class method
- `constructor` - Object constructor
- `destructor` - Object destructor
- `property_getter` - Property getter
- `property_setter` - Property setter
- `operator_overload` - Operator overloading
- `conversion_operator` - Type conversion operator
- `indexer` - Indexer/subscript operator
- `abstract_method` - Abstract method declaration
- `virtual_method` - Virtual/overridable method

**Procedural:**
- `function` - Function (procedural or functional)
- `procedure` - Procedure/subroutine
- `subroutine` - Subroutine
- `paragraph` - COBOL paragraph
- `section` - COBOL section
- `rpg_subprocedure` - **(v2.0)** RPG subprocedure
- `pli_entry` - **(v2.0)** PL/I entry point
- `assembler_entry` - **(v2.0)** Assembler entry point
- `rpg_subroutine` - **(v2.0)** RPG subroutine

**Functional:**
- `lambda` - Anonymous lambda function
- `closure` - Closure
- `higher_order_function` - Higher-order function
- `curried_function` - Curried function
- `functor` - Functor

**Event Handling:**
- `event_handler` - Event handler
- `callback` - Callback function
- `delegate` - Delegate
- `signal_handler` - Signal handler

**Database:**
- `stored_procedure` - Database stored procedure
- `stored_function` - Database function
- `trigger_body` - Trigger implementation
- `cursor` - Database cursor

**Concurrency:**
- `coroutine` - Coroutine
- `generator` - Generator function
- `async_function` - Async function
- `thread_entry` - Thread entry point
- `task` - Task/future

**Testing:**
- `test_case` - Test case
- `test_fixture` - Test fixture/setup
- `mock` - Mock function

**Other:**
- `macro` - Preprocessor macro
- `template` - Template/generic function
- `generic_method` - Generic method
- `main_entry` - Main entry point
- `interrupt_handler` - Interrupt handler
- `exception_handler` - Exception handler
- `finalizer` - Finalizer/cleanup
- `factory_method` - Factory method
- `extension_method` - Extension method
- `script_function` - Script function
- `command` - Command/action
- `other` - Other types

**Relationships:**
- `contained_in_unit` - Encapsulation unit containing this callable
- `has_parameters` - Parameters of this callable
- `invokes_callables` - Other callables invoked by this one
- `accesses_data_elements` - Data elements accessed (read)
- `modifies_data_elements` - Data elements modified (written)
- `raises_exceptions` - ~~Exceptions that may be raised~~ **Deprecated in v2.0** — use `raises_exception_types` (ExceptionType[]) instead
- `handles_exceptions` - ~~Exceptions handled~~ **Deprecated in v2.0** — use `handles_exception_types` (ExceptionType[]) instead
- `raises_exception_types` - **(v2.0)** ExceptionType[] that may be raised
- `handles_exception_types` - **(v2.0)** ExceptionType[] that are handled
- `overrides_callable` - Callable in parent this overrides
- `implements_operation` - Architectural Operation this implements

**Example - Java Method:**
```yaml
create_user:
  a: CallableUnit
  name: createUser
  callable_type: method
  visibility: public
  return_type: User
  complexity_score: 8
  contained_in_unit: user_service
  implements_operation: create_user_operation
```

**Example - COBOL Paragraph:**
```yaml
calculate_totals:
  a: CallableUnit
  name: CALCULATE-TOTALS
  callable_type: paragraph
  contained_in_unit: payroll_batch
```

### DataStructure

Represents organized data storage - the paradigm-agnostic representation of classes, records, structs, etc.

**Key Attributes:**
- `structure_type` - **Required.** The paradigm-specific type (see DataStructureType enum)
- `nesting_level` - Nesting depth (for hierarchical structures like COBOL)
- `is_mutable` - Whether data can be modified
- `is_serializable` - Whether this can be serialized
- `persistence_type` - How this is persisted (transient, database, file, memory, cache)
- `passed_via_ipc` - **(v2.0)** IPCConnection[] through which this structure is passed

**DataStructureType Values** (50 total):

**Object-Oriented:**
- `class_data` - Data members of a class
- `inner_class` - Inner/nested class
- `anonymous_class` - Anonymous class

**Procedural:**
- `struct` - C/C++ struct
- `record` - Pascal/Ada record or COBOL record
- `union` - C union

**COBOL:**
- `group_item` - COBOL group item (composite data)
- `copybook_structure` - COBOL copybook structure
- `commarea` - CICS communication area
- `rpg_data_structure` - **(v2.0)** RPG data structure
- `pli_structure` - **(v2.0)** PL/I structure
- `assembler_dsect` - **(v2.0)** Assembler DSECT
- `cobol_file_descriptor` - **(v2.0)** COBOL file descriptor (FD)

**Functional:**
- `algebraic_data_type` - ADT (Haskell, ML)
- `type_class` - Type class
- `product_type` - Product type (tuple-like)
- `sum_type` - Sum/variant type

**Collections:**
- `array` - Fixed-size array
- `dynamic_array` - Dynamic array
- `list` - List structure
- `dictionary` - Dictionary/map/hash
- `set` - Set structure
- `queue` - Queue
- `stack` - Stack
- `tree` - Tree structure
- `graph` - Graph structure

**Database:**
- `table_structure` - Database table structure
- `view_structure` - Database view structure
- `cursor_structure` - Cursor structure
- `rowtype` - Database row type

**Domain-Driven Design:**
- `value_object` - DDD value object
- `dto` - Data Transfer Object

**Other:**
- `tuple` - Tuple
- `pair` - Key-value pair
- `enum` - Enumeration
- `flags` - Bit flags
- `configuration_object` - Configuration data
- `message` - Message structure
- `event` - Event data
- `command` - Command data
- `json_schema` - JSON schema structure
- `xml_schema` - XML schema structure
- `protobuf_message` - Protocol Buffers message
- `avro_record` - Avro record
- `smart_pointer` - Smart pointer wrapper
- `reference_wrapper` - Reference wrapper

**Relationships:**
- `contained_in_unit` - Encapsulation unit containing this structure
- `contains_data_elements` - Data elements in this structure
- `has_parent_structure` - Parent structure (for nested structures)
- `has_child_structures` - Child/nested structures
- `maps_to_domain_entity` - Domain entity this maps to
- `maps_to_value_object` - Value object this maps to
- `persisted_in_collection` - Collection where this is persisted

**Example - Java Class Data:**
```yaml
user_data:
  a: DataStructure
  name: UserData
  structure_type: class_data
  contained_in_unit: user_entity
  maps_to_domain_entity: user_entity
```

**Example - COBOL Group Item:**
```yaml
employee_record:
  a: DataStructure
  name: EMPLOYEE-RECORD
  structure_type: group_item
  nesting_level: 1
  contained_in_unit: payroll_copybook
```

### DataElement

Individual data fields, variables, or constants.

**Key Attributes:**
- `element_category` - Category of element (field, static_field, local_variable, parameter, constant, global_variable, computed, temporary)
- `data_type` - Data type (string, integer, User, etc.) — **Deprecated for typed analysis in v2.0** — use `declared_type` (TypeExpression) instead
- `declared_type` - **(v2.0)** TypeExpression for the declared type
- `visibility` - Visibility level
- `is_constant` - Whether this is a constant/immutable
- `is_nullable` - Whether this can be null
- `default_value` - Default value
- `has_ownership_annotations` - **(v2.0)** OwnershipAnnotation[] for this element
- `mapped_from_screen_fields` - **(v2.0)** ScreenField[] mapped to this element

**Relationships:**
- `contained_in_unit` - Encapsulation unit containing this element
- `contained_in_structure` - Data structure containing this element
- `has_parent_element` - Parent element (for nested fields)
- `has_type_definition` - Type definition reference

**Example:**
```yaml
user_email:
  a: DataElement
  name: email
  element_category: field
  data_type: String
  visibility: private
  is_nullable: false
  contained_in_structure: user_data
```

### Parameter

Function/method parameter.

**Key Attributes:**
- `direction` - Direction (range: `ParameterDirection`): `input`, `output`, `input_output`, `return`
- `position` - Position in parameter list
- `passing_mechanism` - How passed (by_value, by_reference, by_name, by_result)

**Example:**
```yaml
username_param:
  a: Parameter
  name: username
  direction: input
  data_type: String
  position: 1
  parameter_of: create_user
```

## Semantic Code Structure

### CodeBlock

A logical block of code (conditional, loop, try-catch, etc.).

**Key Attributes:**
- `block_type` - Type (sequential, conditional, loop, try_catch, transaction, critical_section, scope)

### Statement

Individual code statement.

**Key Attributes:**
- `statement_category` - Category (declaration, assignment, invocation, control_transfer, io_operation, data_manipulation, transaction_control, exception_handling)
- `line_number` - Source line number

### ControlFlow

Control flow between code elements (calls, branches, etc.).

**Key Attributes:**
- `flow_type` - Type (call, async_call, branch, jump, return, throw, yield)
- `is_conditional` - Whether flow is conditional
- `condition` - Condition expression

**Relationships:**
- `has_source_callable` - Source callable
- `has_target_callable` - Target callable
- `has_source_statement` - Source statement
- `has_target_statement` - Target statement

### DataFlow

Data flow between elements.

**Key Attributes:**
- `flow_type` - Type (read, write, modify, define, use)

**Relationships:**
- `has_source_element` - Source data element
- `has_target_element` - Target data element

## Mapping to Architecture

The code structure model integrates with the architectural model:

### Component Implementation

```yaml
user_service_component:
  a: Component
  name: UserManagement

user_service_class:
  a: EncapsulationUnit
  encapsulation_type: class
  implements_component: user_service_component

user_repository_class:
  a: EncapsulationUnit
  encapsulation_type: class
  implements_component: user_service_component
```

### Operation Implementation

```yaml
create_user_op:
  a: Operation
  name: CreateUser
  
create_user_method:
  a: CallableUnit
  callable_type: method
  implements_operation: create_user_op
```

### Domain Entity Mapping

```yaml
user_entity:
  a: DomainEntity
  name: User

user_class:
  a: EncapsulationUnit
  encapsulation_type: class

user_data_structure:
  a: DataStructure
  structure_type: class_data
  maps_to_domain_entity: user_entity
```

## Cross-Paradigm Examples

### Modern Java Microservice

```yaml
# File
user_service_file:
  a: CodeContainer
  container_path: /src/main/java/com/example/UserService.java
  container_type: source_file
  format: Java

# Class
user_service:
  a: EncapsulationUnit
  name: UserService
  encapsulation_type: class
  visibility: public
  stereotype: Service
  defined_in_container: user_service_file

# Method
create_user:
  a: CallableUnit
  name: createUser
  callable_type: method
  visibility: public
  return_type: User
  contained_in_unit: user_service
```

### COBOL Mainframe Application

```yaml
# Library Member
payroll_source:
  a: CodeContainer
  container_path: SYS1.COBLIB(PAYROLL)
  container_type: library_member
  format: COBOL

# Program
payroll_program:
  a: EncapsulationUnit
  name: PAYROLL
  encapsulation_type: batch_program
  defined_in_container: payroll_source

# Paragraph
calculate_pay:
  a: CallableUnit
  name: CALCULATE-PAY
  callable_type: paragraph
  contained_in_unit: payroll_program

# Copybook
employee_copybook:
  a: CodeContainer
  container_path: SYS1.COPYLIB(EMPLOYEE)
  container_type: library_member
  format: COBOL

employee_structure:
  a: EncapsulationUnit
  name: EMPLOYEE-RECORD
  encapsulation_type: copybook
  defined_in_container: employee_copybook

# Group Item
employee_data:
  a: DataStructure
  name: EMPLOYEE-RECORD
  structure_type: group_item
  nesting_level: 1
  contained_in_unit: employee_structure
```

### Python Script

```yaml
# File
data_processor_file:
  a: CodeContainer
  container_path: /scripts/process_data.py
  container_type: script
  format: Python

# Module
data_processor:
  a: EncapsulationUnit
  name: process_data
  encapsulation_type: module
  defined_in_container: data_processor_file

# Function
process_records:
  a: CallableUnit
  name: process_records
  callable_type: function
  is_async: true
  contained_in_unit: data_processor
```

### SQL Stored Procedure

```yaml
# Database Object
update_inventory_proc:
  a: EncapsulationUnit
  name: update_inventory
  encapsulation_type: stored_procedure

# Procedure Body
update_inventory_impl:
  a: CallableUnit
  name: update_inventory
  callable_type: stored_procedure
  contained_in_unit: update_inventory_proc
```

## Supporting Enumerations

### Additional Type Enumerations

- **VisibilityType**: `public`, `private`, `protected`, `internal`, `package`
- **CallableCategory**: `normal`, `operator`, `main_entry` **(v2.0 — cleaned to 3 values)**
- **EntryPointType**: `main_program`, `transaction_entry`, `event_handler`, `scheduled_entry`, `api_endpoint`
- **DataStructureCategory**: `composite`, `collection`, `hierarchical`, `value_type`, `reference_type`, `union`
- **DataElementCategory**: `field`, `static_field`, `local_variable`, `parameter`, `constant`, `global_variable`, `computed`, `temporary`
- **ParameterDirection**: `input`, `output`, `input_output`, `return`
- **PassingMechanism**: `by_value`, `by_reference`, `by_name`, `by_result`
- **CodeBlockType**: `sequential`, `conditional`, `loop`, `try_catch`, `transaction`, `critical_section`, `scope`
- **StatementCategory**: `declaration`, `assignment`, `invocation`, `control_transfer`, `io_operation`, `data_manipulation`, `transaction_control`, `exception_handling`
- **ReferenceType**: `import_module`, `import_symbol`, `include_source`, `inherit`, `implement`
- **ControlFlowType**: `call`, `async_call`, `branch`, `jump`, `return`, `throw`, `yield`
- **DataFlowType**: `read`, `write`, `modify`, `define`, `use`

## Usage Patterns

### Tracing Implementation

Trace from architectural concept to implementation:

```sparql
# Find all code implementing a Component
SELECT ?code ?type WHERE {
  ?code sao:implements_component :user_management_component .
  ?code sao:encapsulation_type ?type .
}
```

### Call Graph Analysis

```sparql
# Find call chains
SELECT ?caller ?callee WHERE {
  ?flow a sao:ControlFlow ;
        sao:flow_type "call" ;
        sao:source_callable ?caller ;
        sao:target_callable ?callee .
}
```

### Cross-Reference Analysis

```sparql
# Find all places a function is called
SELECT ?caller WHERE {
  ?flow a sao:ControlFlow ;
        sao:target_callable :create_user_method ;
        sao:source_callable ?caller .
}
```

## Best Practices

1. **Use Qualified Names**: Always provide `qualified_name` for encapsulation units
2. **Link to Architecture**: Connect code to Components and Operations via `implements_component` and `implements_operation`
3. **Track Dependencies**: Use DefinitionReference to model imports/includes
4. **Model Call Graphs**: Use ControlFlow to represent invocation relationships
5. **Map Data**: Connect DataStructures to DomainEntities via `maps_to_domain_entity`
6. **Specify Types Precisely**: Use the most specific type enum value available
7. **Document Visibility**: Always specify visibility for encapsulation units and callables
8. **Track Complexity**: Record complexity metrics for callables to support quality analysis

## Integration with Other Layers

- **Structural Foundation**: CodeContainers map to Modules, EncapsulationUnits implement Components
- **Domain Modeling**: DataStructures map to DomainEntities and ValueObjects
- **Behavior**: CallableUnits implement Operations and participate in Workflows
- **Data Management**: DataStructures are persisted in Collections
- **Integration**: EncapsulationUnits may expose or consume Interfaces

## New Sections in v2.0

The following sections were introduced in SAO v2.0 to support advanced type modeling, error handling, file I/O, screen interaction, batch orchestration, inter-process communication, preprocessor/metaprogramming, memory/ownership models, database schema objects, and programming language metadata.

### Type System Modeling (Section 18)

**TypeExpression** (is_a NamedEntity)

A recursive type model capable of representing generics, unions, pointers, and function types.

**Key Attributes:**
- `type_kind` - TypeKind (e.g., primitive, generic, union, pointer, function_type, array)
- `base_type` - Base type name or reference
- `has_type_parameters` - TypeExpression[] (self-referential, multivalued) for generic parameters
- `type_constraints` - Constraints on type parameters
- `is_nullable` - Whether this type is nullable
- `nullability_model` - Nullability model (e.g., optional, nullable_reference, maybe)
- `pointer_semantics` - Pointer semantics (e.g., raw, shared, unique, weak)

**Relationships:**
- Connected to DataElement via `declared_type` / `type_of_data_elements`
- Connected to Parameter via `has_type` / `type_of_parameters`
- Connected to CallableUnit via `has_return_type` / `return_type_of_callables`

### Error Handling Model (Section 19)

**ErrorModel** (is_a NamedEntity)

Describes the error handling strategy for a module or language.

**Key Attributes:**
- `strategy` - ErrorHandlingStrategy (e.g., exceptions, error_codes, result_type, condition_system)
- `checkedness` - ExceptionCheckedness (e.g., checked, unchecked, mixed)

**Relationships:**
- Connected to EncapsulationUnit via `error_model_for_module`
- Connected to ProgrammingLanguage

---

**ExceptionType** (is_a NamedEntity)

Represents a specific exception or error type in the exception hierarchy.

**Key Attributes:**
- `qualified_name` - Fully qualified exception class name
- `is_checked` - Whether this is a checked exception
- `has_parent_exception` - Parent ExceptionType in the hierarchy
- `has_child_exceptions` - Child ExceptionType[] in the hierarchy

**Relationships:**
- Connected to CallableUnit via `raises_exception_types` / `handles_exception_types`

### File I/O Definitions (Section 20)

**FileDefinition** (is_a NamedEntity)

Represents a declared file or dataset used by a program.

**Key Attributes:**
- `organization` - FileOrganization (e.g., sequential, indexed, relative, vsam_ksds, vsam_rrds)
- `access_mode` - FileAccessMode (e.g., sequential, random, dynamic)
- `record_format` - RecordFormat (e.g., fixed, variable, undefined)
- `record_length` - Record length
- `block_size` - Block size
- `key_fields` - Key field names
- `file_status_field` - File status variable name
- `external_name` - External dataset or file name

**Relationships:**
- Connected to CallableUnit via `uses_file_definitions`
- Connected to CodeContainer via `has_file_definitions`
- Connected to DataStore

---

**FileOperation** (is_a NamedEntity)

Represents an individual file I/O operation within code.

**Key Attributes:**
- `operation_type` - FileOperationType (e.g., open, close, read, write, rewrite, delete, start)
- `condition_handling` - Condition or error handling for this operation

**Relationships:**
- Connected to FileDefinition
- Connected to CallableUnit via `has_file_operations`

### Screen / Terminal Interaction (Section 21)

**ScreenDefinition** (is_a NamedEntity)

Represents a terminal screen or display definition (e.g., BMS map, DDS display file).

**Key Attributes:**
- `screen_type` - ScreenType (e.g., bms_map, dds_display, mfs_format, panel)
- `rows` - Number of rows
- `columns` - Number of columns
- `external_name` - External map or screen name

**Relationships:**
- Connected to ScreenField (contains fields)
- Connected to EncapsulationUnit via `screen_used_by_programs`
- Connected to CodeContainer via `has_screen_definitions`

---

**ScreenField** (is_a NamedEntity)

Represents an individual field on a screen definition.

**Key Attributes:**
- `row` - Row position
- `column` - Column position
- `length` - Field length
- `is_input` - Whether this field accepts input
- `is_protected` - Whether this field is protected
- `attribute_byte` - Display attribute byte
- `initial_value` - Initial/default value

**Relationships:**
- Connected to ScreenDefinition
- Connected to DataElement via `mapped_from_screen_fields`

### Job Control / Batch Orchestration (Section 22)

**JobDefinition** (is_a NamedEntity)

Represents a batch job definition (e.g., JCL JOB statement).

**Key Attributes:**
- `job_class` - Job execution class
- `priority` - Job priority
- `restart_point` - Restart step or checkpoint
- `scheduling_info` - Scheduling metadata

**Relationships:**
- Contains JobStep[] (ordered steps within the job)
- Can depend on other JobDefinition[] (job dependencies)

---

**JobStep** (is_a NamedEntity)

Represents an individual step within a batch job.

**Key Attributes:**
- `step_type` - JobStepType (e.g., exec_program, exec_proc, utility)
- `program_name` - Program or procedure to execute
- `condition_code` - Condition code for step execution
- `region_size` - Memory region size

**Relationships:**
- Connected to JobDefinition (parent job)
- Connected to EncapsulationUnit via `executed_by_job_steps`

---

**DatasetAllocation** (is_a NamedEntity)

Represents a dataset or file allocation within a job step (e.g., JCL DD statement).

**Key Attributes:**
- `dd_name` - DD name (logical file name)
- `dataset_name` - Physical dataset name
- `disposition` - DatasetDisposition (e.g., new, old, shr, mod)
- `space_primary` - Primary space allocation
- `space_secondary` - Secondary space allocation
- `record_format` - Record format

**Relationships:**
- Connected to JobStep
- Connected to FileDefinition

### Inter-Process Communication (Section 23)

**IPCConnection** (is_a NamedEntity)

Represents a communication channel between processes or programs.

**Key Attributes:**
- `mechanism` - IPCMechanism (e.g., message_queue, socket, shared_memory, named_pipe, cics_link, cics_xctl, grpc_call, event_bus)
- `is_synchronous` - Whether the communication is synchronous
- `transaction_scoped` - Whether the connection is scoped to a transaction

**Relationships:**
- Connects source EncapsulationUnit (`has_outgoing_ipc_connections`) to target EncapsulationUnit (`has_incoming_ipc_connections`)
- Passes DataStructure[] via `passed_via_ipc`

### Preprocessor / Metaprogramming (Section 24)

**PreprocessorDirective** (is_a NamedEntity)

Represents a preprocessor directive or metaprogramming construct.

**Key Attributes:**
- `directive_type` - MetaprogrammingType (e.g., conditional_compilation, macro_definition, include, pragma, template_instantiation)
- `condition` - Condition expression (for conditional compilation)
- `expansion` - Expanded text or result

**Relationships:**
- Connected to CodeContainer via `has_preprocessor_directives`
- Connected to EncapsulationUnit via `affected_by_directives`
- Connected to CallableUnit via `callable_affected_by_directives`

### Memory / Ownership Model (Section 25)

**MemoryModel** (is_a NamedEntity)

Describes the memory management model for a module or language.

**Key Attributes:**
- `primary_model` - OwnershipModel (e.g., gc_managed, reference_counted, manual, ownership_based, arena)
- `gc_type` - Garbage collector type (e.g., generational, concurrent, reference_counting)
- `supports_unsafe` - Whether unsafe/unmanaged memory access is supported

**Relationships:**
- Connected to EncapsulationUnit via `memory_model_for_module`
- Connected to ProgrammingLanguage

---

**OwnershipAnnotation** (is_a NamedEntity)

Represents an ownership or lifetime annotation on a data element.

**Key Attributes:**
- `ownership` - OwnershipModel (e.g., owned, borrowed, shared, static)
- `lifetime` - LifetimeScope (e.g., static, local, heap, parameter)
- `lifetime_name` - Named lifetime identifier (e.g., `'a` in Rust)

**Relationships:**
- Connected to DataElement via `has_ownership_annotations`

### Database Schema Objects (Section 27)

**DatabaseConstraint** (is_a NamedEntity)

Represents a constraint on a database table or collection.

**Key Attributes:**
- `constraint_type` - DatabaseConstraintType (e.g., primary_key, foreign_key, unique, check, not_null, default)
- `columns` - Column names involved
- `reference_table` - Referenced table (for foreign keys)
- `reference_columns` - Referenced column names
- `expression` - Constraint expression (for check constraints)

**Relationships:**
- Connected to Collection

---

**DatabaseIndex** (is_a NamedEntity)

Represents an index on a database table or collection.

**Key Attributes:**
- `index_type` - IndexType (e.g., btree, hash, gin, gist, fulltext)
- `columns` - Indexed column names
- `is_unique` - Whether this is a unique index
- `is_partial` - Whether this is a partial/filtered index
- `filter_expression` - Filter expression (for partial indexes)

**Relationships:**
- Connected to Collection

### Programming Language (Section 28)

**ProgrammingLanguage** (is_a NamedEntity)

Represents a programming language and its characteristics, replacing the string-based `format` attribute on CodeContainer.

**Key Attributes:**
- `paradigms` - ProgrammingParadigm[] (e.g., object_oriented, procedural, functional, logic, declarative)
- `type_discipline` - Type discipline (e.g., static, dynamic, gradual, untyped)
- `has_preprocessor` - Whether the language has a preprocessor
- `has_gc` - Whether the language has garbage collection
- `year_introduced` - Year the language was introduced

**Relationships:**
- Connected to CodeContainer via `written_in_language` (replaces `format` string)
- Connected to ErrorModel
- Connected to MemoryModel

This code structure model provides complete traceability from high-level architecture down to individual lines of code, supporting analysis, documentation, and transformation across any programming paradigm.
