# Section 9: Observability

This section defines metrics, logs, traces, spans, alerts, alert rules, incidents, and health checks.

## Overview

The Observability section provides comprehensive monitoring, logging, tracing, and alerting capabilities to understand system behavior and health.

## The Three Pillars of Observability

### 1. Metrics
Numerical measurements over time

### 2. Logs
Discrete events with timestamp and context

### 3. Traces
Request flows through distributed systems

---

## Core Concepts

### Metric

**Definition**: A quantitative measurement over time.

**Key Attributes**:
- **metric_type**: COUNTER, GAUGE, HISTOGRAM, SUMMARY
- **unit**: Unit of measurement (seconds, bytes, requests, etc.)
- **labels**: Metric labels for dimensionality

**Relationships**:
- **metric_emitted_by_component**: `Component` emitting this metric
- **monitored_by_alert_rules**: `AlertRule` entities monitoring this metric

**Metric Types**:

#### COUNTER
Monotonically increasing value (only goes up).
- **Examples**: total_requests, errors_total, bytes_sent
- **Use Case**: Cumulative counts, rates can be calculated

#### GAUGE
Value that can increase or decrease.
- **Examples**: cpu_usage, memory_usage, queue_depth, active_connections
- **Use Case**: Current state, resource utilization

#### HISTOGRAM
Distribution of values in buckets.
- **Examples**: request_duration_seconds, response_size_bytes
- **Use Case**: Percentiles, distributions
- **Buckets**: Pre-defined ranges (0-10ms, 10-50ms, 50-100ms, etc.)

#### SUMMARY
Summary statistics (quantiles).
- **Examples**: request_duration_seconds (with p50, p95, p99)
- **Use Case**: Percentiles without pre-defined buckets
- **Trade-off**: More accurate percentiles, higher overhead

**Metric Naming Conventions**:
- Use descriptive names: `http_requests_total`, not `requests`
- Include unit in name: `request_duration_seconds`, `memory_bytes`
- Use labels for dimensions: `{method="GET", status="200"}`

**Key Metrics to Track**:
- **RED Metrics** (Requests, Errors, Duration):
  - Request rate
  - Error rate
  - Duration (latency)
- **USE Metrics** (Utilization, Saturation, Errors):
  - Resource utilization (CPU, memory, disk)
  - Saturation (queue depth, load)
  - Error counts
- **Golden Signals**:
  - Latency
  - Traffic
  - Errors
  - Saturation

---

### Log

**Definition**: A timestamped record of discrete events.

**Key Attributes**:
- **log_type**: APPLICATION, ACCESS, ERROR, SECURITY, AUDIT, DEBUG
- **log_entries**: List of `LogEntry` records (inverse: `entry_in_log`)

**Relationships**:
- **log_governed_by_retention**: `RetentionPolicy` for log retention

**Log Types**:
- **APPLICATION**: Application-level logs (info, warnings)
- **ACCESS**: HTTP access logs, API requests
- **ERROR**: Errors and exceptions
- **SECURITY**: Security-related events (auth, access control)
- **AUDIT**: Compliance and audit trail (see Section 6)
- **DEBUG**: Detailed debugging information

**Structured Logging**:
Use structured formats (JSON) instead of plain text:
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "ERROR",
  "service": "order-service",
  "trace_id": "abc123",
  "user_id": "user_456",
  "message": "Payment processing failed",
  "error": "InsufficientFunds",
  "amount": 99.99
}
```

**Log Levels**:
- **TRACE**: Very detailed, typically disabled
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARN**: Warning messages, potential issues
- **ERROR**: Error messages, failures
- **FATAL**: Critical errors causing shutdown

---

### LogEntry

**Definition**: A single record within a log.

**Class**: `is_a: NamedEntity` (not `Log`). In SAO v2.0, LogEntry was changed from a subclass of Log to a subclass of NamedEntity, with an explicit relationship back to its parent Log.

**Key Attributes**:
- **timestamp**: When the event occurred
- **level**: Log level (DEBUG, INFO, WARN, ERROR)
- **message**: Log message
- **context**: Additional context (trace ID, user ID, etc.)
- **entry_in_log**: The `Log` this entry belongs to (range: Log, inverse: `log_entries`)

**Best Practices**:
1. **Correlation IDs**: Include trace/request ID in all logs
2. **Structured Data**: Use structured logging (JSON)
3. **Contextual Information**: Include relevant context
4. **Avoid PII**: Don't log sensitive personal information
5. **Appropriate Levels**: Use correct log levels

---

### Trace

**Definition**: A causal chain of operations across services.

**Purpose**: Track requests as they flow through distributed systems.

**Key Attributes**:
- **trace_id**: Unique identifier for the entire trace
- **trace_spans**: List of `Span` entities representing operations (inverse: `belongs_to_trace`)

**Relationships**:
- **starts_with_span**: Root `Span` of the trace

**Distributed Tracing**:
- Track requests across multiple services
- Identify bottlenecks and latency sources
- Understand service dependencies
- Debug distributed systems

**Trace Context Propagation**:
- W3C Trace Context standard
- Propagate trace_id and span_id in headers
- Maintain parent-child relationships

---

### Span

**Definition**: A single unit of work within a trace.

**Class**: `is_a: NamedEntity` (not `Trace`). In SAO v2.0, Span was changed from a subclass of Trace to a subclass of NamedEntity, with an explicit relationship back to its parent Trace.

**Key Attributes**:
- **span_id**: Unique identifier for this span
- **operation_name**: Name of the operation
- **start_time**: Operation start timestamp
- **end_time**: Operation end timestamp
- **status**: Span status (OK, ERROR, etc.)
- **attributes**: Key-value pairs with additional context
- **belongs_to_trace**: The `Trace` this span belongs to (range: Trace, inverse: `trace_spans`)

**Relationships**:
- **child_of_span**: Parent span (for nested operations)
- **parent_of_spans**: Child spans
- **root_of_trace**: Trace this is the root span of

**Span Attributes**:
- HTTP method, URL, status code
- Database query, table name
- Error messages
- Custom business context

**Example Trace Structure**:
```
Trace: Process Order
  Span 1: HTTP POST /orders (200ms)
    Span 2: Validate Order (10ms)
    Span 3: Reserve Inventory (50ms)
      Span 4: Database Query (30ms)
    Span 5: Process Payment (100ms)
      Span 6: External API Call to Stripe (90ms)
    Span 7: Create Shipment (40ms)
