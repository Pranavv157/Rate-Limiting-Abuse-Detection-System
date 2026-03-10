# Rate Limiting & Abuse Detection System

A production-inspired backend system built with Django and Redis to protect APIs from excessive usage and abusive behavior.

This project demonstrates how real-world systems go beyond simple rate limiting by combining dynamic policies, behavioral abuse detection, progressive enforcement, and observability.

---

##  Problem Statement

Traditional rate limiting only restricts request volume but fails to detect malicious behavior that stays under limits.

Examples:
- Slow credential stuffing
- Distributed abuse
- Repeated failed logins
- Endpoint probing

This system addresses those gaps.

---

## 🏗️ High-Level Architecture

Request Flow:

AuthenticationMiddleware  
→ Enforcement (Cooldown Check)  
→ Rate Limit Policy  
→ Redis Rate Counter  
→ Abuse Detection Engine  
→ Logging & Metrics  
→ View

Redis is used for fast, ephemeral state.  
Django handles request lifecycle and authentication.

---

## 🧩 Key Components

### 1. Rate Limit Middleware
- Enforces limits using Redis counters
- Fail-open design to protect availability
- Endpoint-aware keys

### 2. Policy Layer
- Decides limits dynamically per request
- Based on endpoint and authentication state
- Keeps enforcement logic clean

### 3. Abuse Detection Engine
- Scores suspicious behavior over time
- Uses event-based signals
- TTL-based decay for automatic recovery

### 4. Enforcement Engine
- Applies progressive penalties
- Temporary cooldowns instead of hard bans
- Auto-unblock using Redis TTL

### 5. Observability
- Structured logs for decisions
- Redis-backed counters for metrics
- Debuggable enforcement actions

---

## 🔐 Enforcement Strategy

| Abuse Score | Action |
|------------|-------|
| 0–3 | Allow |
| 4–6 | Strict rate limits |
| 7–9 | Temporary cooldown |
| ≥10 | Extended cooldown |

No permanent bans are applied automatically.

---

## 🔑 Redis Key Design

Examples:

- `rate_limit:{identity}:{path}`
- `abuse_score:{identity}`
- `cooldown:{identity}`
- `metrics:rate_limit_hits`

TTL is used extensively to avoid manual cleanup.

---

## ⚠️ Design Trade-offs

### Why fixed-window rate limiting?
- Simple
- Predictable
- Easy to debug

### Why fail-open on Redis errors?
- Rate limiting should not cause outages
- Availability > protection

### Why no permanent bans?
- Avoid false positives
- Shared IPs and NAT scenarios
- Human review required for hard bans

---

## 🧪 Testing & Execution

- Redis must be running locally
- Run Django server
- Use repeated requests to trigger limits
- Inspect Redis keys and TTLs manually

---

## 🚀 Future Improvements


- Trust score integration
- Redis Lua scripts for atomic enforcement
- Prometheus / Grafana metrics
- Admin dashboards

---

## 📌 Summary

This project demonstrates how modern backend systems combine rate limiting, behavioral analysis, and progressive enforcement to protect APIs safely and observably.

Client
  ↓
Auth Middleware
  ↓
Cooldown Check
  ↓
Policy Decision
  ↓
Redis Counter
  ↓
Abuse Scoring
  ↓
View
