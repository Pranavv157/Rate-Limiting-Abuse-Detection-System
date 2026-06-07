# Redis-Based Rate Limiting & Abuse Detection System

A production-inspired backend security system built with **Django** and **Redis** that protects APIs from excessive traffic, automated abuse, and suspicious behavior.

Unlike traditional rate limiters that only count requests, this system combines **dynamic rate limiting**, **behavioral abuse scoring**, **progressive enforcement**, and **observability** to emulate patterns commonly used in modern backend platforms.

---

# Overview

Modern APIs face more than simple traffic spikes. Attackers often operate below traditional rate limits using techniques such as:

* Credential stuffing
* Brute-force login attempts
* Endpoint probing
* Distributed abuse
* Slow and persistent malicious traffic

A simple request counter is often insufficient for detecting these patterns.

This project demonstrates how backend systems can combine multiple layers of protection to identify and respond to suspicious behavior while maintaining system availability.

---

# Key Features

## Dynamic Rate Limiting

Request limits are determined dynamically based on:

* Authentication status
* Endpoint sensitivity
* Request context

### Configured Limits

| Endpoint     | Anonymous User     | Authenticated User |
| ------------ | ------------------ | ------------------ |
| Login        | 5 requests/window  | 10 requests/window |
| Search       | 10 requests/window | 30 requests/window |
| Default APIs | 10 requests/window | 20 requests/window |

---

## Redis-Based Request Tracking

Rate limits are enforced using Redis atomic operations:

* `INCR`
* `EXPIRE`

Benefits:

* Low latency
* Shared state across application instances
* Automatic expiration using TTLs
* Simple operational model

---

## Behavioral Abuse Detection

The system tracks suspicious activity and converts it into an abuse score.

### Event Scoring

| Event               | Score |
| ------------------- | ----- |
| Rate Limit Hit      | +2    |
| Failed Login        | +3    |
| Unauthorized Access | +1    |

Abuse scores automatically decay over time using Redis TTLs to prevent permanent penalties for temporary behavior.

---

## Progressive Enforcement

Instead of immediately banning users, the system applies graduated penalties.

### Cooldown Thresholds

| Abuse Score | Action            |
| ----------- | ----------------- |
| 0 - 6       | Allow             |
| 7 - 9       | 1 Minute Cooldown |
| 10+         | 5 Minute Cooldown |

This mirrors approaches commonly used by API gateways, Web Application Firewalls (WAFs), and security platforms.

---

## Observability

The system includes:

* Structured logging
* Rate-limit event tracking
* Abuse event tracking
* Redis-backed metrics

Example metric:

```text
metrics:rate_limit_hits
```

---

## Fault-Tolerant Design

The system follows a **fail-open strategy**.

If Redis becomes unavailable:

* Requests continue to be served
* Users are not blocked
* Errors are logged for investigation

This prevents infrastructure failures from causing application outages.

---

# System Architecture

## Request Lifecycle

```text
Client Request
       │
       ▼
Authentication Middleware
       │
       ▼
Enforcement Decision Engine
       │
       ▼
Rate Limit Policy Engine
       │
       ▼
Redis Rate Counter
       │
       ▼
Abuse Detection Engine
       │
       ▼
Application View
       │
       ▼
Response
```

---

# Core Components

## 1. RateLimitMiddleware

Responsible for:

* Request interception
* Identity resolution
* Rate limit enforcement
* Abuse event generation
* Cooldown enforcement
* Metrics collection

---

## 2. RateLimitPolicy

Responsible for:

* Dynamic request limits
* Endpoint-specific rules
* Authentication-aware policies

The policy layer remains independent of Redis and enforcement logic.

---

## 3. AbuseEngine

Tracks suspicious behavior over time.

Responsibilities:

* Event scoring
* Abuse accumulation
* Automatic score decay
* Behavioral analysis

---

## 4. EnforcementDecision

Converts abuse scores into actions.

Responsibilities:

* Progressive enforcement
* Cooldown determination
* Security decision making

---

# Redis Key Design

