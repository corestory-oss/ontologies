# Code Structure

The Code Structure layer provides a paradigm-agnostic framework for modeling software applications at the implementation level. This layer bridges the gap between architectural concepts (Components, Operations) and the actual source code that implements them, supporting both modern and legacy systems.

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
- `format` - Language or format (COBOL, Java, Python, SQL, etc.)
- `size_bytes` - Size in bytes
- `line_count` - Number of lines
- `encoding` - Character encoding
- `checksum` - Content hash for version tracking

**Container Types:**
- `source_file` - Standard source code file
- `library_member` - Member of a partitioned dataset or library (mainframe)
- `include_file` - Header or include file
- `script` - Executable script
- `configuration` - Configuration file
- `schema_definition` - Database or API schema
- `notebook_cell` - Jupyter notebook cell
- `inline_code` - Embedded code (JavaScript in HTML, SQL in application)

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
- `parent_location` - Parent storage location (hierarchical)
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
- `visibility` - Visibility level (public, private, protected, internal, package, module)
- `qualified_name` - Fully qualified name (e.g., com.example.UserService)
- `stereotype` - Additional stereotype (Service, Repository, DTO, Controller, etc.)
- `is_abstract` - Whether this is abstract/incomplete
- `is_final` - Whether this can be extended
- `is_static` - Whether this is static/stateless

**EncapsulationType Values** (31 total):

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

**Database:**
- `stored_procedure` - Database stored procedure package
- `function_package` - Function package (Oracle)
- `trigger` - Database trigger
- `view` - Database view

**Other:**
- `object` - Module-level object (Scala)
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
- `is_abstract` - Whether this is abstract
- `is_virtual` - Whether this is virtual/overridable
- `complexity_score` - Cyclomatic complexity or similar metric
- `entry_point_type` - If this is an entry point (main, constructor, handler, etc.)

**CallableType Values** (48 total):

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
- `raises_exceptions` - Exceptions that may be raised
- `handles_exceptions` - Exceptions handled
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

**DataStructureType Values** (43 total):

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
- `parent_structure` - Parent structure (for nested structures)
- `child_structures` - Child/nested structures
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
- `element_type` - Type of element (field, property, variable, constant, parameter)
- `data_type` - Data type (string, integer, User, etc.)
- `visibility` - Visibility level
- `is_static` - Whether this is static
- `is_final` - Whether this is final/immutable
- `is_nullable` - Whether this can be null
- `default_value` - Default value
- `min_occurs` - Minimum occurrences (for arrays)
- `max_occurs` - Maximum occurrences

**Relationships:**
- `contained_in_unit` - Encapsulation unit containing this element
- `contained_in_structure` - Data structure containing this element
- `parent_element` - Parent element (for nested fields)
- `has_type_definition` - Type definition reference

**Example:**
```yaml
user_email:
  a: DataElement
  name: email
  element_type: field
  data_type: String
  visibility: private
  is_nullable: false
  contained_in_structure: user_data
```

### Parameter

Function/method parameter.

**Key Attributes:**
- `parameter_type` - Type (input, output, input_output, return, variadic)
- `data_type` - Data type
- `position` - Position in parameter list
- `is_optional` - Whether this is optional
- `default_value` - Default value
- `passing_mechanism` - How passed (by_value, by_reference, by_name)

**Example:**
```yaml
username_param:
  a: Parameter
  name: username
  parameter_type: input
  data_type: String
  position: 1
  is_optional: false
  parameter_of: create_user
```

## Semantic Code Structure

### CodeBlock

A logical block of code (conditional, loop, try-catch, etc.).

**Key Attributes:**
- `block_type` - Type (conditional, loop, try_catch, synchronized, etc.)
- `condition` - Condition expression
- `nesting_level` - Nesting depth

### Statement

Individual code statement.

**Key Attributes:**
- `statement_type` - Type (assignment, invocation, return, declaration, etc.)
- `line_number` - Source line number
- `complexity_contribution` - Contribution to complexity

### ControlFlow

Control flow between code elements (calls, branches, etc.).

**Key Attributes:**
- `flow_type` - Type (call, conditional_branch, unconditional_branch, loop, etc.)
- `is_conditional` - Whether flow is conditional
- `condition` - Condition expression

**Relationships:**
- `source_callable` - Source callable
- `target_callable` - Target callable
- `source_statement` - Source statement
- `target_statement` - Target statement

### DataFlow

Data flow between elements.

**Key Attributes:**
- `flow_type` - Type (parameter_passing, return_value, field_access, assignment, etc.)
- `data_type` - Type of data flowing

**Relationships:**
- `source_element` - Source data element
- `target_element` - Target data element

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

- **VisibilityType**: public, private, protected, internal, package, module, file
- **CallableCategory**: synchronous, asynchronous, event_driven, reactive
- **EntryPointType**: main, constructor, destructor, initializer, event_handler, callback
- **DataStructureCategory**: simple, composite, collection, reference
- **DataElementCategory**: field, property, variable, constant, parameter
- **ParameterDirection**: input, output, input_output, return
- **PassingMechanism**: by_value, by_reference, by_name, by_need
- **CodeBlockType**: conditional, loop, try_catch, synchronized, transaction, scope
- **StatementCategory**: assignment, invocation, return, declaration, control, exception
- **ReferenceType**: import, include, using, require, copy
- **ControlFlowType**: call, conditional_branch, unconditional_branch, loop, exception
- **DataFlowType**: parameter_passing, return_value, field_access, assignment, reference

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

This code structure model provides complete traceability from high-level architecture down to individual lines of code, supporting analysis, documentation, and transformation across any programming paradigm.
