# Section 6: Data Management

This section defines data stores, collections, records, schemas, data classification, retention policies, data lineage, and audit logging.

> **v2.0 Note**: In SAO v2.0.0, many cross-entity relationships are now inlined directly on the owning class rather than declared as standalone slot references. Classes such as `Schema`, `DataStore`, and `RetentionPolicy` gain back-reference attributes that make navigating the ontology more explicit. Additionally, `SchemaVersion` and `AuditEntry` have been restructured from subclass inheritance to composition (they are now `is_a: NamedEntity` with explicit reference attributes back to their parent).

## Overview

The Data Management section provides comprehensive modeling of data persistence, schema management, data governance, and audit trails.

## Core Concepts

### DataStore

**Definition**: A persistence mechanism for storing data.

**Key Attributes**:
- **store_type**: `relational_db`, `document_db`, `key_value_store`, `graph_db`, `time_series_db`, `object_storage`, `search_index`, `cache`, `message_broker`, `data_lake`, `vsam`, `flat_file`, `isam`, `dead_letter_queue`
- **connection_string**: Connection configuration
- **collections**: List of collections/tables

**Relationships**:
- **hosted_on_infrastructure**: `Infrastructure` hosting the data store
- **persists_aggregates**: `Aggregate` entities stored
- **store_read_by_pipelines**: `DataPipeline` entities that read from this store
- **store_written_by_pipelines**: `DataPipeline` entities that write to this store
- **store_file_definitions**: `FileDefinition` entities associated with this store

**Data Store Types**:
- `relational_db`: SQL databases (PostgreSQL, MySQL, Oracle)
- `document_db`: NoSQL document stores (MongoDB, CouchDB)
- `key_value_store`: KV stores (Redis, DynamoDB)
- `graph_db`: Graph databases (Neo4j, ArangoDB)
- `time_series_db`: Time-series databases (InfluxDB, TimescaleDB)
- `object_storage`: Object stores (S3, Azure Blob)
- `search_index`: Search engines (Elasticsearch, Solr)
- `cache`: In-memory caches (Redis, Memcached)
- `message_broker`: Message queues (Kafka, RabbitMQ)
- `data_lake`: Analytics data lakes (S3, ADLS)
- `vsam`: IBM VSAM dataset
- `flat_file`: Sequential or flat file
- `isam`: Indexed Sequential Access Method file
- `dead_letter_queue`: Dead letter queue

---

### Collection

**Definition**: A logical grouping of records (table, collection, bucket).

**Key Attributes**:
- **indexes**: Index definitions for query performance (**deprecated** in v2.0 -- use `has_indexes` instead)

**Relationships**:
- **collection_structured_by_schema**: `Schema` defining structure
- **governed_by_retention_policy**: `RetentionPolicy` for data lifecycle
- **stores_records**: `Record` instances
- **has_constraints**: `DatabaseConstraint[]` (inlined) -- constraint definitions for this collection (see Section 27)
- **has_indexes**: `DatabaseIndex[]` (inlined) -- index definitions for this collection (see Section 27)

**Collection Patterns**:
- **Relational Table**: Structured rows with fixed schema
- **Document Collection**: Flexible JSON documents
- **Object Bucket**: Binary objects with metadata
- **Event Stream**: Append-only log of events

---

### Record

**Definition**: A single persisted instance of data.

**Key Attributes**:
- **classifications**: Data sensitivity classifications

**Relationships**:
- **stored_in_collection**: Parent `Collection`
- **conforms_to_schema**: `Schema` for validation
- **has_lineage**: `DataLineage` tracking origin and transformations

---

### Schema

**Definition**: Structural definition of stored data.

**Key Attributes**:
- Implements `Versionable` mixin
- **schema_type**: `table_schema`, `document_schema`, `event_schema`, `api_schema`, `message_schema`
- **definition**: Schema definition (JSON Schema, DDL, etc.)
- **schema_versions**: List of `SchemaVersion` entities (v2.0 back-reference)

**Back-Reference Attributes** (v2.0):
- **structures_resource_types**: `ResourceType` entities structured by this schema
- **structures_collections**: `Collection` entities structured by this schema
- **structures_events**: `Event` entities structured by this schema
- **structures_messages**: `Message` entities structured by this schema
- **defines_operation_input**: `Operation` entities using this schema as input
- **defines_operation_output**: `Operation` entities using this schema as output
- **validates_records**: `Record` entities validated by this schema

**Schema Evolution**:
- **Backward Compatible**: New schema can read old data
- **Forward Compatible**: Old schema can read new data
- **Breaking Change**: Incompatible schema change

