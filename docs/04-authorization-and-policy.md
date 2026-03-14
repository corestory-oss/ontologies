# Section 3: Authorization and Policy

This section defines the authorization model including roles, permissions, policies, scopes, and constraints.

> **v2.0 Note**: In SAO v2.0, all single-use relationship slots have been inlined as class attributes. Relationships and back-references are now defined directly on classes rather than referencing global `slots:` for single-domain relationships.

## Overview

The Authorization and Policy section provides a flexible, fine-grained access control model that supports multiple authorization paradigms including RBAC (Role-Based Access Control), ABAC (Attribute-Based Access Control), REBAC (Relationship-Based Access Control), and PBAC (Policy-Based Access Control).

## Core Concepts

### Role

**Definition**: A named collection of permissions assignable to actors.

**Purpose**: Groups permissions into meaningful job functions or responsibilities that can be assigned to identities.

**Key Attributes**:
- Inherits from `NamedEntity`
- **is_system_role**: Whether this is a built-in system role that cannot be deleted

**Relationships**:
- **grants_permissions**: `Permission` entities included in this role
- **assigned_to_identities**: `Identity` entities that have this role
- **inherits_from_role**: Parent role for role hierarchy
- **inherited_by_roles**: Child roles that inherit from this role *(v2.0 back-reference)*
- **can_access_features**: `Feature` entities accessible to this role *(v2.0 back-reference)*

**Role Patterns**:
- **Flat Roles**: Simple role assignments without hierarchy
- **Role Hierarchy**: Roles inherit permissions from parent roles
- **Parametric Roles**: Roles with parameters (e.g., Owner of Resource X)

**Example Roles**:
- **Administrator**: Full system access
- **User Manager**: Can create and manage users
- **Content Editor**: Can create and edit content
- **Viewer**: Read-only access
- **Billing Admin**: Can manage billing and subscriptions
- **Security Auditor**: Can view audit logs and security events

**Best Practices**:
1. Follow principle of least privilege
2. Create roles based on job functions, not individuals
3. Regularly audit role assignments
4. Use role hierarchy to reduce redundancy
5. Document the purpose and scope of each role

---

### Permission

**Definition**: A specific allowed action on a resource type or instance.

**Purpose**: Represents atomic units of access that can be granted or denied.

**Key Attributes**:
- Inherits from `NamedEntity`
- **constraints**: List of conditions that must be satisfied

**Relationships**:
- **allows_actions**: `Action` entities permitted by this permission
- **granted_by_roles**: `Role` entities that grant this permission
- **applies_to_resource_types**: `ResourceType` entities this permission governs
- **limited_by_scope**: `Scope` entity defining boundaries
- **required_by_capabilities**: `Capability` entities requiring this permission *(v2.0 back-reference)*
- **evaluated_by_policies**: `Policy` entities evaluating this permission *(v2.0 back-reference)*

**Permission Naming Conventions**:
- `<action>:<resource_type>` - e.g., `read:user`, `write:order`
- `<resource>:<action>` - e.g., `user:read`, `order:write`
- `<service>:<resource>:<action>` - e.g., `billing:invoice:create`

**Permission Granularity**:
- **Coarse-Grained**: `manage:users` (all user operations)
- **Fine-Grained**: `read:user:email` (specific field access)
- **Instance-Level**: `delete:order:123` (specific resource instance)

**Example Permissions**:
- `read:user` - Read user information
- `write:order` - Create or update orders
- `delete:comment` - Delete comments
- `execute:report:financial` - Run financial reports
- `admin:system` - Full system administration

---

### Policy

**Definition**: A rule set governing access decisions.

**Purpose**: Implements complex authorization logic that cannot be expressed through simple role-permission mappings.

**Key Attributes**:
- Inherits from `NamedEntity`
- **policy_type**: Type of policy
  - **RBAC**: Role-Based Access Control
  - **ABAC**: Attribute-Based Access Control
  - **REBAC**: Relationship-Based Access Control
  - **PBAC**: Policy-Based Access Control
- **rules**: List of rules within this policy
- **priority**: Evaluation priority (higher priority policies evaluated first)

**Relationships**:
- **evaluates_permissions**: `Permission` entities evaluated by this policy
- **enforced_by_system**: `System` that enforces this policy *(v2.0 inlined attribute)*
- **guards_routes**: `Route` entities guarded by this policy *(v2.0 inlined attribute)*

**Policy Types Explained**:

#### RBAC (Role-Based Access Control)
Access decisions based on roles assigned to identities.
- **Use Case**: Simple organizational hierarchies
- **Example**: "Users with 'Editor' role can edit articles"

#### ABAC (Attribute-Based Access Control)
Access decisions based on attributes of subject, resource, action, and environment.
- **Use Case**: Complex, context-dependent access rules
- **Example**: "Users can edit articles if article.status='draft' AND user.department=article.department"

#### REBAC (Relationship-Based Access Control)
Access decisions based on relationships between entities.
- **Use Case**: Social networks, collaborative applications
- **Example**: "Users can view files shared with them OR files in groups they are members of"

