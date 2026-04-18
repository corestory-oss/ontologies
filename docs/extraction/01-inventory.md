# Phase 1: Inventory and Language Identification

**Input:** Raw repository (source tree, build manifests, lock files)
**Output:** **StorageLocation** hierarchy, skeletal **CodeContainer** instances, **ProgrammingLanguage** instances, **PackageManager**, **PackageDependency**

---

## 1. Overview

Phase 1 is the first extraction phase and the most mechanical. It walks the repository file tree and produces a complete inventory of where code lives, what languages are used, and what external packages the project depends on. Every subsequent phase builds on this inventory.

This phase is fully automatable and deterministic: given the same repository, it MUST produce the same output. No semantic reasoning is required -- only file-system traversal, extension mapping, and manifest parsing.

Why it comes first: every later phase needs to know which files exist, where they are, and what language they are written in. The **StorageLocation** hierarchy anchors the physical structure; **CodeContainer** instances become the targets that Phase 2 populates with parsed code elements.

---

## 2. Step 1: Build the StorageLocation hierarchy

Walk the repository file tree top-down. For each directory (or platform-equivalent namespace/package), create a **StorageLocation** instance.

### Required attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Directory or namespace name (e.g., `src`, `controllers`, `com.example.orders`) |
| `location_path` | string (required) | Relative path from the repository root (e.g., `src/main/java/com/example`) |
| `location_type` | `StorageLocationType` | One of the permissible values below |

### `location_type` permissible values

