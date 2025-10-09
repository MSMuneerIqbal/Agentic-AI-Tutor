# Alerts & Monitoring - Tutor GPT

## Overview

This document defines alert rules for monitoring Tutor GPT system health, performance, and reliability.

## Alert Rules

### 1. High Guardrail Rejection Rate

**Rule**: `guardrail_reject_rate > 10% over 5 minutes`

**Severity**: Warning

**Description**: Indicates excessive guardrail violations, suggesting:
- Users sending malicious input
- Agent outputs becoming unstable
- Guardrail rules too restrictive

**Alert Definition** (Prometheus):
```yaml
- alert: HighGuardrailRejectionRate
  expr: |
    (
      rate(guardrail_trigger_count[5m]) / rate(request_latency_count[5m])
    ) > 0.10
  for: 5m
  labels:
    severity: warning
    component: guardrails
  annotations:
    summary: "High guardrail rejection rate detected"
    description: "Guardrail rejection rate is {{ $value | humanizePercentage }} over the last 5 minutes"
```

**Thresholds**:
- Warning: >10% over 5 minutes
- Critical: >25% over 5 minutes

**Response**: See [Guardrail Failures Runbook](#runbook-guardrail-failures)

---

### 2. Pinecone Error Rate

**Rule**: `pinecone_error_rate > 1% of requests`

**Severity**: Warning (>1%), Critical (>5%)

**Description**: RAG functionality degraded or unavailable.

**Alert Definition** (Prometheus):
```yaml
- alert: PineconeErrorRate
  expr: |
    (
      rate(tool_error_count{tool="pinecone"}[5m]) / rate(pinecone_query_latency_count[5m])
    ) > 0.01
  for: 5m
  labels:
    severity: warning
    component: rag
  annotations:
    summary: "Pinecone error rate elevated"
    description: "Pinecone errors at {{ $value | humanizePercentage }} of queries"
```

**Thresholds**:
- Warning: >1% over 5 minutes
- Critical: >5% over 5 minutes

**Response**: See [Pinecone Failures Runbook](#runbook-pinecone-failures)

---

### 3. Gemini Timeout Spike

**Rule**: `gemini_timeout_count > 5 in 5 minutes`

**Severity**: Warning (>5), Critical (>20)

**Description**: Gemini API experiencing high latency or availability issues.

**Alert Definition** (Prometheus):
```yaml
- alert: GeminiTimeoutSpike
  expr: rate(gemini_timeout_count[5m]) > 0.017  # ~5 per 5 min
  for: 5m
  labels:
    severity: warning
    component: llm
  annotations:
    summary: "Gemini API timeouts spiking"
    description: "{{ $value }} timeouts per second over the last 5 minutes"
```

**Thresholds**:
- Warning: >5 timeouts in 5 minutes
- Critical: >20 timeouts in 5 minutes

**Response**: See [Gemini Timeouts Runbook](#runbook-gemini-timeouts)

---

### 4. TAVILY Error Rate

**Rule**: `tavily_error_count > 3 in 5 minutes`

**Severity**: Warning

**Description**: TAVILY MCP experiencing errors, affecting live search.

**Alert Definition** (Prometheus):
```yaml
- alert: TavilyErrorRate
  expr: rate(tavily_errors_count[5m]) > 0.01
  for: 5m
  labels:
    severity: warning
    component: mcp
  annotations:
    summary: "TAVILY MCP errors detected"
    description: "{{ $value }} TAVILY errors per second"
```

**Response**: See [TAVILY Failures Runbook](#runbook-tavily-failures)

---

### 5. High Request Latency (p95)

**Rule**: `request_latency_p95 > 1000ms`

**Severity**: Warning (>1s), Critical (>3s)

**Description**: API performance degraded, users experiencing slow responses.

**Alert Definition** (Prometheus):
```yaml
- alert: HighRequestLatency
  expr: |
    histogram_quantile(0.95, rate(request_latency_bucket[5m])) > 1.0
  for: 5m
  labels:
    severity: warning
    component: api
  annotations:
    summary: "High API latency detected"
    description: "p95 latency is {{ $value }}s"
```

**Thresholds**:
- Warning: p95 >1s over 5 minutes
- Critical: p95 >3s over 5 minutes

**Response**: See [High Latency Runbook](#runbook-high-latency)

---

### 6. Lesson Generation Latency (p95)

**Rule**: `lesson_generation_latency_p95 > 2000ms`

**Severity**: Warning

**Description**: Lesson generation taking too long, affecting user experience.

**Alert Definition** (Prometheus):
```yaml
- alert: SlowLessonGeneration
  expr: |
    histogram_quantile(0.95, rate(lesson_generation_latency_bucket[5m])) > 2.0
  for: 5m
  labels:
    severity: warning
    component: tutor
  annotations:
    summary: "Lesson generation slow"
    description: "p95 lesson generation is {{ $value }}s"
```

**Response**: Check Gemini API status, RAG performance

---

### 7. No Active Sessions

**Rule**: `sessions_active == 0 for 30 minutes during business hours`

**Severity**: Info

**Description**: Possible outage or deployment issue preventing new sessions.

---

## Runbooks

### Runbook: Guardrail Failures

**Alert**: High Guardrail Rejection Rate

**Investigation Steps**:

1. **Check guardrail metrics**:
   ```bash
   curl http://localhost:8000/metrics/summary
   ```
   Look at `reliability.guardrail_triggers`

2. **Check logs for violation reasons**:
   ```bash
   grep "guardrail triggered" app.log | tail -50
   ```

3. **Identify most common violations**:
   - Input too long?
   - Output containing secrets?
   - Agent-specific rule failures?

4. **Analyze patterns**:
   - Single user/IP causing issues?
   - Specific agent consistently failing?
   - Time-based pattern (attack)?

**Resolution**:

- **If malicious input**: Block IP, add rate limiting
- **If agent output issues**: Check agent prompts, review recent changes
- **If rules too strict**: Adjust guardrail thresholds in `app/guards/policies.py`

**Prevention**:
- Review guardrail rules monthly
- Add integration tests for edge cases
- Implement gradual rollout for guardrail changes

---

### Runbook: Pinecone Failures

**Alert**: Pinecone Error Rate

**Investigation Steps**:

1. **Check Pinecone status**:
   - Visit Pinecone status page
   - Check API rate limits

2. **Review error types**:
   ```bash
   curl http://localhost:8000/metrics/health
   ```
   Check `errors.tool_errors`

3. **Check Pinecone dashboard**:
   - API usage
   - Vector count
   - Index health

4. **Test Pinecone connection**:
   ```python
   from app.tools.rag_tool import test_connection
   test_connection()
   ```

**Resolution**:

- **If rate limited**: Implement backoff, upgrade plan
- **If index corrupted**: Rebuild index from backups
- **If quota exceeded**: Upgrade Pinecone plan
- **If network issues**: Check firewall, DNS

**Fallback**:
- System continues without RAG (graceful degradation)
- Lessons delivered without citations

---

### Runbook: Gemini Timeouts

**Alert**: Gemini Timeout Spike

**Investigation Steps**:

1. **Check Gemini API status**:
   - Google Cloud Status Dashboard
   - Gemini API status page

2. **Review timeout patterns**:
   ```bash
   grep "gemini_timeout" app.log | tail -50
   ```

3. **Check request volume**:
   - Are we sending too many requests?
   - Any rate limiting responses?

4. **Test Gemini connectivity**:
   ```python
   from app.agents.config import gemini_client
   # Test simple completion
   ```

**Resolution**:

- **If Gemini outage**: Wait, use cached responses, show user-friendly message
- **If rate limited**: Implement exponential backoff, queue requests
- **If network issues**: Check egress, DNS, firewall

**Prevention**:
- Implement request queuing
- Add response caching
- Set appropriate timeout values (30s)

---

### Runbook: TAVILY Failures

**Alert**: TAVILY Error Rate

**Investigation Steps**:

1. **Check TAVILY MCP status**:
   ```bash
   # Test TAVILY connection
   curl -X POST http://localhost:8000/api/v1/tools/tavily/test
   ```

2. **Review error types**:
   - Network errors?
   - Rate limit errors?
   - Invalid query format?

**Resolution**:

- **If TAVILY down**: Fall back to RAG only
- **If rate limited**: Implement caching, reduce query frequency
- **If query format issues**: Review query construction logic

**Fallback**:
- Use RAG without live examples
- Tutor continues with static content

---

### Runbook: High Latency

**Alert**: High Request Latency (p95)

**Investigation Steps**:

1. **Identify slow endpoints**:
   ```bash
   curl http://localhost:8000/metrics/summary
   ```

2. **Check component latencies**:
   - Database query times
   - Redis operations
   - Gemini API calls
   - RAG queries

3. **Review resource usage**:
   - CPU, Memory, Network
   - Database connections
   - Redis connections

4. **Check for slow queries**:
   ```bash
   grep "Slow request detected" app.log
   ```

**Resolution**:

- **If database slow**: Add indexes, optimize queries, scale DB
- **If Gemini slow**: Add caching, implement timeouts
- **If RAG slow**: Optimize vector search, cache results
- **If resource constrained**: Scale horizontally, optimize code

**Prevention**:
- Regular performance testing
- Query optimization reviews
- Implement caching aggressively

---

## Alert Channels

### Production Alerts

- **Critical**: PagerDuty (24/7 on-call)
- **Warning**: Slack #alerts channel
- **Info**: Email to team@tutorgpt.com

### Staging Alerts

- **All**: Slack #staging-alerts channel

### Development

- **All**: Local logs only, no external notifications

## Alert Acknowledgment

All alerts must be acknowledged within:
- **Critical**: 15 minutes
- **Warning**: 1 hour
- **Info**: 4 hours

Unacknowledged alerts escalate to next tier.

## Alert Testing

Test alerts monthly:
```bash
# Trigger test alert
curl -X POST http://localhost:8000/api/v1/admin/trigger-test-alert
```

## Metrics Dashboard

Access Grafana dashboard: http://metrics.tutorgpt.com

**Key Dashboards**:
1. **System Health** - Overall system status
2. **Performance** - Latency and throughput
3. **Reliability** - Error rates and guardrails
4. **Capacity** - Resource usage and sessions

## On-Call Rotation

See on-call schedule: [On-Call Schedule](./oncall-schedule.md)

## Related Documentation

- [Testing Guide](./testing-guide.md)
- [Runbook Index](./runbooks/README.md)
- [Monitoring Architecture](../architecture/monitoring.md)

