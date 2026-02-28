# ModelRelay

**ModelRelay** is a stateless AI inference gateway that provides a clean, production-oriented abstraction layer over LLM providers (e.g., OpenAI).

It exposes REST endpoints for chat completions and embeddings, with structured logging, error mapping, and pluggable provider architecture.

Live deployment:
👉 https://modelrelay.onrender.com/docs

---

## Why ModelRelay?

In production systems, applications should not call model providers directly.

ModelRelay provides:

- Centralized provider integration
- Consistent request/response contracts
- Structured logging with request IDs
- Latency measurement
- Clean error mapping (rate limits, timeouts, upstream failures)
- CI-enforced code quality
- Containerized deployment

---

## Architecture

Client  
↓  
FastAPI Router  
↓  
Service Layer (validation + latency measurement)  
↓  
Provider Interface  
↓  
OpenAI Provider  
↓  
OpenAI API  

Cross-cutting concerns:
- Request ID middleware
- Structured JSON logging
- Global error handler
- Typed schemas (Pydantic v2)
- Deterministic fake providers for testing

---

## Endpoints

### Health
`GET /v1/health`

---

### Chat
`POST /v1/chat`

Request:
```json
{
  "messages": [
    { "role": "user", "content": "Hello" }
  ],
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "max_output_tokens": 32
}
```

---

### Embeddings
`POST /v1/embeddings`

```json
{
  "input": "hello world",
  "model": "text-embedding-3-small"
}
```

---

## Error Handling

Upstream errors are mapped to consistent gateway responses.

Example (rate limit):

```json
{
  "error": {
    "code": "UPSTREAM_RATE_LIMITED",
    "message": "Upstream provider rate limited the request",
    "retryable": true,
    "details": null
  }
}
```

---

## Tech Stack

 - FastAPI
 - Pydantic
 - OpenAI Python SDK
 - Docker
 - GitHub Actions (ruff, mypy, pytest)
 - Render (production deployment)

---

## Local Developement

After forking, from repo root:

```bash
pip install -r requirements.txt
uvicorn app.main:create_app --factory --reload
```

Swagger UI:
http://localhost:8000/docs

---

## Docker

```bash
docker build -t modelrelay .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key modelrelay
```

---

## CI

Every push runs:

 - Ruff (linting)
 - MyPy (type checking)
 - Pytest (unit tests)

---

## Design Principles

 - Strict internal typing
 - Explicit provider abstraction
 - Deterministic test environment (fake providers)
 - Clear error boundaries
 - Minimal surface area
 - Production-first thinking

---

## Production Considerations (Future Work)

 - API key authentication
 - Rate limiting at gateway layer
 - Request tracing integration
 - Multi-provider failover
 - Streaming support
 - Observability integration (OpenTelemetry)

---