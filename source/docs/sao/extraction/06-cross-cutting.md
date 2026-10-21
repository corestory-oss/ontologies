# Phase 6: Cross-Cutting Concerns

**Input:** All prior phase outputs + configs + deployment manifests + CI/CD files + test files + documentation
**Output:** Classes across SAO Sections 2-3 (Identity/Auth), 8 (Deployment), 9 (Observability), 10 (Compliance), 11 (Testing), 12 (UI), 13-14 (Build/CI/CD), 15-17 (Advanced), 30 (Knowledge)

---

## 1. Overview

Cross-cutting concerns span every layer of a software system. Security, identity, testing, deployment, observability, compliance, UI structure, CI/CD, concurrency, and knowledge artifacts are not confined to a single architectural tier -- they attach everywhere.

This phase can start as soon as Phase 2 completes and MAY run in parallel with Phases 3-5. It is organized into two independent groups:

- **Group A: Security, Governance, Quality** -- Identity, authorization, compliance, testing, UI, build/CI-CD, and knowledge artifacts.
- **Group B: Runtime & Ops** -- Deployment, observability, and concurrency.

The two groups have no ordering dependency on each other and MAY be worked on simultaneously. Automation varies by subsection (40-80%): identity and CI/CD extraction are largely automatable from configuration files, while compliance and knowledge artifacts typically require human judgment.

---

## 2. Group A: Security, Governance, Quality

### 2.1 Identity and Multi-Tenancy

Extract the identity model -- how users, services, and external actors are represented and authenticated.

**Classes:** **Identity**, **Credential**, **Tenant**, **Organization**

| Class | Key attributes | Links |
|---|---|---|
| **Identity** | `identity_type` | `represents_actor` -> **Actor**, `has_roles` -> **Role**, `belongs_to_tenant` -> **Tenant**, `member_of_organizations` -> **Organization** |
| **Credential** | `credential_type`, `expires_at`, `is_active` | Inlined under **Identity** via `credentials` |
| **Tenant** | `name` | `organizations` -> **Organization**, `settings` -> **Configuration**, `contains_identities` -> **Identity** |
| **Organization** | `name` | `parent` / `children` -> **Organization**, `has_identity_members` -> **Identity** |

**`credential_type` permissible values** (enum `CredentialType`):

- `password`
- `token`
- `certificate`
- `api_key`
- `biometric`
- `mfa`
- `oauth`

**Sources:** Auth configuration files, identity provider integration code (OIDC, SAML, LDAP), user model definitions, session management code.

**Extraction guidance:** Scan for authentication middleware, login controllers, and identity provider SDKs. For each distinct identity type, create an **Identity** and link it to the corresponding **Actor** via `represents_actor`. Create **Credential** instances for each authentication mechanism. If the system is multi-tenant, create **Tenant** and **Organization** instances from tenant configuration or database schemas.

```yaml
identities:
  - name: UserIdentity
    identity_type: human_user
    represents_actor: EndUser
    credentials:
      - name: PasswordCredential
        credential_type: password
        is_active: true
      - name: OAuthCredential
        credential_type: oauth
        is_active: true
    belongs_to_tenant: DefaultTenant
    has_roles: [CustomerRole]
```

---

### 2.2 Authorization and Policy

Extract the authorization model -- how permissions are granted, scoped, and enforced.

**Classes:** **Role**, **Permission**, **Policy**, **Scope**, **Constraint**

| Class | Key attributes | Links |
|---|---|---|
| **Role** | `name`, `is_system_role` | `grants_permissions` -> **Permission**, `inherits_from_role` -> **Role**, `can_access_features` -> **Feature** |
| **Permission** | `name` | `allows_actions` -> **Action**, `applies_to_resource_types` -> **ResourceType**, `limited_by_scope` -> **Scope** |
| **Policy** | `policy_type`, `priority` | `evaluates_permissions` -> **Permission**, `enforced_by_system` -> **System**, `guards_routes` -> **Route** |
| **Scope** | `scope_type`, `resource_pattern` | `limits_permissions` -> **Permission** |
| **Constraint** | `constraint_type`, `expression` | Inlined under **Permission** via `constraints` |

**`policy_type` permissible values** (enum `PolicyType`):

- `rbac`
- `abac`
- `rebac`
- `pbac`

**`scope_type` permissible values** (enum `ScopeType`):

- `global`
- `tenant`
- `organization`
- `resource`
- `field`