#### PBAC (Policy-Based Access Control)
Access decisions based on centrally defined policies.
- **Use Case**: Enterprise compliance, regulatory requirements
- **Example**: "Access to PHI requires MFA AND recent security training"

**Policy Evaluation Flow**:
1. Collect policies applicable to the request
2. Sort policies by priority
3. Evaluate each policy's rules
4. Combine results (allow, deny, not applicable)
5. Apply policy combination algorithm (deny-overrides, permit-overrides, etc.)

**Example Policies**:
- Data residency policy (GDPR compliance)
- Time-based access restrictions
- IP address allowlisting
- MFA requirement for sensitive operations
- Data classification-based access control

---

### Scope

**Definition**: A boundary limiting where a permission applies.

**Purpose**: Restricts permissions to specific contexts, reducing the blast radius of access grants.

**Key Attributes**:
- Inherits from `NamedEntity`
- **scope_type**: Type of scope
  - **GLOBAL**: System-wide global scope
  - **TENANT**: Limited to a specific tenant
  - **ORGANIZATION**: Limited to an organization within a tenant
  - **RESOURCE**: Limited to a specific resource or resource type
  - **FIELD**: Limited to specific fields within a resource
- **resource_pattern**: Pattern matching resources in scope (e.g., regex, glob)

**Relationships**:
- **limits_permissions**: `Permission` entities limited by this scope *(v2.0 back-reference)*

**Scope Hierarchies**:
```
GLOBAL
  └── TENANT (tenant_id=123)
       └── ORGANIZATION (org_id=456)
            └── RESOURCE (resource_type=order)
                 └── FIELD (field=payment_info)
```

**Example Scopes**:
- Global scope: System-wide access (administrators)
- Tenant scope: Access limited to tenant's data
- Organization scope: Department-specific access
- Resource scope: Access to specific resource types (e.g., only "draft" orders)
- Field scope: Access to specific fields (e.g., hide salary information)

**Scope Pattern Matching**:
- **Exact Match**: `resource_id=12345`
- **Wildcard**: `resource_type=order:*`
- **Attribute Match**: `status=published`
- **Path Pattern**: `/tenants/*/users/*`

---

### Constraint

**Definition**: A condition that must be satisfied for authorization.

**Purpose**: Adds contextual or temporal restrictions to permissions.

**Key Attributes**:
- Inherits from `NamedEntity`
- **constraint_type**: Type of constraint
  - **TEMPORAL**: Time-based constraint (date/time ranges)
  - **SPATIAL**: Location or geography-based constraint
  - **ATTRIBUTE**: Attribute or property-based constraint
  - **CONTEXT**: Context-dependent constraint (device, IP, etc.)
  - **RATE_LIMIT**: Rate limiting or quota-based constraint
- **expression**: Constraint expression (e.g., "hour >= 9 AND hour <= 17")
- **parameters**: Constraint parameters

**Constraint Types Explained**:

#### TEMPORAL Constraints
Access allowed only during specific time periods.
- **Examples**:
  - Business hours only: "Monday-Friday, 9am-5pm"
  - Embargo period: "Not before 2024-01-01"
  - Expiration: "Access expires on 2024-12-31"

#### SPATIAL Constraints
Access restricted by geographic location.
- **Examples**:
  - Country restriction: "user.country IN ['US', 'CA', 'MX']"
  - Office location: "user.location = 'HQ'"
  - IP range: "request.ip IN office_ip_ranges"

#### ATTRIBUTE Constraints
Access based on resource or user attributes.
- **Examples**:
  - Ownership: "resource.owner_id = user.id"
  - Department match: "user.department = resource.department"
  - Classification: "user.clearance_level >= resource.classification_level"

#### CONTEXT Constraints
Access based on request context.
- **Examples**:
  - Device type: "device.type = 'corporate_managed'"
  - Network: "request.network = 'corporate_vpn'"
  - Authentication method: "auth.method = 'MFA'"

#### RATE_LIMIT Constraints
Access limited by usage quotas.
- **Examples**:
  - API rate limit: "100 requests per minute"
  - Download quota: "10 GB per day"
  - Concurrent sessions: "Maximum 5 active sessions"

**Constraint Evaluation**:
Constraints are evaluated at authorization time, and access is granted only if all constraints are satisfied.

**Example Constraints**:
```
Temporal: "access_time.hour >= 9 AND access_time.hour <= 17 AND access_time.day_of_week IN ['MON','TUE','WED','THU','FRI']"

Spatial: "user.ip_address IN corporate_ip_ranges"

Attribute: "user.clearance_level >= 'SECRET' AND user.training.security_awareness.completed = true"

Context: "request.mfa_verified = true AND device.trusted = true"

Rate Limit: "api_calls.count(last_1_hour) <= 1000"
```

---

## Authorization Patterns