```

---

### Alert

**Definition**: A notification triggered by metric thresholds or anomalies.

**Key Attributes**:
- **severity**: Alert severity (critical, warning, info)
- **triggered_at**: When alert was triggered
- **acknowledged_at**: When alert was acknowledged
- **resolved_at**: When issue was resolved

**Relationships**:
- **triggered_by_rule**: `AlertRule` that triggered this alert
- **escalates_to_incident**: `Incident` if escalated

**Alert Severity Levels**:
- **CRITICAL**: Immediate action required, service down
- **WARNING**: Requires attention, potential issues
- **INFO**: Informational, awareness only

**Alert Best Practices**:
1. **Actionable**: Alert only on actionable conditions
2. **Context**: Include enough context to diagnose
3. **Deduplication**: Deduplicate similar alerts
4. **Routing**: Route to appropriate team
5. **Escalation**: Escalate if not acknowledged

---

### AlertRule

**Definition**: The condition that triggers an alert.

**Key Attributes**:
- **condition**: Alert condition expression (e.g., "error_rate > 5%")
- **threshold**: Threshold value
- **duration_seconds**: Duration before alerting (avoid flapping)
- **notification_channels**: Where to send alerts (email, Slack, PagerDuty)

**Relationships**:
- **monitors_metrics**: `Metric` entities being monitored
- **triggers_alerts**: `Alert` entities triggered

**Common Alert Rules**:
- **High Error Rate**: `error_rate > 1% for 5 minutes`
- **High Latency**: `p99_latency > 1s for 3 minutes`
- **Low Availability**: `availability < 99.9% for 15 minutes`
- **Resource Exhaustion**: `memory_usage > 90% for 10 minutes`
- **Disk Space**: `disk_usage > 85%`

**Alert Fatigue Prevention**:
- Set appropriate thresholds
- Use duration to avoid flapping
- Deduplicate similar alerts
- Regular review and tuning
- Auto-resolve when condition clears

---

### Incident

**Definition**: A tracked degradation or outage event.

**Key Attributes**:
- **severity**: Incident severity (P1-P5 or SEV1-SEV5)
- **status**: Current status (investigating, identified, monitoring, resolved)
- **started_at**: Incident start time
- **resolved_at**: Resolution time
- **root_cause**: Root cause analysis
- **postmortem_url**: Link to incident postmortem

**Relationships**:
- **escalated_from_alerts**: `Alert` entities that led to incident
- **affects_services**: `Service` entities impacted

**Incident Severity Levels**:
- **P1/SEV1**: Critical - Complete outage, all users affected
- **P2/SEV2**: High - Major functionality impaired
- **P3/SEV3**: Medium - Partial degradation
- **P4/SEV4**: Low - Minor issues
- **P5/SEV5**: Minimal - Cosmetic issues

**Incident Response Process**:
1. **Detection**: Alert triggers or user report
2. **Triage**: Assess severity and impact
3. **Investigation**: Identify root cause
4. **Mitigation**: Implement fix or workaround
5. **Resolution**: Verify issue resolved
6. **Postmortem**: Document incident and learnings

---

### HealthCheck

**Definition**: A probe verifying service availability.

**Key Attributes**:
- **check_type**: LIVENESS, READINESS, DEPENDENCY, STARTUP
- **endpoint**: Health check endpoint URL
- **interval_seconds**: Check frequency
- **timeout_seconds**: Check timeout
- **success_threshold**: Successes before marking healthy
- **failure_threshold**: Failures before marking unhealthy

**Health Check Types**:

#### LIVENESS
Determines if service is alive (should be restarted if failing).
- **Check**: Basic process health
- **Example**: `/health/live` returns 200 if process is running

#### READINESS
Determines if service can accept traffic.
- **Check**: Dependencies available, ready to serve
- **Example**: `/health/ready` returns 200 if DB is connected

#### DEPENDENCY
Check health of dependencies.
- **Check**: Database, cache, external APIs
- **Example**: Verify can connect to database

#### STARTUP
Probe during service initialization.
- **Check**: Slow-starting containers
- **Example**: Wait for warmup before liveness checks

**Health Check Implementation**:
```
GET /health/live
Response: 200 OK
{
  "status": "UP",
  "timestamp": "2024-01-15T10:30:45Z"
}