**`constraint_type` permissible values** (enum `ConstraintType`):

- `temporal`
- `spatial`
- `attribute`
- `context`
- `rate_limit`

**Sources:** RBAC configuration files, `@PreAuthorize` / `@Secured` / `@RolesAllowed` annotations, policy engines (OPA, Casbin), IAM definitions (AWS IAM policies, Azure RBAC), middleware guard code.

**Extraction guidance:** Identify all roles from configuration or code annotations. For each role, create a **Role** and link it to the permissions it grants. Create a **Policy** for each distinct authorization strategy. If roles inherit from other roles, set `inherits_from_role`. Scopes and constraints SHOULD be extracted from conditional access logic (e.g., tenant-scoped queries, time-based restrictions).

```yaml
roles:
  - name: Admin
    is_system_role: true
    grants_permissions: [ManageUsers, ManageOrders]
    inherits_from_role: Viewer

permissions:
  - name: ManageUsers
    allows_actions: [CreateUser, UpdateUser, DeleteUser]
    applies_to_resource_types: [UserResource]
    limited_by_scope: TenantScope
    constraints:
      - name: BusinessHoursOnly
        constraint_type: temporal
        expression: "time.hour >= 9 && time.hour <= 17"

policies:
  - name: TenantRBAC
    policy_type: rbac
    evaluates_permissions: [ManageUsers, ManageOrders]

scopes:
  - name: TenantScope
    scope_type: tenant
    resource_pattern: "tenant/${tenant_id}/*"
```

---

### 2.3 Compliance and Governance

Extract compliance obligations, controls, evidence, and risk assessments.

**Classes:** **ComplianceRequirement**, **Control**, **Evidence**, **RiskAssessment**

| Class | Key attributes | Links |
|---|---|---|
| **ComplianceRequirement** | `framework`, `effective_date` | `controls` -> **Control** (inlined), `applies_to_systems` -> **System** |
| **Control** | `control_id`, `implementation`, `frequency` | `evidence` -> **Evidence** (inlined), `owned_by_actor` -> **Actor**, `mitigates_risks` -> **RiskAssessment** |
| **Evidence** | `evidence_type`, `collected_at`, `artifact_uri` | `verified_by_actor` -> **Actor** |
| **RiskAssessment** | `risk_level`, `threats`, `vulnerabilities`, `residual_risk` | `mitigated_by_controls` -> **Control**, `assesses_system` -> **System** |

**`framework` permissible values** (enum `ComplianceFramework`):

- `gdpr`
- `hipaa`
- `soc2`
- `pci_dss`
- `iso27001`
- `sox`
- `ccpa`
- `fedramp`

**Sources:** Compliance documentation, audit records, security policies, data processing agreements, privacy impact assessments.

**Extraction guidance:** Identify applicable compliance frameworks from documentation, README files, or legal notices. For each framework, create a **ComplianceRequirement** and list its **Control** instances. Controls SHOULD reference the **Actor** who owns them and any **Evidence** that proves effectiveness. **RiskAssessment** instances MAY be created from security review documents or threat models.

```yaml
compliance_requirements:
  - name: GDPR Compliance
    framework: gdpr
    effective_date: "2024-01-01T00:00:00Z"
    applies_to_systems: [OrderManagementSystem]
    controls:
      - name: DataEncryptionAtRest
        control_id: GDPR-ENC-001
        implementation: "AES-256 encryption for all PII fields"
        owned_by_actor: SecurityTeam
        evidence:
          - name: EncryptionAuditLog
            evidence_type: automated_scan
            artifact_uri: "s3://audits/enc-report-2024-q2.pdf"
```

---

### 2.4 Testing

Catalog test suites, individual test cases, assertions, and coverage metrics.

**Classes:** **TestSuite**, **TestCase**, **TestAssertion**, **TestCoverage**

| Class | Key attributes | Links |
|---|---|---|
| **TestSuite** | `suite_type` (required), `framework`, `source_location`, `total_cases`, `passing_cases`, `failing_cases` | `contains_test_cases` -> **TestCase**, `tests_component` -> **Component**, `tests_module` -> **Module** |
| **TestCase** | `status`, `priority`, `is_automated` | `assertions` -> **TestAssertion** (inlined), `belongs_to_suite` -> **TestSuite**, `tests_callable` -> **CallableUnit**, `tests_operation` -> **Operation** |
| **TestAssertion** | `assertion_type`, `expected_value`, `line_number` | Inlined under **TestCase** |
| **TestCoverage** | `line_coverage_percent`, `branch_coverage_percent`, `function_coverage_percent`, `coverage_tool` | `coverage_for_component` -> **Component**, `coverage_for_module` -> **Module** |