**Example Schema Types**:
- `table_schema`: SQL CREATE TABLE statement
- `document_schema`: JSON Schema for documents
- `event_schema`: Event payload schema
- `api_schema`: OpenAPI/GraphQL schema
- `message_schema`: Message format schema

---

### SchemaVersion

**Definition**: A specific iteration of a schema.

> **v2.0 Change**: `SchemaVersion` is now `is_a: NamedEntity` (previously `is_a: Schema`). Instead of inheriting from `Schema`, it uses the `version_of_schema` attribute to reference its parent `Schema`.

**Key Attributes**:
- **version**: Semantic version number
- **definition**: Schema at this version
- **migration_script**: Migration from previous version
- **is_backward_compatible**: Compatibility flag

**Relationships**:
- **version_of_schema**: `Schema` that this version belongs to

**Schema Versioning Best Practices**:
1. Use semantic versioning
2. Provide migration scripts
3. Test backward compatibility
4. Document breaking changes
5. Support multiple versions during transition

---

### DataClassification

**Definition**: A sensitivity or handling category for data.

**Key Attributes**:
- **classification_type**: `public`, `internal`, `confidential`, `restricted`, `pii`, `phi`, `pci`
- **handling_requirements**: Required procedures
- **encryption_required**: Encryption flag

**Classification Levels**:
- `public`: Publicly accessible information
- `internal`: Internal use only
- `confidential`: Sensitive business information
- `restricted`: Highly restricted access
- `pii`: Personally Identifiable Information (GDPR)
- `phi`: Protected Health Information (HIPAA)
- `pci`: Payment Card Industry data (PCI-DSS)

**Handling Requirements**:
- Encryption at rest and in transit
- Access logging and monitoring
- Data masking for non-production environments
- Secure deletion procedures
- Access control restrictions

---

### RetentionPolicy

**Definition**: Rules governing data lifecycle and deletion.

**Key Attributes**:
- **retention_days**: Days to retain data
- **archive_after_days**: Days before archiving
- **deletion_strategy**: How data is deleted (soft delete, hard delete, anonymize)

**Back-Reference Attributes** (v2.0):
- **governs_collections**: `Collection` entities governed by this policy
- **governs_logs**: `Log` entities governed by this policy
- **governs_audit_logs**: `AuditLog` entities governed by this policy

**Retention Strategies**:
- **Legal Hold**: Prevent deletion for legal reasons
- **Compliance-Driven**: Based on regulatory requirements (GDPR, HIPAA, SOX)
- **Business-Driven**: Based on business needs
- **Automatic Archival**: Move to cheaper storage after period
- **Secure Deletion**: Cryptographic erasure or overwriting

**Example Retention Policies**:
- **User Data**: 7 years retention (GDPR compliance)
- **Application Logs**: 90 days retention, archive to cold storage after 30 days
- **Audit Logs**: 10 years retention (regulatory requirement)
- **Session Data**: 24 hours retention
- **Temporary Files**: Delete after 7 days

---

### DataLineage

**Definition**: The origin, transformation history, and movement of data.

**Key Attributes**:
- **source**: Original data source
- **transformations**: List of transformations applied

**Relationships**:
- **derived_from_records**: Source `Record` entities
- **tracks_record**: Target `Record` being tracked

**Lineage Use Cases**:
- **Compliance**: Demonstrate data provenance for regulations
- **Debugging**: Trace data quality issues to source
- **Impact Analysis**: Understand downstream effects of changes
- **Optimization**: Identify redundant transformations

**Lineage Tracking Levels**:
- **Table-Level**: Track dataset dependencies
- **Column-Level**: Track field-level lineage
- **Record-Level**: Track individual record transformations

---

### AuditLog

**Definition**: A tamper-evident record of system activities.

**Key Attributes**:
- **entries**: List of `AuditEntry` records
- **audit_log_entries**: `AuditEntry[]` (v2.0 back-reference from `AuditEntry.entry_in_audit_log`)

**Relationships**:
- **auditlog_governed_by_retention**: `RetentionPolicy` for log retention

**Audit Log Requirements**:
- Immutability (write-once)
- Tamper-evidence (cryptographic signatures)
- Completeness (all actions logged)
- Accuracy (correct timestamps, actors)
- Availability (accessible for audits)

---

### AuditEntry

**Definition**: A single record within an audit log.

