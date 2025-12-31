# Section 2: Actors and Identity

This section defines entities and actors that interact with the system, along with their identity and organizational structures.

## Overview

The Actors and Identity section provides a comprehensive model for representing who or what can perform actions within the system, how they are authenticated, and how they are organized within tenants and organizational hierarchies.

## Core Concepts

### Actor

**Definition**: Any entity that can initiate actions within the system (abstract base class).

**Purpose**: Provides a unified abstraction for both human users and automated systems that interact with the application.

**Key Attributes**:
- Inherits from `NamedEntity`
- **category**: Actor category (HUMAN, SYSTEM)

**Relationships**:
- **has_identities**: One or more `Identity` entities associated with this actor

**Specialized Actor Types**:

#### HumanActor
A human user of the system.

**Attributes**:
- **actor_type**: Type of human actor
  - **END_USER**: Regular end user of the system
  - **ADMINISTRATOR**: System administrator with elevated privileges
  - **OPERATOR**: Operations personnel managing system runtime
  - **DEVELOPER**: Software developer or engineer
  - **AUDITOR**: Compliance or security auditor
- **email**: Contact email address

**Example Use Cases**:
- Customer purchasing products
- System administrator managing users
- DevOps engineer deploying services
- Security auditor reviewing access logs

#### SystemActor
A system or automated actor.

**Attributes**:
- **actor_type**: Type of system actor
  - **INTERNAL_SERVICE**: Internal service within the system
  - **EXTERNAL_SYSTEM**: External third-party system
  - **SCHEDULED_PROCESS**: Scheduled or cron-based process
  - **AI_AGENT**: Artificial intelligence agent or bot
  - **MESSAGE_TRIGGER**: Message or event-triggered automation
- **service_account**: Service account identifier

**Example Use Cases**:
- Microservice calling another service
- External payment gateway
- Nightly batch job
- Chatbot assistant
- Webhook handler

---

### Identity

**Definition**: A verified representation of an actor within the system.

**Purpose**: Represents the authenticated identity of an actor, which can have multiple roles and credentials.

**Key Attributes**:
- Inherits from `NamedEntity`
- **identity_type**: Type of identity (user, service, device)
- **credentials**: List of associated credentials

**Relationships**:
- **represents_actor**: The `Actor` this identity represents
- **has_roles**: `Role` entities assigned to this identity
- **belongs_to_tenant**: The `Tenant` this identity belongs to
- **member_of_organizations**: `Organization` entities this identity is a member of

**Identity Types**:
- **User Identity**: Represents a human user account
- **Service Identity**: Represents a service account for automation
- **Device Identity**: Represents a registered device

**Example Use Cases**:
- User account with email/password authentication
- Service account for CI/CD pipeline
- OAuth identity from third-party provider
- Device registration for mobile app

---

### Credential

**Definition**: Authentication material proving an identity claim.

**Purpose**: Represents the means by which an identity can be authenticated.

**Key Attributes**:
- Inherits from `NamedEntity`
- **credential_type**: Type of credential
  - **PASSWORD**: Username and password credentials
  - **TOKEN**: Token-based authentication (JWT, bearer token)
  - **CERTIFICATE**: Digital certificate or X.509 certificate
  - **API_KEY**: API key for service authentication
  - **BIOMETRIC**: Biometric authentication (fingerprint, face recognition)
  - **MFA**: Multi-factor authentication
  - **OAUTH**: OAuth 2.0 authentication flow
- **expires_at**: Expiration timestamp
- **is_active**: Whether the credential is currently active

**Credential Lifecycle**:
1. **Creation**: Credential is generated or registered
2. **Active**: Credential can be used for authentication
3. **Rotation**: New credential replaces old one (for tokens, API keys)
4. **Expiration**: Credential expires based on policy
5. **Revocation**: Credential is explicitly invalidated

**Security Best Practices**:
- Store passwords using strong hashing algorithms (bcrypt, Argon2)
- Implement credential rotation policies for tokens and API keys
- Require MFA for privileged operations
- Use short-lived tokens with refresh token patterns
- Audit all credential usage

**Example Use Cases**:
- User password for login
- JWT token for API authentication
- X.509 certificate for mutual TLS
- API key for external integrations
- Biometric fingerprint for mobile app

---

### Tenant

**Definition**: An organizational boundary for multi-tenant systems.

**Purpose**: Isolates data and configuration for different customers or organizational units in a multi-tenant application.

**Key Attributes**:
- Inherits from `NamedEntity`
- **organizations**: List of organizations within this tenant
- **settings**: Tenant-specific configuration

**Relationships**:
- **contains_identities**: `Identity` entities within this tenant

**Multi-Tenancy Patterns**:
- **Single Database, Shared Schema**: All tenants share the same database and schema with tenant ID filtering
- **Single Database, Separate Schemas**: Each tenant has its own schema in a shared database
- **Separate Databases**: Each tenant has a completely isolated database

**Tenant Isolation Strategies**:
- Row-level security with tenant ID
- Schema-level isolation
- Database-level isolation
- Application-level filtering

**Example Use Cases**:
- Enterprise customer account in SaaS platform
- Regional division of a multinational company
- Department in a university system
- Franchise location in retail chain

