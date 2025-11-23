# Production-Level Notes

This document describes how the minimal assignment implementation could be extended into a production-ready threat intelligence microservice.

## 1. Architecture

The assignment implementation uses a flat FastAPI application located in src/main.py.  
A production version would adopt:

- application factory pattern (create_app)
- modular routers (api/, services/, external/)
- dependency injection for external clients
- config management (pydantic BaseSettings, env switching for dev/stage/prod)

For scaling, the system naturally fits a microservice-per-domain structure:

- API gateway (FastAPI / API router)
- TI fetcher service (async workers)
- ML/AI scoring service
- Persistence service (PostgreSQL / ClickHouse)
- Frontend served from CDN

Async workers (Celery, Dramatiq, or native asyncio queues) would be used for heavy TI queries.

## 2. Deployment & DevOps

Minimal steps for production deployment:

- Dockerfile and multi-stage build
- docker-compose for local dev
- CI/CD via GitHub Actions:
  - lint (ruff)
  - type-check (mypy)
  - tests (pytest)
  - docker build & push to registry
- Helm chart for Kubernetes deployment
- Prometheus metrics & Grafana dashboard
- structured logging (Loguru or standard logging + JSON handlers)

Environments:
- development
- staging
- production

All secrets stored in:
- Kubernetes Secrets
- Vault/SM (AWS/GCP/Azure)

## 3. MLOps Layer

If the LLM is a core scoring component, production requirements include:

- prompt versioning (LangSmith or manual repo)
- audit trails of every LLM call
- rate limiting and fallbacks
- graceful degradation (local model, heuristic scoring)
- gating rules (pre-filtering requests before sending to LLM)
- load testing for API-Latency under LLM delays

Optional:
- fine-tuning small model for risk scoring
- feature store (Feast) for TI data
- incremental retraining pipeline

## 4. Data Persistence

Current version does not store data; production would use:

- PostgreSQL for metadata
- Redis for caching (IP reputation results have slow update cycles)
- ClickHouse for high-volume TI logs

Caching reduces external API calls, saves money, and avoids rate-limit issues.

TTL example:
- AbuseIPDB: 12h
- IPQualityScore: 12–24h
- VirusTotal: 24h (unless high-risk indicators change)

## 5. Security & Zero-Trust

Basic principles required for a TI system:

- no hardcoded secrets (env only)
- no outbound calls without validation
- audit log for all IP lookups
- JWT-based user identities (if exposed publicly)
- strict CORS policy
- request throttling (FastAPI middleware)
- API key or OAuth2 for protected endpoints
- network-level isolation between services (K8s network policies)

All outbound TI queries must be monitored and rate-limited.

## 6. Observability

Production stack:

- Logging: JSON logs → Loki / Elasticsearch
- Metrics: Prometheus exporter
- Tracing: OpenTelemetry tracing for:
  - HTTP handlers
  - external TI calls
  - LLM calls

Alerts:
- TI API failures
- rate limit thresholds
- latency spikes
- anomaly patterns

## 7. Cost Control (FinOps)

Threat-intelligence + LLM usage has cost implications.  
Production should implement:

- caching layer (reduces calls by ~80–95%)
- adaptive rate-limiting
- fallback scoring (no LLM call for “safe IPs”)
- monthly cost dashboard (Prometheus + Grafana + custom panels)
- API usage batching

Typical reduction: 3–7× cost reduction.

## 8. Testing Strategy

Beyond assignment tests, production testing includes:

- integration tests with mock TI sources
- contract tests (Pact or internal schema checks)
- load testing (k6)
- disaster recovery tests (simulated API failure)
- security tests:
  - fuzz testing
  - SSRF blocking
  - malformed input

Regression suite should cover:
- aggregator integrity
- scoring logic correctness
- LLM fallback correctness

## 9. Future Development

Potential roadmap:

- support for 10+ TI providers
- machine-learned risk scoring model
- correlation engine (multi-source signal fusion)
- clustering related IPs (graph-based enrichment)
- frontend dashboard (React/Vue)
- user accounts and saved reports
- role-based access control

## Summary

The assignment implementation is intentionally minimal.  
However, the architecture, code structure, and separation of modules allow for straightforward evolution into a scalable, production-grade system.