GET /health/ready
Response: 200 OK
{
  "status": "UP",
  "checks": {
    "database": "UP",
    "cache": "UP",
    "external_api": "UP"
  }
}
```

---

## Observability Patterns

### Correlation
- Use correlation IDs (trace IDs) across logs, metrics, and traces
- Link related events together
- Enable end-to-end request tracking

### Dashboards
- Real-time system health visibility
- Service-level indicators (SLIs)
- Business metrics
- Custom views for different teams

### Service Level Objectives (SLOs)
- Define target reliability levels
- **SLI** (Service Level Indicator): Measurement (e.g., latency)
- **SLO** (Service Level Objective): Target (e.g., p99 < 200ms)
- **SLA** (Service Level Agreement): Contract (e.g., 99.9% uptime)
- **Error Budget**: Allowed failures to meet SLO

### Synthetic Monitoring
- Proactive monitoring with synthetic transactions
- Simulate user workflows
- Detect issues before users

---

## Best Practices

### Metrics
1. **RED/USE/Golden Signals**: Track key metrics
2. **Cardinality**: Avoid high-cardinality labels
3. **Retention**: Balance retention with storage costs
4. **Aggregation**: Pre-aggregate when possible
5. **Consistency**: Use consistent naming and labels

### Logs
1. **Structured Logging**: Use JSON or structured format
2. **Correlation IDs**: Include trace IDs
3. **Log Levels**: Use appropriate levels
4. **Sensitive Data**: Don't log PII, credentials
5. **Sampling**: Sample high-volume logs

### Traces
1. **Sampling**: Sample traces in high-traffic systems
2. **Span Names**: Use meaningful operation names
3. **Attributes**: Include relevant context
4. **Propagation**: Propagate trace context across services
5. **Performance**: Minimize tracing overhead

### Alerts
1. **Actionable**: Only alert on actionable conditions
2. **Severity**: Use appropriate severity levels
3. **Runbooks**: Link to runbooks for resolution
4. **On-Call**: Route to appropriate on-call team
5. **Retrospective**: Review and tune alert rules

---

## SAO v2.0 Changes

In SAO v2.0, relationship attributes that were previously modeled as standalone linkML relationship classes have been inlined directly into the domain classes. For example, `Incident` now carries `escalated_from_alerts` and `affects_services` as direct attributes, `Alert` carries `escalates_to_incident`, and `AlertRule` carries `triggers_alerts`. Additionally, `LogEntry` and `Span` were changed from subclasses of `Log` and `Trace` respectively to subclasses of `NamedEntity`, with explicit back-reference attributes (`entry_in_log`, `belongs_to_trace`) linking them to their parent entities.

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Components emit metrics and logs
- **Section 5 (Behavior)**: Events generate logs
- **Section 6 (Data Management)**: Logs subject to retention policies
- **Section 7 (Integration)**: Integration metrics and traces
- **Section 8 (Deployment)**: Deployment health checks

---

## Example: Observability for Order Service

```
Metrics:
  - order_requests_total (COUNTER)
    Labels: method, status
  - order_processing_duration_seconds (HISTOGRAM)
    Buckets: 0.1, 0.5, 1.0, 2.0, 5.0
  - active_orders (GAUGE)
  - payment_failures_total (COUNTER)

Logs:
  - Application Log (JSON structured)
    Level: INFO
    Message: "Order created"
    Trace ID: "abc123"
    Order ID: "order_456"
    Customer ID: "cust_789"

  - Error Log
    Level: ERROR
    Message: "Payment processing failed"
    Error: "InsufficientFunds"
    Stack Trace: ...

Traces:
  Trace: Create Order
    Span: POST /api/orders (250ms)
      Span: Validate order (15ms)
      Span: Check inventory (40ms)
      Span: Process payment (150ms)
        Span: Stripe API call (130ms)
      Span: Create order record (30ms)
      Span: Emit OrderCreated event (15ms)

Alerts:
  - High Error Rate
    Condition: order_error_rate > 5% for 5 minutes
    Severity: CRITICAL
    Notification: PagerDuty, Slack #alerts
    Runbook: https://wiki/runbooks/order-service-errors

  - High Latency
    Condition: order_p99_latency > 2s for 3 minutes
    Severity: WARNING
    Notification: Slack #alerts

Health Checks:
  - Liveness: GET /health/live
    Interval: 10s
    Timeout: 1s
    Failure Threshold: 3

  - Readiness: GET /health/ready
    Checks: Database, Cache, Payment Gateway
    Interval: 5s
    Timeout: 2s
```