---

### Organization

**Definition**: A logical grouping of users and resources within a tenant.

**Purpose**: Provides hierarchical organization structure within a tenant for managing users, permissions, and resources.

**Key Attributes**:
- Inherits from `NamedEntity`
- **parent**: Parent organization for hierarchical structures
- **children**: Child organizations

**Relationships**:
- **has_identity_members**: `Identity` entities that are members of this organization

**Organizational Hierarchies**:
- **Flat**: Single-level organizations within a tenant
- **Hierarchical**: Tree structure of organizations
- **Matrix**: Organizations with multiple reporting relationships

**Use Cases for Organizations**:
- Department structure (Engineering, Sales, Marketing)
- Geographic regions (North America, EMEA, APAC)
- Business units (Retail, Wholesale, E-commerce)
- Project teams or workgroups

**Permission Inheritance**:
Organizations can be used with organizational scopes to inherit permissions down the hierarchy.

**Example Use Cases**:
- Engineering department with sub-teams (Frontend, Backend, DevOps)
- Regional sales offices under global sales organization
- Product teams within engineering division
- Store locations within retail chain

---

## Identity and Access Management Patterns

### Single Sign-On (SSO)
An identity can authenticate once and access multiple systems through integration with identity providers (SAML, OAuth, OpenID Connect).

### Federated Identity
Identities can be federated from external identity providers (Google, Microsoft, Okta) while maintaining local role assignments.

### Service-to-Service Authentication
System actors use service identities with certificate-based or token-based credentials for secure inter-service communication.

### Identity Lifecycle Management
1. **Provisioning**: Creating new identities
2. **Authentication**: Verifying identities with credentials
3. **Authorization**: Assigning roles and permissions
4. **Modification**: Updating identity attributes and roles
5. **Suspension**: Temporarily disabling identities
6. **Deprovisioning**: Removing identities and revoking access

---

## Best Practices

### Identity Management
1. **Unique Identifiers**: Use immutable, globally unique identifiers for identities
2. **Email Verification**: Verify email addresses during registration
3. **Account Recovery**: Implement secure password reset flows
4. **Activity Tracking**: Log all identity changes for audit purposes

### Credential Management
1. **Strong Password Policies**: Enforce minimum complexity requirements
2. **Credential Rotation**: Require periodic password changes and token rotation
3. **MFA Enforcement**: Require multi-factor authentication for sensitive operations
4. **Secure Storage**: Never store credentials in plain text
5. **Rate Limiting**: Implement login attempt rate limiting

### Tenant Management
1. **Data Isolation**: Ensure complete data isolation between tenants
2. **Resource Quotas**: Implement resource limits per tenant
3. **Tenant-Specific Configuration**: Allow tenants to customize settings
4. **Tenant Lifecycle**: Support tenant provisioning, suspension, and deletion

### Organization Management
1. **Flexible Hierarchies**: Support reorganization without breaking permissions
2. **Inheritance Policies**: Define clear permission inheritance rules
3. **Delegation**: Allow organizations to manage their own members
4. **Cross-Organization Collaboration**: Support users in multiple organizations

---

## Security Considerations

### Authentication
- Implement secure authentication protocols (OAuth 2.0, OpenID Connect)
- Use HTTPS for all credential transmission
- Implement account lockout after failed attempts
- Support passwordless authentication options

### Authorization
- Follow principle of least privilege
- Implement role-based access control (see Section 3)
- Audit all permission changes
- Regularly review and prune unused accounts

### Compliance
- Support GDPR right to deletion for identities
- Implement data residency requirements for tenants
- Maintain audit logs for compliance (see Section 10)
- Support data export for regulatory requirements

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Actors interact with interfaces and perform operations
- **Section 3 (Authorization)**: Identities have roles that grant permissions
- **Section 4 (Domain Modeling)**: Entities track which actor created/modified them
- **Section 5 (Behavior)**: Actions are performed by actors
- **Section 6 (Data Management)**: Audit entries record actor actions
- **Section 10 (Governance)**: Controls are owned by actors; evidence is verified by actors

---

## Common Patterns and Examples

### User Registration Flow
```
1. HumanActor submits registration
2. System creates Identity with email verification token
3. User verifies email
4. System activates Credential (PASSWORD)
5. System assigns default Role to Identity
6. Identity belongs to Tenant and default Organization
```

### Service Account Creation
```
1. Administrator creates SystemActor
2. System generates service Identity
3. System creates Credential (API_KEY or CERTIFICATE)
4. Administrator assigns Roles with limited permissions
5. Service uses credentials for authentication
```

### Multi-Tenant User Onboarding
```
1. New Tenant is created
2. Admin user Identity is created within Tenant
3. Admin creates Organizations within Tenant
4. Admin invites additional users
5. Users accept invitations and join Organizations
6. Permissions are scoped to Tenant and Organizations
```

### External Identity Federation
```
1. User initiates OAuth login with external provider
2. System receives OAuth callback with user info
3. System creates or links Identity using external ID
4. System creates OAUTH Credential
5. User is authenticated and assigned appropriate Roles
```