The system uses explicit namespaces for isolation and maintainability.

## Rate Limiting

```text
rate_limit:{identity}:{path}
```

Example:

```text
rate_limit:user:1:/login/
```

---

## Abuse Tracking

```text
abuse_score:{identity}
```

Example:

```text
abuse_score:user:1
```

---

## Cooldown Enforcement

```text
cooldown:{identity}
```

Example:

```text
cooldown:user:1
```

---

## Metrics

```text
metrics:rate_limit_hits
```

---

# Technology Stack

* Python
* Django
* Redis
* Docker
* Postman

---

# Testing Scenarios

The system was validated through the following scenarios:

## Anonymous User Flow

* Request counting
* Rate limit enforcement
* Abuse score generation
* Cooldown escalation

---

## Authenticated User Flow

* Session-based authentication
* User-specific limits
* Independent Redis identities
* Dynamic policy enforcement

---

## Abuse Detection

* Event accumulation
* Abuse score calculation
* TTL-based score decay
* Progressive escalation

---

## Enforcement

* Temporary cooldowns
* Automatic recovery using TTLs
* Threshold-based actions

---

# Engineering Decisions

## Why Redis?

* Atomic operations
* Extremely low latency
* Native TTL support
* Distributed-system friendly
* Well-suited for ephemeral security state

---

## Why Fixed Window Rate Limiting?

* Simple implementation
* Easy to reason about
* Operationally predictable
* Straightforward debugging

---

## Why Progressive Cooldowns Instead of Permanent Bans?

Permanent bans can produce false positives.

Cooldown-based enforcement:

* Reduces accidental lockouts
* Supports shared IP environments
* Allows automatic recovery
* Improves user experience

---

## Why Fail-Open?

Rate limiting is a protective layer rather than a critical business function.

Serving legitimate traffic is generally preferable to causing a system outage because of an infrastructure dependency failure.

---

# Trade-offs

Every design choice introduces trade-offs.

| Design Choice                | Benefit                                      | Trade-off                                    |
| ---------------------------- | -------------------------------------------- | -------------------------------------------- |
| Fixed Window Rate Limiting   | Simple and efficient implementation          | Allows burst traffic near window boundaries  |
| Redis TTL-Based Decay        | Automatic cleanup with minimal complexity    | Less flexible than custom decay strategies   |
| Fail-Open Design             | Maintains availability during Redis failures | Abuse protection may be temporarily bypassed |
| Session-Based Authentication | Easy integration with Django                 | Less suitable for stateless architectures    |
| Progressive Cooldowns        | Reduces false positives                      | Attackers may retry after cooldown expiry    |
| Redis Counters               | Fast request tracking                        | Less accurate than Sliding Window algorithms |

## Known Limitations

* Uses Fixed Window rate limiting instead of Sliding Window algorithms.
* Abuse detection is rule-based rather than behavior-learning based.
* Cooldowns are temporary and do not enforce permanent bans.
* Metrics are stored in Redis and not exported to external monitoring systems.
* Designed around a single Redis instance.

---

# Future Enhancements

Potential production-grade extensions include:

* Sliding Window Rate Limiting
* Redis Lua Scripts for atomic enforcement
* Distributed Rate Limiting across regions
* JWT-based authentication support
* Prometheus metrics integration
* Grafana dashboards
* Admin security dashboard
* CAPTCHA integration
* Trust score system
* Machine learning-based abuse detection

---

# Key Learnings

Through this project, I gained hands-on experience designing and implementing:

* Middleware-based request processing
* Redis-backed security controls
* Dynamic policy evaluation
* Behavioral abuse tracking
* Progressive enforcement mechanisms
* TTL-based state management
* Observability and operational debugging
* Fault-tolerant backend design patterns

---

# Summary

This project demonstrates how modern backend systems can move beyond simple request throttling by combining:

* Dynamic rate limiting
* Behavioral abuse analysis
* Progressive enforcement
* Observability
* Fault-tolerant design

The result is a layered protection system that balances security, operational reliability, and user experience while remaining simple to reason about and extend.