- `directory` -- standard filesystem directory
- `library` -- partitioned dataset or library (mainframe PDS)
- `package` -- language-level package (e.g., Java package, Python package with `__init__.py`)
- `namespace` -- language-level namespace (e.g., C# namespace, C++ namespace)
- `module_path` -- Go module path or similar module-level path

The extraction agent MUST choose the most specific applicable value. For a Java project, `src/main/java/com/example/orders` SHOULD be typed as `package`; its parent `src/main/java` SHOULD be typed as `directory`.

### Establishing the hierarchy

- Set `has_parent_location` on each child to reference its parent **StorageLocation**.
- Set `contains_locations` on each parent to list its children.
- The root **StorageLocation** (the repository root) has no `has_parent_location`.

### Module mapping

The attribute `maps_to_module` links a **StorageLocation** to a **Module** instance. In Phase 1, this SHOULD be left empty unless the mapping is unambiguous (e.g., a Go module root, a Python package with a clear `__init__.py`). Module identification is the responsibility of Phase 3.

### Directories to skip

The extraction agent SHOULD skip directories that do not contain meaningful source code:

- Version control directories (`.git`, `.svn`, `.hg`)
- Dependency directories (`node_modules`, `vendor`, `.venv`, `target`, `build`, `dist`)
- IDE directories (`.idea`, `.vscode` -- unless extracting IDE configuration is in scope)

---

## 3. Step 2: Create CodeContainer instances

For each source file in the repository, create a **CodeContainer** instance. Non-source files (binary assets, images, fonts) SHOULD be excluded unless they are relevant to the application's structure (e.g., compiled protobuf files).

### Required and recommended attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | string | inherited | File name without path (e.g., `UserService.java`) |
| `container_path` | string | yes | Full relative path from repository root (e.g., `src/main/java/com/example/UserService.java`) |
| `container_type` | `CodeContainerType` | recommended | Mapped from file extension (see table below) |
| `line_count` | integer | recommended | Total lines in the file |
| `size_bytes` | integer | optional | File size in bytes |
| `encoding` | string | optional | Character encoding (e.g., `utf-8`, `ebcdic`) |

### `container_type` permissible values

- `source_file` -- standard source code file
- `library_member` -- member of a partitioned dataset or library (mainframe)
- `include_file` -- shared definitions file (C/C++ header, COBOL copybook)
- `script` -- standalone script (shell, Python script, etc.)
- `configuration` -- configuration file (`application.yml`, `.env`, etc.)
- `schema_definition` -- schema file (OpenAPI, GraphQL, Protobuf, DDL)
- `notebook_cell` -- Jupyter notebook or similar
- `inline_code` -- inline code embedded in another artifact
- `jcl_member` -- JCL member in a PDS
- `rpg_source` -- RPG source member
- `pli_source` -- PL/I source member
- `assembler_source` -- assembler source member
- `cl_source` -- IBM CL (Control Language) source

### Extension-to-type mapping heuristic

The extraction agent SHOULD use file extensions to assign `container_type`. The following table covers common cases:

| Extensions | `container_type` |
|---|---|
| `.java`, `.py`, `.rs`, `.go`, `.ts`, `.js`, `.c`, `.cpp`, `.cs`, `.rb`, `.kt`, `.swift`, `.scala` | `source_file` |
| `.h`, `.hpp`, `.hxx` | `include_file` |
| `.cpy`, `.cbl`, `.cob` | `source_file` (COBOL) or `include_file` (copybook) |
| `.sh`, `.bash`, `.ps1`, `.bat`, `.cmd` | `script` |
| `.yml`, `.yaml`, `.json`, `.toml`, `.ini`, `.cfg`, `.properties`, `.env` | `configuration` |
| `.proto`, `.graphql`, `.gql`, `.xsd`, `.wsdl`, `.avsc` | `schema_definition` |
| `.ipynb` | `notebook_cell` |
| `.jcl` | `jcl_member` |
| `.rpg`, `.rpgle` | `rpg_source` |
| `.pli` | `pli_source` |
| `.asm`, `.s` | `assembler_source` |
| `.clp`, `.clle` | `cl_source` |

When a file extension is ambiguous (e.g., `.json` could be configuration or schema), the extraction agent SHOULD default to `configuration` and let later phases reclassify.

### Linking to StorageLocation

Each **CodeContainer** MUST set `contained_in_storage_location` to reference the **StorageLocation** for the directory that contains it. The inverse attribute `contains_containers` on the **StorageLocation** MUST also be populated.

### Linking to language

The attribute `written_in_language` links a **CodeContainer** to a **ProgrammingLanguage** instance. Populate this after Step 3 creates the language instances.

---

## 4. Step 3: Identify programming languages

Scan the **CodeContainer** instances created in Step 2. For each distinct programming language found, create a single **ProgrammingLanguage** instance.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Language name (e.g., `Java`, `Python`, `Rust`, `COBOL`) |
| `paradigms` | `ProgrammingParadigm` (multivalued) | Paradigms the language supports |
| `type_discipline` | string | Type system characterization (e.g., `static_strong`, `dynamic_strong`) |
| `has_preprocessor` | boolean | Whether the language has a preprocessor (e.g., `true` for C/C++) |
| `has_gc` | boolean | Whether the language has garbage collection |
| `year_introduced` | integer | Year the language was first released (optional) |

### `paradigms` permissible values

- `object_oriented`
- `procedural`
- `functional`
- `logic`
- `concatenative`
- `data_driven`
- `multi_paradigm`

### Common language profiles

| Language | `paradigms` | `type_discipline` | `has_gc` | `has_preprocessor` |
|---|---|---|---|---|
| Java | `object_oriented`, `multi_paradigm` | `static_strong` | `true` | `false` |
| Python | `object_oriented`, `procedural`, `functional`, `multi_paradigm` | `dynamic_strong` | `true` | `false` |
| TypeScript | `object_oriented`, `functional`, `multi_paradigm` | `static_strong` | `true` | `false` |
| C | `procedural` | `static_weak` | `false` | `true` |
| C++ | `object_oriented`, `procedural`, `functional`, `multi_paradigm` | `static_strong` | `false` | `true` |
| Rust | `functional`, `procedural`, `multi_paradigm` | `static_strong` | `false` | `true` |
| Go | `procedural`, `multi_paradigm` | `static_strong` | `true` | `false` |
| COBOL | `procedural` | `static_strong` | `false` | `true` |

### Linking containers to languages

After creating all **ProgrammingLanguage** instances, iterate over every **CodeContainer** and set `written_in_language` to the appropriate language based on file extension. The inverse attribute `language_used_by_containers` on the **ProgrammingLanguage** instance lists all containers using that language.

Configuration files, schema definitions, and other non-source containers MAY have `written_in_language` left empty, or MAY reference a markup/data language if one has been created (e.g., a YAML language instance).

---

## 5. Step 4: Parse dependency manifests

Identify build and dependency manifest files in the repository. For each package manager detected, create a **PackageManager** instance; for each declared dependency, create a **PackageDependency** instance.

### Identifying manifests

| Manifest file | `manager_type` |
|---|---|
| `package.json` | `npm` |
| `requirements.txt`, `setup.py`, `setup.cfg`, `pyproject.toml` (with pip/setuptools) | `pip` |
| `pom.xml` | `maven` |
| `build.gradle`, `build.gradle.kts` | `gradle` |
| `Cargo.toml` | `cargo` |
| `*.csproj`, `*.sln` (with NuGet references) | `nuget` |
| `go.mod` | `go_modules` |
| `Gemfile` | `bundler` |
| `composer.json` | `composer` |
| `conanfile.txt`, `conanfile.py` | `conan` |

### PackageManager attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Descriptive name (e.g., `npm`, `Maven Central`) |
| `manager_type` | `PackageManagerType` (required) | One of: `npm`, `pip`, `maven`, `gradle`, `nuget`, `cargo`, `go_modules`, `bundler`, `composer`, `conan`, `none` |
| `manifest_file` | string | Path to the manifest file (e.g., `package.json`) |
| `lock_file` | string | Path to the lock file (e.g., `package-lock.json`) |
| `registry_url` | URI | Package registry URL (e.g., `https://registry.npmjs.org`) |

### PackageDependency attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Instance name for the dependency |
| `package_name` | string (required) | Package identifier (e.g., `express`, `spring-boot-starter-web`) |
| `version_constraint` | string | Declared version range (e.g., `^4.18.0`, `>=3.0,<4.0`) |
| `resolved_version` | string | Actual resolved version from lock file (e.g., `4.18.2`) |
| `scope` | `DependencyScope` | One of the values below |
| `is_direct` | boolean | `true` for direct dependencies, `false` for transitive |
| `license` | string | SPDX license identifier if known (e.g., `MIT`, `Apache-2.0`) |

### `scope` permissible values

- `production` -- required at runtime
- `development` -- development-only tooling
- `test` -- test-only dependencies
- `build` -- build-time only
- `optional` -- optional/feature-gated
- `provided` -- expected to be provided by the runtime environment

### Scope mapping from ecosystems

| Ecosystem | Production | Development | Test |
|---|---|---|---|
| npm | `dependencies` | `devDependencies` | (convention-based) |
| Maven | `compile` scope | -- | `test` scope |
| Gradle | `implementation` | -- | `testImplementation` |
| pip | main requirements | `requirements-dev.txt` | `requirements-test.txt` |
| Cargo | `[dependencies]` | -- | `[dev-dependencies]` |

### Linking dependencies

**PackageDependency** links to a **Module** via `dependency_of_module`, and **PackageManager** links to a **Module** via `manages_dependencies_for_module`. In Phase 1, if a **Module** has not yet been created (modules are identified in Phase 3), the extraction agent SHOULD defer these links and record the association for later stitching.

For transitive dependencies (from lock files), set `is_direct` to `false` and use `has_transitive_dependencies` / `transitive_dependency_of` to establish the dependency graph between **PackageDependency** instances.

In Phase 1, the extraction agent SHOULD focus on direct dependencies. Transitive dependencies MAY be extracted from lock files if available, but full transitive graph construction is optional.

---

## 6. YAML output example

The following example shows Phase 1 output for a small Node.js project with three directories, four source files, one language, and three dependencies.

```yaml
# Phase 1 output: Inventory
# Project: my-api

storage_locations:
  - name: my-api
    location_path: "."
    location_type: directory
    contains_locations:
      - src-dir
      - src-routes-dir
    contains_containers:
      - package-json

  - id: src-dir
    name: src
    location_path: src
    location_type: directory
    parent_location: my-api
    contains_locations:
      - src-routes-dir
    contains_containers:
      - app-ts
      - db-ts

  - id: src-routes-dir
    name: routes
    location_path: src/routes
    location_type: directory
    parent_location: src-dir
    contains_containers:
      - users-ts

code_containers:
  - name: package.json
    container_path: package.json
    container_type: configuration
    line_count: 28
    contained_in_storage_location: my-api

  - id: app-ts
    name: app.ts
    container_path: src/app.ts
    container_type: source_file
    line_count: 45
    contained_in_storage_location: src-dir
    written_in_language: typescript-lang

  - id: db-ts
    name: db.ts
    container_path: src/db.ts
    container_type: source_file
    line_count: 22
    contained_in_storage_location: src-dir
    written_in_language: typescript-lang

  - id: users-ts
    name: users.ts
    container_path: src/routes/users.ts
    container_type: source_file
    line_count: 67
    contained_in_storage_location: src-routes-dir
    written_in_language: typescript-lang

programming_languages:
  - id: typescript-lang
    name: TypeScript
    paradigms:
      - object_oriented
      - functional
      - multi_paradigm
    type_discipline: static_strong
    has_gc: true
    has_preprocessor: false
    language_used_by_containers:
      - app-ts
      - db-ts
      - users-ts

package_managers:
  - name: npm
    manager_type: npm
    manifest_file: package.json
    lock_file: package-lock.json
    registry_url: https://registry.npmjs.org

package_dependencies:
  - name: express-dep
    package_name: express
    version_constraint: "^4.18.0"
    resolved_version: "4.18.2"
    scope: production
    is_direct: true
    license: MIT

  - name: pg-dep
    package_name: pg
    version_constraint: "^8.11.0"
    resolved_version: "8.11.3"
    scope: production
    is_direct: true
    license: MIT

  - name: typescript-dep
    package_name: typescript
    version_constraint: "^5.2.0"
    resolved_version: "5.3.3"
    scope: development
    is_direct: true
    license: Apache-2.0
```

---

## 7. Checklist

After Phase 1 completes, verify the following:

- [ ] Every source-relevant directory has a **StorageLocation** instance
- [ ] The **StorageLocation** hierarchy (via `has_parent_location` / `contains_locations`) matches the actual directory structure
- [ ] Every source file has a **CodeContainer** instance with `container_path` and `container_type` set
- [ ] Every **CodeContainer** is linked to its parent **StorageLocation** via `contained_in_storage_location`
- [ ] Every source-code **CodeContainer** has `written_in_language` set to a **ProgrammingLanguage** instance
- [ ] At least one **ProgrammingLanguage** instance exists with `paradigms` and `type_discipline` populated
- [ ] All build/dependency manifest files have been identified
- [ ] A **PackageManager** instance exists for each package manager detected
- [ ] All direct dependencies are captured as **PackageDependency** instances with `package_name`, `version_constraint`, and `scope`
- [ ] No files from excluded directories (`node_modules`, `.git`, `vendor`, etc.) are included

When all items pass, proceed to [Phase 2: Code Structure](02-code-structure.md).
