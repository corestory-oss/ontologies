# Section 8: Deployment and Operations

This section defines environments, deployments, deployment units, configuration, infrastructure, and releases.

> **v2.0 Note**: In SAO v2.0.0, many cross-entity relationships are now inlined directly on the owning class rather than declared as standalone slot references. Classes such as `Environment`, `Configuration`, `Infrastructure`, `Release`, and `DeploymentUnit` gain back-reference attributes that make navigating the ontology more explicit.

## Overview

The Deployment and Operations section models how software is packaged, configured, deployed, and run across different environments.

## Core Concepts

### Environment

**Definition**: A runtime context with specific configuration.

**Key Attributes**:
- **environment_type**: `development`, `testing`, `staging`, `production`, `dr`

**Relationships**:
- **hosts_deployments**: `Deployment` instances running in this environment
- **env_configured_by**: `Configuration` entities for this environment
- **uses_infrastructure**: `Infrastructure` resources used
- **deployed_by_pipelines**: `BuildPipeline` entities that deploy to this environment (v2.0 back-reference)

**Environment Types**:
- `development`: For active software development
- `testing`: For QA and integration testing
- `staging`: Pre-production environment mirroring production
- `production`: Live production environment serving users
- `dr`: Disaster recovery environment

**Environment Characteristics**:
- Different configurations (database connections, API keys)
- Different scale (smaller in dev, larger in prod)
- Different monitoring and alerting levels
- Different access controls

---

### Deployment

**Definition**: An instance of a service running in an environment.

**Key Attributes**:
- **replicas**: Number of instances/replicas running

**Relationships**:
- **deploys_service**: The `Service` being deployed
- **deployed_in_environment**: Target `Environment`
- **deploys_unit**: `DeploymentUnit` being deployed
- **deployment_configured_by**: `Configuration` entities
- **deploys_release**: `Release` version being deployed

**Deployment Patterns**:
- **Blue-Green**: Two identical environments, switch traffic
- **Canary**: Gradual rollout to subset of users
- **Rolling**: Replace instances gradually
- **Recreate**: Stop all old, start all new
- **Shadow**: Run new version alongside old for testing

---

### DeploymentUnit

**Definition**: The packaged artifact being deployed.

**Key Attributes**:
- **unit_type**: `container`, `vm`, `serverless_function`, `binary`, `package`
- **artifact_uri**: Location of the deployment artifact
- **checksum**: Artifact integrity checksum

**Back-Reference Attributes** (v2.0):
- **deployed_in_deployments**: `Deployment` entities that deploy this unit

**Deployment Unit Types**:
- `container`: Docker/OCI container image
- `vm`: Virtual machine image (AMI, qcow2)
- `serverless_function`: Lambda/Cloud Function package
- `binary`: Compiled executable binary
- `package`: Application package (JAR, WAR, ZIP)

**Artifact Management**:
- Store in artifact repository (Artifactory, Nexus, container registry)
- Version all artifacts
- Sign artifacts for integrity
- Scan for vulnerabilities
- Implement immutable artifacts (never modify, only replace)

---

### Configuration

**Definition**: Runtime parameters for a deployment.

**Key Attributes**:
- **config_type**: `environment_variable`, `config_file`, `secret`, `feature_flag`, `remote_config`
- **value**: Configuration value
- **is_secret**: Whether this is sensitive data
- **source**: Configuration source (vault, config service, etc.)

**Configuration Types**:
- `environment_variable`: OS environment variables
- `config_file`: YAML, JSON, properties files
- `secret`: Sensitive values (passwords, API keys) from secret manager
- `feature_flag`: Feature toggle configuration
- `remote_config`: Configuration from remote service (Spring Cloud Config, AWS AppConfig)

**Back-Reference Attributes** (v2.0):
- **controls_features**: `FeatureFlag` entities controlled by this configuration
- **configures_environments**: `Environment` entities configured
- **configures_deployments**: `Deployment` entities configured

**Configuration Best Practices**:
1. **Externalize**: Keep config separate from code
2. **Environment-Specific**: Different values per environment
3. **Secrets Management**: Use secret managers (Vault, AWS Secrets Manager)
4. **Validation**: Validate configuration on startup
5. **Hot Reload**: Support dynamic configuration updates when possible

---

### Infrastructure

**Definition**: The underlying compute, storage, and network resources.

**Key Attributes**:
- **infra_type**: `compute`, `storage`, `network`, `load_balancer`, `dns`, `cdn`, `firewall`, `api_gateway`, `service_mesh`
- **provider**: Cloud or infrastructure provider (AWS, Azure, GCP, on-premise)
- **region**: Geographic region
- **specifications**: Resource specifications (instance type, size, etc.)

**Relationships**:
- **used_by_environments**: `Environment` entities using this infrastructure
- **hosts_datastores**: `DataStore` entities hosted
- **infrastructure_provisioned_by_iac**: `IaCDefinition` entities provisioning this infrastructure (v2.0 back-reference)

**Infrastructure Types**:
- `compute`: VMs, containers, serverless compute
- `storage`: Disks, volumes, object storage
- `network`: VPC, subnets, routing
- `load_balancer`: Application/network load balancers
- `dns`: Domain name services
- `cdn`: Content delivery networks
- `firewall`: Security groups, network ACLs
- `api_gateway`: API gateway or ingress controller
- `service_mesh`: Service mesh control plane (Istio, Linkerd, etc.)