**`suite_type` permissible values** (enum `TestSuiteType`):

- `unit`
- `integration`
- `functional`
- `end_to_end`
- `performance`
- `security`
- `regression`
- `smoke`
- `contract`

**`status` permissible values** (enum `TestCaseStatus`):

- `passing`
- `failing`
- `skipped`
- `flaky`
- `pending`

**`assertion_type` permissible values** (enum `AssertionType`):

- `equality`
- `truthiness`
- `exception`
- `type_check`
- `containment`
- `mock_verification`
- `snapshot`
- `custom`

**Sources:** Test directories (`test/`, `tests/`, `__tests__/`, `spec/`), test runner configuration (Jest, pytest, JUnit, Go test), coverage reports (Istanbul, JaCoCo, coverage.py).

**Extraction guidance:** Scan test directories and files (patterns like `*_test.go`, `*Test.java`, `test_*.py`, `*.spec.ts`). Create one **TestSuite** per logical grouping (typically per test file or class). For each test function, create a **TestCase** linked to the **CallableUnit** or **Operation** it tests. Coverage data SHOULD be extracted from coverage reports if available.

```yaml
test_suites:
  - name: UserServiceTests
    suite_type: unit
    framework: pytest
    source_location: tests/test_user_service.py
    total_cases: 12
    passing_cases: 11
    failing_cases: 1
    tests_component: UserServiceComponent
    contains_test_cases:
      - name: test_create_user_success
        status: passing
        is_automated: true
        tests_operation: CreateUserOp
        assertions:
          - name: assert_user_created
            assertion_type: equality
            expected_value: "201"

test_coverage:
  - name: UserServiceCoverage
    line_coverage_percent: 87.5
    branch_coverage_percent: 72.0
    coverage_tool: coverage.py
    coverage_for_component: UserServiceComponent
```

---

### 2.5 UI/Frontend

Map frontend component hierarchies, routing structure, and state management.

**Classes:** **UIComponent**, **Route**, **StateStore**

| Class | Key attributes | Links |
|---|---|---|
| **UIComponent** | `component_type` (required), `framework`, `is_lazy_loaded`, `is_server_rendered`, `source_location` | `has_parent_ui_component` / `has_child_ui_components` -> **UIComponent**, `renders_on_route` -> **Route**, `managed_by_state` -> **StateStore** |
| **Route** | `path_pattern` (required), `route_type`, `is_dynamic`, `is_authenticated` | `route_renders_component` -> **UIComponent**, `has_parent_route` / `has_child_routes` -> **Route**, `route_guarded_by` -> **Policy** |
| **StateStore** | `management_type` (required), `framework`, `actions`, `selectors` | `manages_ui_components` -> **UIComponent** |

**`component_type` permissible values** (enum `UIComponentType`):

- `page`
- `layout`
- `form`
- `widget`
- `modal`
- `navigation`
- `data_display`
- `composite`
- `higher_order`
- `provider`

**`route_type` permissible values** (enum `RouteType`):

- `page_route`
- `api_route`
- `layout_route`
- `redirect`
- `catch_all`
- `guarded`

**`management_type` permissible values** (enum `StateManagementType`):

- `local_state`
- `global_store`
- `context`
- `url_state`
- `server_state`
- `form_state`

**Sources:** Frontend component files (`.tsx`, `.vue`, `.svelte`), routing configuration (`react-router`, `vue-router`, Next.js `app/` directory), state management setup (Redux store, Vuex/Pinia modules, Zustand stores).

**Extraction guidance:** Walk the frontend source tree and create a **UIComponent** for each component file. Set `has_parent_ui_component` / `has_child_ui_components` from import analysis and JSX/template usage. Extract routes from routing configuration; for file-based routing (Next.js, Nuxt), derive `path_pattern` from directory structure. If a route requires authentication, set `is_authenticated` to `true` and link `route_guarded_by` to the relevant **Policy**.