> **v2.0 Change**: `AuditEntry` is now `is_a: NamedEntity` (previously `is_a: AuditLog`). Instead of inheriting from `AuditLog`, it uses the `entry_in_audit_log` attribute to reference its parent `AuditLog`. Conversely, `AuditLog` now has the `audit_log_entries` back-reference attribute.

**Key Attributes**:
- **timestamp**: When the event occurred (required)
- **outcome**: Result of the action (success, failure, error)
- **details**: Additional context

**Relationships**:
- **entry_in_audit_log**: `AuditLog` that this entry belongs to
- **audit_performed_by_actor**: `Actor` who performed action
- **records_action**: `Action` that was performed
- **affects_resource**: `Resource` affected

**Audit Entry Contents**:
- **Who**: Actor/identity performing action
- **What**: Action performed
- **When**: Timestamp of action
- **Where**: Source IP, location, service
- **Why**: Context or reason (if available)
- **Result**: Success or failure

**Audit Event Examples**:
- User login/logout
- Permission changes
- Data access (especially PII/PHI)
- Configuration changes
- System events (start, stop, deploy)
- Security events (failed auth, suspicious activity)

---

## Data Management Patterns

### Polyglot Persistence
Use different data stores for different use cases:
- Relational DB for transactional data
- Document DB for flexible schemas
- Cache for frequently accessed data
- Search index for full-text search
- Time-series DB for metrics

### CQRS (Command Query Responsibility Segregation)
Separate read and write data models:
- Write model: Optimized for updates
- Read model: Optimized for queries
- Synchronization via events

### Event Sourcing
Store events as source of truth:
- Append-only event log
- Rebuild state by replaying events
- Complete audit trail
- Time travel capabilities

### Data Lake Pattern
Centralized repository for all data:
- Raw data in native format
- Schema-on-read
- Support for batch and stream processing
- Analytics and ML use cases

---

## Best Practices

### Schema Management
1. **Version Control**: Store schemas in version control
2. **Validation**: Validate data against schemas
3. **Evolution**: Plan for schema evolution
4. **Documentation**: Document schema fields and semantics

### Data Classification
1. **Automatic Classification**: Auto-detect and classify sensitive data
2. **Labeling**: Tag data with classification labels
3. **Enforcement**: Enforce handling requirements automatically
4. **Monitoring**: Monitor access to classified data

### Retention and Archival
1. **Automated Policies**: Implement automated retention policies
2. **Compliance**: Align with regulatory requirements
3. **Cost Optimization**: Archive to cheaper storage
4. **Verification**: Regularly verify retention compliance

### Audit Logging
1. **Comprehensive**: Log all security-relevant events
2. **Integrity**: Ensure logs cannot be tampered
3. **Availability**: Make logs accessible for investigation
4. **Analysis**: Use SIEM tools for log analysis
5. **Privacy**: Protect sensitive data in logs

### Data Lineage
1. **Automated Tracking**: Automatically capture lineage metadata
2. **Visualization**: Provide lineage visualization tools
3. **Granularity**: Track at appropriate level (table, column, record)
4. **Integration**: Integrate with data catalog and governance tools

---

## Relationships with Other Sections

- **Section 4 (Domain Modeling)**: Aggregates persisted in data stores
- **Section 5 (Behavior)**: Actions recorded in audit logs
- **Section 7 (Integration)**: Message schemas for integration
- **Section 8 (Deployment)**: Data stores hosted on infrastructure
- **Section 9 (Observability)**: Logs stored with retention policies
- **Section 10 (Governance)**: Compliance requirements drive retention policies

---

## Example: E-Commerce Data Architecture

```
DataStores:
  - ProductDB (relational_db)
    - Collections: products, categories, inventory
    - Schema: Relational table schemas
    - Retention: 7 years

  - OrderDB (relational_db)
    - Collections: orders, order_items, payments
    - Classification: pci for payment data
    - Retention: 10 years (compliance)
    - Audit: All access logged

  - SessionCache (cache)
    - Collections: user_sessions
    - Retention: 24 hours

  - ProductSearch (search_index)
    - Collections: product_index
    - Schema: Product search schema
    - Sync: From ProductDB via events

  - EventStore (message_broker)
    - Collections: domain_events
    - Schema: Event schemas (versioned)
    - Retention: 30 days, archive to data lake

Data Lineage Example:
  - Raw Product Data (from supplier API)
    -> Enrichment (add images, descriptions)
    -> Validation (check required fields)
    -> Normalization (standardize formats)
    -> ProductDB (transactional storage)
    -> ProductSearch (indexed for search)
    -> AnalyticsDB (for reporting)
```