**Infrastructure as Code (IaC)**:
- Terraform, CloudFormation, Pulumi
- Version control infrastructure definitions
- Automated provisioning and configuration
- Reproducible environments
- Drift detection

---

### Release

**Definition**: A versioned, deployable package of changes.

**Key Attributes**:
- Implements `Versionable` mixin
- **version**: Semantic version number
- **changelog**: Release notes describing changes
- **artifacts**: List of `DeploymentUnit` entities

**Back-Reference Attributes** (v2.0):
- **deployed_in_deployments_as_release**: `Deployment` entities that deploy this release

**Release Process**:
1. **Build**: Compile and package code
2. **Test**: Run automated tests
3. **Stage**: Deploy to staging environment
4. **Approve**: Manual or automated approval gate
5. **Deploy**: Deploy to production
6. **Monitor**: Monitor for issues
7. **Rollback**: Rollback if problems detected

**Semantic Versioning (SemVer)**:
- **MAJOR**: Incompatible API changes (1.0.0 -> 2.0.0)
- **MINOR**: Backward-compatible functionality (1.0.0 -> 1.1.0)
- **PATCH**: Backward-compatible bug fixes (1.0.0 -> 1.0.1)

---

## Deployment Strategies

### Blue-Green Deployment
- Maintain two identical environments (Blue and Green)
- Deploy new version to idle environment
- Switch traffic to new environment
- Keep old environment for quick rollback

**Pros**: Zero downtime, easy rollback
**Cons**: Requires double infrastructure

### Canary Deployment
- Deploy new version to small subset of instances
- Monitor metrics and errors
- Gradually increase traffic to new version
- Rollback if issues detected

**Pros**: Reduces blast radius, early detection
**Cons**: Requires traffic splitting, more complex

### Rolling Deployment
- Replace instances one at a time
- Health check each new instance before continuing
- Continue until all instances replaced

**Pros**: No extra infrastructure needed
**Cons**: Mixed versions during deployment

### Feature Flags
- Deploy code with features disabled
- Enable features dynamically via configuration
- Decouple deployment from feature release

**Pros**: Instant rollback, gradual rollout, A/B testing
**Cons**: Code complexity, technical debt

---

## Best Practices

### Deployment Automation
1. **CI/CD Pipeline**: Automate build, test, deploy
2. **Immutable Infrastructure**: Replace, don't modify
3. **Automated Testing**: Run tests before deployment
4. **Deployment Gates**: Approval and validation gates
5. **Rollback Automation**: Automated rollback on failure

### Configuration Management
1. **12-Factor App**: Follow 12-factor principles
2. **Secrets Rotation**: Rotate secrets regularly
3. **Configuration Validation**: Validate on startup
4. **Least Privilege**: Minimal permissions for services
5. **Audit Logging**: Log all configuration changes

### Environment Management
1. **Parity**: Keep dev, staging, prod as similar as possible
2. **Isolation**: Isolate environments (network, IAM)
3. **Environment Variables**: Use env vars for environment-specific config
4. **Testing in Production-Like**: Test in staging that mirrors production
5. **Cost Management**: Right-size non-production environments

### Release Management
1. **Versioning**: Use semantic versioning
2. **Changelog**: Maintain detailed changelogs
3. **Release Notes**: Document changes for users
4. **Rollback Plan**: Have rollback plan for every release
5. **Communication**: Communicate releases to stakeholders

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Services are deployed
- **Section 6 (Data Management)**: Data stores hosted on infrastructure
- **Section 9 (Observability)**: Deployments emit metrics and logs
- **Section 10 (Governance)**: Infrastructure must comply with requirements

---

## Example: Microservice Deployment

```
Release: OrderService v2.3.1
  Version: 2.3.1
  Changelog: "Fixed payment validation bug, improved performance"
  Artifacts:
    - DeploymentUnit: order-service:2.3.1
      Type: CONTAINER
      URI: docker.io/mycompany/order-service:2.3.1
      Checksum: sha256:abc123...

Environments:
  Development:
    Infrastructure:
      - Type: COMPUTE (t3.small EC2)
      - Region: us-east-1
    Configuration:
      - DB_HOST: dev-db.internal (ENVIRONMENT_VARIABLE)
      - LOG_LEVEL: DEBUG
      - STRIPE_API_KEY: (SECRET from AWS Secrets Manager)

  Production:
    Infrastructure:
      - Type: COMPUTE (EKS cluster with c5.2xlarge nodes)
      - Region: us-east-1, us-west-2 (multi-region)
      - Type: LOAD_BALANCER (Application Load Balancer)
      - Type: CDN (CloudFront)
    Configuration:
      - DB_HOST: prod-db.rds.amazonaws.com
      - LOG_LEVEL: INFO
      - STRIPE_API_KEY: (SECRET from AWS Secrets Manager)
      - ENABLE_NEW_PRICING: true (FEATURE_FLAG)

Deployment Strategy: Canary
  Step 1: Deploy to 5% of instances
    - Monitor error rate, latency, CPU, memory
    - Duration: 30 minutes

  Step 2: Deploy to 25% if metrics healthy
    - Monitor same metrics
    - Duration: 1 hour

  Step 3: Deploy to 100% if metrics healthy
    - Full rollout

  Rollback Trigger:
    - Error rate > 1%
    - p99 latency > 500ms
    - Manual rollback command

Monitoring:
  - Health checks: /health/live, /health/ready
  - Metrics: request_rate, error_rate, latency_p99, cpu_usage, memory_usage
  - Alerts: High error rate, high latency, health check failures
```