```yaml
ui_components:
  - name: DashboardPage
    component_type: page
    framework: react
    source_location: src/pages/Dashboard.tsx
    renders_on_route: [DashboardRoute]
    managed_by_state: [AppStore]
    child_ui_components: [OrdersWidget, UserStatsWidget]

routes:
  - name: DashboardRoute
    path_pattern: /dashboard
    route_type: page_route
    is_authenticated: true
    route_guarded_by: [TenantRBAC]

state_stores:
  - name: AppStore
    management_type: global_store
    framework: zustand
    actions: [fetchOrders, updateUser]
    selectors: [selectCurrentUser, selectOrderList]
```

---

### 2.6 Build, CI/CD, and Dependencies

Document build pipelines, their stages, produced artifacts, registries, and known vulnerabilities.

**Classes:** **BuildPipeline**, **PipelineStage**, **BuildArtifact**, **ArtifactRegistry**, **KnownVulnerability**

| Class | Key attributes | Links |
|---|---|---|
| **BuildPipeline** | `pipeline_type` (required), `platform`, `trigger`, `source_file` | `stages` -> **PipelineStage** (inlined), `pipeline_deploys_to_environments` -> **Environment**, `pipeline_produces_artifacts` -> **BuildArtifact** |
| **PipelineStage** | `stage_type` (required), `order`, `condition`, `runner`, `is_manual` | Inlined under **BuildPipeline** |
| **BuildArtifact** | `artifact_type` (required), `artifact_uri`, `size_bytes`, `checksum` | `artifact_produced_by_pipeline` -> **BuildPipeline**, `artifact_stored_in_registry` -> **ArtifactRegistry** |
| **ArtifactRegistry** | `registry_type`, `base_url`, `is_private` | `stores_artifacts` -> **BuildArtifact** |
| **KnownVulnerability** | `cve_id`, `severity` (required), `cvss_score`, `affected_versions`, `fixed_version` | Inlined under **PackageDependency** |

**`pipeline_type` permissible values** (enum `PipelineType`):

- `build`
- `test`
- `deploy`
- `release`
- `integration`
- `delivery`
- `validation`

**`stage_type` permissible values** (enum `PipelineStageType`):

- `checkout`
- `build`
- `test`
- `lint`
- `security_scan`
- `package`
- `publish`
- `deploy`
- `approval`
- `rollback`
- `notify`

**`artifact_type` permissible values** (enum `ArtifactType`):

- `container_image`
- `binary`
- `archive`
- `package`
- `library`
- `documentation`
- `report`
- `load_module`

**`severity` permissible values** (enum `VulnerabilitySeverity`):

- `critical`
- `high`
- `medium`
- `low`
- `none`

**Sources:** CI/CD configuration files (`.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Makefile`), package manifests, vulnerability scan reports (`npm audit`, `snyk`, `trivy`).

**Extraction guidance:** Locate all CI/CD configuration files and create one **BuildPipeline** per pipeline definition. Parse stages in order and create **PipelineStage** instances with sequential `order` values. Identify produced artifacts and their registries. For known vulnerabilities, parse audit reports or lock file advisories and link **KnownVulnerability** instances to the affected **PackageDependency** (from Phase 1).

```yaml
build_pipelines:
  - name: MainCI
    pipeline_type: integration
    platform: github_actions
    source_file: .github/workflows/ci.yml
    trigger: [push, pull_request]
    trigger_branches: [main, "feature/**"]
    pipeline_deploys_to_environments: [Staging]
    stages:
      - name: Checkout
        stage_type: checkout
        order: 1
      - name: Lint
        stage_type: lint
        order: 2
      - name: UnitTests
        stage_type: test
        order: 3
      - name: BuildImage
        stage_type: build
        order: 4
      - name: PushToRegistry
        stage_type: publish
        order: 5
    pipeline_produces_artifacts: [AppImage]

build_artifacts:
  - name: AppImage
    artifact_type: container_image
    artifact_uri: "ghcr.io/acme/app:latest"
    artifact_stored_in_registry: GHCRRegistry

artifact_registries:
  - name: GHCRRegistry
    registry_type: container
    base_url: "https://ghcr.io/acme"
    is_private: true
```

---

### 2.7 Knowledge Artifacts

Index documentation, decision records, runbooks, and other knowledge artifacts.

**Class:** **KnowledgeArtifact**

| Attribute | Type | Description |
|---|---|---|
| `artifact_type` | `KnowledgeArtifactType` | Category of the artifact |
| `status` | `KnowledgeArtifactStatus` | Lifecycle state |
| `uri` | URI | Location of the artifact |
| `content` | string | Inline content (optional) |
| `authored_by` | string (multivalued) | Author names |
| `authored_at` | Timestamp | Creation date |