### Simple RBAC
1. Identity has one or more Roles
2. Roles grant Permissions
3. Permissions allow Actions on ResourceTypes
4. Decision: Allow if identity has required permission

### RBAC with Constraints
1. Basic RBAC decision
2. Evaluate constraints on permission
3. Decision: Allow if permission exists AND all constraints satisfied

### ABAC with Policies
1. Identify applicable policies for request
2. Evaluate policy rules using attributes of:
   - Subject (identity, roles, attributes)
   - Resource (type, attributes, owner)
   - Action (operation type)
   - Environment (time, location, context)
3. Combine policy decisions
4. Decision: Based on policy combination algorithm

### REBAC (Relationship-Based)
1. Identify relationships between identity and resource
2. Check if relationship grants required permission
3. Decision: Allow if relationship exists with sufficient permission

### Hierarchical RBAC
1. Resolve role hierarchy (inherit permissions from parent roles)
2. Collect all permissions from all roles
3. Evaluate constraints on each permission
4. Decision: Allow if any permission grants access

---

## Best Practices

### Permission Design
1. **Granularity**: Balance between too coarse (security risk) and too fine (management complexity)
2. **Naming**: Use consistent, descriptive naming conventions
3. **Documentation**: Document the purpose and scope of each permission
4. **Least Privilege**: Grant minimum necessary permissions

### Role Design
1. **Job Functions**: Base roles on actual job functions, not individuals
2. **Separation of Duties**: Prevent conflicts of interest through role separation
3. **Regular Review**: Audit role assignments periodically
4. **Dynamic Roles**: Support temporary role assignments for special projects

### Policy Design
1. **Principle of Least Privilege**: Default deny, explicit allow
2. **Defense in Depth**: Layer multiple authorization mechanisms
3. **Clear Precedence**: Define clear policy evaluation order
4. **Testing**: Test policies with various scenarios before deployment

### Scope Management
1. **Hierarchical Scopes**: Use scope hierarchies for easier management
2. **Pattern Matching**: Use resource patterns to avoid explicit enumeration
3. **Inheritance**: Allow scope inheritance down organizational hierarchy

### Constraint Implementation
1. **Performance**: Evaluate lightweight constraints before expensive ones
2. **Caching**: Cache constraint evaluations when appropriate
3. **Failure Modes**: Define behavior when constraint evaluation fails
4. **Monitoring**: Track constraint violations for security monitoring

---

## Security Considerations

### Authorization Bypass Prevention
- Enforce authorization at API gateway and service layers
- Never rely on client-side authorization checks
- Use cryptographic signatures to prevent parameter tampering
- Audit all authorization decisions

### Privilege Escalation Prevention
- Restrict permission to grant permissions (delegation)
- Prevent circular role inheritance
- Validate all authorization changes
- Implement approval workflows for sensitive permissions

### Performance and Scalability
- Cache authorization decisions when appropriate
- Use efficient policy evaluation algorithms
- Implement authorization decision caching
- Monitor authorization system performance

### Compliance
- Support separation of duties requirements
- Implement audit logging for all authorization decisions
- Support time-limited access grants
- Enable access recertification processes

---

## Relationships with Other Sections

- **Section 2 (Actors and Identity)**: Identities have roles; actors perform authorized actions
- **Section 4 (Domain Modeling)**: Permissions target resources and resource types
- **Section 5 (Behavior)**: Actions are subject to authorization
- **Section 6 (Data Management)**: Authorization decisions are audited
- **Section 10 (Governance)**: Compliance requirements drive authorization policies

---

## Common Authorization Scenarios

### Document Editing System
```
Role: Editor
Permissions:
  - read:document (scope: tenant)
  - write:document (scope: tenant, constraint: owner OR collaborator)
  - delete:document (scope: tenant, constraint: owner ONLY)

Policy: Time-Based Editing
Rules:
  - Allow write:document IF current_time BETWEEN 9am-5pm
  - Deny write:document on weekends
```

### Healthcare System (HIPAA Compliance)
```
Role: Clinician
Permissions:
  - read:patient_record (scope: assigned_patients, constraint: active_treatment)
  - write:clinical_note (scope: assigned_patients)

Policy: PHI Access Control
Rules:
  - Require MFA for PHI access
  - Allow access only from corporate network
  - Log all PHI access for audit
  - Deny access if security training expired
```

### Multi-Tenant SaaS Platform
```
Role: Tenant Admin
Permissions:
  - manage:users (scope: tenant)
  - configure:settings (scope: tenant)
  - view:billing (scope: tenant)

Constraints:
  - Spatial: Access only from approved countries
  - Rate Limit: Max 1000 API calls per hour
  - Temporal: No billing access during month-end close
```

### Collaborative Platform (REBAC)
```
Relationships:
  - user OWNS resource
  - user COLLABORATES_ON resource
  - user MEMBER_OF group
  - group HAS_ACCESS_TO resource

Permissions derived from relationships:
  - Owner: read, write, delete, share
  - Collaborator: read, write
  - Group Member: read (if group has access)
```