**Links:** `documents_system`, `documents_bounded_context`, `documents_module`, `documents_component`, `documents_aggregate`, `documents_domain_entity`, `documents_service`, `documents_integration`, `stored_in_container` -> **CodeContainer**.

**`artifact_type` permissible values** (enum `KnowledgeArtifactType`):

- `adr`
- `readme`
- `design_doc`
- `runbook`
- `wiki_page`
- `api_doc`
- `onboarding_guide`
- `postmortem`
- `changelog`
- `comment`
- `diagram`
- `rfc`
- `sop`

**`status` permissible values** (enum `KnowledgeArtifactStatus`):

- `draft`
- `published`
- `accepted`
- `superseded`
- `deprecated`
- `archived`

**Sources:** README files, `docs/` directories, ADR directories (`docs/adr/`, `docs/decisions/`), wiki pages, inline code comments of architectural significance.

**Extraction guidance:** Scan for documentation files (Markdown, AsciiDoc, reStructuredText) across the repository. Create a **KnowledgeArtifact** for each significant document and link it to the SAO entity it documents via the appropriate `documents_*` relationship. For ADRs, set `status` to `accepted` or `superseded` based on the ADR header. Supersession chains SHOULD use `superseded_by` / `supersedes` links.

```yaml
knowledge_artifacts:
  - name: ADR-001 Use PostgreSQL
    artifact_type: adr
    status: accepted
    uri: docs/adr/001-use-postgresql.md
    authored_by: ["Jane Doe"]
    documents_system: OrderManagementSystem

  - name: API Reference
    artifact_type: api_doc
    status: published
    uri: docs/api-reference.md
    documents_service: OrderService
```

---

## 3. Group B: Runtime & Ops

### 3.1 Deployment and Operations

Capture the deployment topology -- environments, deployment units, configuration, infrastructure, and releases.

**Classes:** **Environment**, **Deployment**, **DeploymentUnit**, **Configuration**, **Infrastructure**, **Release**

| Class | Key attributes | Links |
|---|---|---|
| **Environment** | `environment_type` | `hosts_deployments` -> **Deployment**, `env_configured_by` -> **Configuration**, `uses_infrastructure` -> **Infrastructure**, `deployed_by_pipelines` -> **BuildPipeline** |
| **Deployment** | `replicas` | `deploys_service` -> **Service**, `deployed_in_environment` -> **Environment**, `deploys_unit` -> **DeploymentUnit**, `deployment_configured_by` -> **Configuration**, `deploys_release` -> **Release** |
| **DeploymentUnit** | `unit_type`, `artifact_uri`, `checksum` | `deployed_in_deployments` -> **Deployment** |
| **Configuration** | `config_type`, `value`, `is_secret`, `source` | `controls_features` -> **Feature**, `configures_environments` -> **Environment**, `configures_deployments` -> **Deployment** |
| **Infrastructure** | `infra_type`, `provider`, `region` | `hosts_datastores` -> **DataStore**, `used_by_environments` -> **Environment**, `infrastructure_provisioned_by_iac` -> **IaCDefinition** |
| **Release** | `version`, `changelog` | `artifacts` -> **DeploymentUnit**, `deployed_in_deployments_as_release` -> **Deployment** |

**`environment_type` permissible values** (enum `EnvironmentType`):

- `development`
- `testing`
- `staging`
- `production`
- `dr`

**`unit_type` permissible values** (enum `DeploymentUnitType`):

- `container`
- `vm`
- `serverless_function`
- `binary`
- `package`

**`config_type` permissible values** (enum `ConfigurationType`):

- `environment_variable`
- `config_file`
- `secret`
- `feature_flag`
- `remote_config`

**`infra_type` permissible values** (enum `InfrastructureType`):

- `compute`
- `storage`
- `network`
- `load_balancer`
- `dns`
- `cdn`
- `firewall`
- `api_gateway`
- `service_mesh`

**Sources:** Dockerfiles, Kubernetes manifests, `docker-compose.yml`, serverless configs (`serverless.yml`, `sam.yaml`), Terraform/CloudFormation definitions, Helm charts, environment-specific config files.

**Extraction guidance:** Create one **Environment** per deployment target. For each service deployed to an environment, create a **Deployment** linking the **Service**, **Environment**, and **DeploymentUnit**. Extract configuration from `.env` files, `application.yml`, Kubernetes ConfigMaps/Secrets -- set `is_secret: true` for sensitive values but MUST NOT include the actual secret value. Create **Infrastructure** instances from IaC definitions. **Release** instances SHOULD be created from release tags or changelogs.

```yaml
environments:
  - name: Production
    environment_type: production
    uses_infrastructure: [ProdK8sCluster, ProdPostgres]
    env_configured_by: [ProdDatabaseUrl]
    deployed_by_pipelines: [MainCI]

deployments:
  - name: OrderServiceProd
    replicas: 3
    deploys_service: OrderService
    deployed_in_environment: Production
    deploys_unit: OrderServiceContainer
    deploys_release: Release_v2_1_0

deployment_units:
  - name: OrderServiceContainer
    unit_type: container
    artifact_uri: "ghcr.io/acme/order-service:2.1.0"

configurations:
  - name: ProdDatabaseUrl
    config_type: environment_variable
    source: kubernetes_secret
    is_secret: true
  - name: EnableNewCheckout
    config_type: feature_flag
    value: "true"
    is_secret: false

infrastructure:
  - name: ProdK8sCluster
    infra_type: compute
    provider: aws
    region: us-east-1
```

---

### 3.2 Observability

Document metrics, logs, traces, health checks, alerts, and incidents.

**Classes:** **Metric**, **Log**, **LogEntry**, **Trace**, **Span**, **HealthCheck**, **Alert**, **AlertRule**, **Incident**

| Class | Key attributes | Links |
|---|---|---|
| **Metric** | `metric_type`, `unit`, `labels` | `metric_emitted_by_component` -> **Component**, `monitored_by_alert_rules` -> **AlertRule** |
| **Log** | `log_type` | `contains_entries` -> **LogEntry**, `log_governed_by_retention` -> **RetentionPolicy** |
| **LogEntry** | `timestamp`, `level`, `message` | `entry_in_log` -> **Log** |
| **Trace** | `trace_id` | `contains_spans` -> **Span**, `starts_with_span` -> **Span** |
| **Span** | `span_id`, `operation_name`, `start_time`, `end_time`, `status` | `belongs_to_trace` -> **Trace**, `child_of_span` / `parent_of_spans` -> **Span** |
| **HealthCheck** | `check_type`, `endpoint`, `interval_seconds`, `timeout_seconds` | -- |
| **Alert** | `severity`, `triggered_at`, `acknowledged_at`, `resolved_at` | `triggered_by_rule` -> **AlertRule**, `escalates_to_incident` -> **Incident** |
| **AlertRule** | `condition`, `threshold`, `duration_seconds`, `notification_channels` | `monitors_metrics` -> **Metric**, `triggers_alerts` -> **Alert** |
| **Incident** | `severity`, `status`, `root_cause`, `postmortem_url` | `escalated_from_alerts` -> **Alert**, `affects_services` -> **Service** |

**`metric_type` permissible values** (enum `MetricType`):

- `counter`
- `gauge`
- `histogram`
- `summary`

**`log_type` permissible values** (enum `LogType`):

- `application`
- `access`
- `error`
- `security`
- `audit`
- `debug`

**`check_type` permissible values** (enum `HealthCheckType`):

- `liveness`
- `readiness`
- `dependency`
- `startup`

**Sources:** Monitoring configuration (Prometheus rules, Datadog monitors, Grafana dashboards), health check endpoints (`/health`, `/ready`), alerting rules, logging configuration (log4j, Winston, slog), distributed tracing setup (OpenTelemetry, Jaeger).

**Extraction guidance:** Scan for metric definitions in code (Prometheus registrations, StatsD calls). Create a **Metric** for each and link it to the emitting **Component**. Identify logging configuration to create **Log** instances -- the extraction agent SHOULD NOT create individual **LogEntry** instances during static extraction (those are runtime artifacts). Extract health check endpoints from framework configuration (Spring Boot Actuator, Kubernetes probes). Parse alerting rules to create **AlertRule** instances. **Incident** instances MAY be created from postmortem documents.

```yaml
metrics:
  - name: http_requests_total
    metric_type: counter
    unit: requests
    labels: [method, status_code, path]
    metric_emitted_by_component: APIGatewayComponent

health_checks:
  - name: LivenessProbe
    check_type: liveness
    endpoint: /health/live
    interval_seconds: 10
    timeout_seconds: 3

alert_rules:
  - name: HighErrorRate
    condition: "rate(http_requests_total{status_code=~'5..'}[5m]) > 0.05"
    threshold: 0.05
    duration_seconds: 300
    notification_channels: ["#alerts-critical", pagerduty]
    monitors_metrics: [http_requests_total]
```

---

### 3.3 Concurrency (if applicable)

Document synchronization primitives and concurrency patterns. This subsection applies only to systems with explicit concurrency management. Skip it for purely request-response web applications that delegate concurrency to the framework.

**Classes:** **ConcurrencyPrimitive**, **ConcurrencyPattern**

| Class | Key attributes | Links |
|---|---|---|
| **ConcurrencyPrimitive** | `primitive_type` (required), `is_reentrant`, `timeout_ms`, `line_number` | `used_by_callables` -> **CallableUnit**, `protects_data_elements` -> **DataElement** |
| **ConcurrencyPattern** | `pattern_type` (required), `max_concurrency`, `framework`, `shared_resources` | `pattern_used_by_component` -> **Component** |

**`primitive_type` permissible values** (enum `ConcurrencyPrimitiveType`):

- `mutex`
- `semaphore`
- `read_write_lock`
- `spin_lock`
- `condition_variable`
- `barrier`
- `latch`
- `atomic`

**`pattern_type` permissible values** (enum `ConcurrencyPatternType`):

- `thread_pool`
- `actor`
- `channel`
- `future_promise`
- `async_await`
- `fork_join`
- `producer_consumer`
- `reactor`
- `proactor`
- `csp`

**Sources:** Thread management code, async runtime configuration, channel usage, lock declarations, actor system setup (Akka, Erlang/OTP), thread pool configuration.

**Extraction guidance:** Search for lock primitives (`sync.Mutex`, `ReentrantLock`, `threading.Lock`, `std::mutex`) and create **ConcurrencyPrimitive** instances. Identify higher-level patterns (thread pools, actor systems, async runtimes) and create **ConcurrencyPattern** instances. Link primitives to the **CallableUnit** that uses them and the **DataElement** they protect.

```yaml
concurrency_primitives:
  - name: OrderCacheLock
    primitive_type: read_write_lock
    is_reentrant: false
    used_by_callables:
      - getOrderFromCache
      - updateOrderCache
    protects_data_elements:
      - orderCacheMap

concurrency_patterns:
  - name: RequestWorkerPool
    pattern_type: thread_pool
    max_concurrency: 50
    framework: java.util.concurrent
    pattern_used_by_component: OrderProcessorComponent

  - name: EventProcessor
    pattern_type: async_await
    framework: tokio
    pattern_used_by_component: EventHandlerComponent
```

---

## 4. Phase 6 Checklist

Before proceeding, verify that the following items have been addressed:

- [ ] **Identity and authorization model extracted** -- **Identity**, **Credential**, **Role**, **Permission**, **Policy**, **Scope**, and **Constraint** instances created
- [ ] **Compliance requirements documented** -- **ComplianceRequirement**, **Control**, **Evidence**, and **RiskAssessment** instances created (if applicable)
- [ ] **Test suites cataloged** -- **TestSuite**, **TestCase**, and **TestCoverage** instances created with links to the components and operations they test
- [ ] **UI components mapped** -- **UIComponent**, **Route**, and **StateStore** instances created (if frontend exists)
- [ ] **CI/CD pipelines documented** -- **BuildPipeline**, **PipelineStage**, **BuildArtifact**, and **ArtifactRegistry** instances created
- [ ] **Knowledge artifacts indexed** -- **KnowledgeArtifact** instances created for significant documentation
- [ ] **Deployment topology captured** -- **Environment**, **Deployment**, **DeploymentUnit**, **Configuration**, **Infrastructure**, and **Release** instances created
- [ ] **Observability infrastructure documented** -- **Metric**, **HealthCheck**, **AlertRule**, **Log**, and **Trace** instances created
- [ ] **Concurrency patterns noted** -- **ConcurrencyPrimitive** and **ConcurrencyPattern** instances created (if applicable)
- [ ] All enum values use exact `permissible_values` from `legacy/sao/sao.yml`
- [ ] Cross-references to entities from prior phases (e.g., **Component**, **Service**, **Actor**, **Operation**) are consistent
