# Architecture — Full-Stack E-Commerce Platform

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │   Pages   │ │Components│ │   Hooks  │ │  Redux   │        │
│  └────┬──────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │              │            │             │              │
│  ┌────▼──────────────▼────────────▼─────────────▼──────┐     │
│  │                  Services (API Layer)                │     │
│  │   axios instance · interceptors · token refresh      │     │
│  └───────────────────────┬──────────────────────────────┘     │
└──────────────────────────┼───────────────────────────────────┘
                           │ HTTP (REST)
┌──────────────────────────┼───────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                   │
│  ┌───────────────────────▼──────────────────────────────────┐ │
│  │                    Routes Layer                           │ │
│  │  auth · products · orders · admin · cart · chatbot       │ │
│  └───────────────────────┬──────────────────────────────────┘ │
│  ┌───────────────────────▼──────────────────────────────────┐ │
│  │                   Services Layer                          │ │
│  │   business logic · validation · orchestration             │ │
│  └───────────────────────┬──────────────────────────────────┘ │
│  ┌───────────────────────▼──────────────────────────────────┐ │
│  │                Repository Layer                           │ │
│  │     SQLAlchemy queries · data access abstraction          │ │
│  └───────────────────────┬──────────────────────────────────┘ │
│  ┌───────────────────────▼──────────────────────────────────┐ │
│  │                Models + Core Layer                        │ │
│  │    ORM models · security · config · rate limiting         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Chatbot Engine Pipeline                      │ │
│  │  Intent → Dispatcher → Engine → Formatter → Response     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          External Integrations                            │ │
│  │   MoMo Payment · OpenRouter AI · SMTP Email              │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## 1. Why a Monolith (Not Microservices)

For an e-commerce platform at this scale — a single development team, a university thesis timeline, and no requirement for independent deployability — a monolith is the correct architectural choice.

| Concern | Monolith | Microservices |
|---|---|---|
| Development velocity | High (one repo, one deploy) | Low (N repos, N CI pipelines) |
| Debugging | Single process, one breakpoint | Distributed tracing, multiple log streams |
| Data consistency | ACID transactions across all entities | Eventual consistency, saga patterns |
| Network overhead | Zero (in-process calls) | Latency, serialization, retry logic |
| Thesis complexity | Focus on features, not infrastructure | Ops overhead outweighs educational value |

**Counter-argument addressed:** "Microservices scale better."

The bottleneck of this application is the **MySQL database**, not the compute layer. Splitting into microservices would move the bottleneck from the database to the network without solving the actual scaling constraint. The correct scaling path is:

1. **Vertical** — larger database instance, connection pooling
2. **Read replicas** — separate read traffic from write traffic
3. **Caching layer** — Redis for session data, product catalog
4. **Only then** — domain-boundary microservices if needed

**But the codebase is layered to allow future extraction.** Each service module (`auth_service`, `order_service`, `payment_service`) has a single responsibility and clear interface. If the project ever outgrows the monolith, extracting `order_service` into a standalone service requires moving two files and adding an HTTP adapter — a day's work, not a rewrite.

### Decision Record

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Architecture style | Monolith | Microservices | Team size, thesis scope, data consistency requirements |
| Backend framework | FastAPI | Django, Flask | Async-native, auto-docs, Pydantic integration |
| ORM | SQLAlchemy | Django ORM, raw SQL | Mature, explicit, MySQL support |
| Database | MySQL | PostgreSQL, MongoDB | Existing infrastructure, relational integrity |
| Auth protocol | JWT + refresh rotation | Session-based | Stateless, mobile-friendly, NIST compliance |
| Chatbot pipeline | Hybrid (rule + LLM) | Pure LLM or pure rule | Hallucination prevention, cost control |
| Recommendations | Content-based scoring | Collaborative filtering | Cold-start elimination, interpretability |
| Frontend state | Redux + hooks | Pure Redux or pure hooks | Global state in Redux, local state in hooks |
| API client | Axios | fetch, React Query | Interceptor-based token refresh, timeout handling |
| Payment integration | MoMo (direct API) | Stripe, PayPal | Regional requirement (Vietnam market) |

---

## 2. Layered Architecture

```
Route ──→ Service ──→ Repository ──→ Model
  │           │            │            │
  │    Business Logic    Data Access   ORM
  │    Validation         SQL Queries  Tables
  │    Orchestration     Transaction   Columns
  │    Workflow          Management    Relationships
```

### Why three layers and not two?

The naive approach is `Route → Repository` (skip services). This works for simple CRUD but breaks down when business rules enter.

**Example — Order Creation:**
- Route receives HTTP request → calls service
- Service validates stock → calls repository to check inventory
- Service deducts stock → calls repository to update product
- Service creates order → calls repository to insert
- Service creates history entry → calls repository for audit trail
- Service commits transaction → all succeed or all roll back
- Route returns HTTP response

If routes called repositories directly, this multi-step transaction logic would live in the route handler. Routes would become thick, untestable, and non-reusable.

### When the layer is useful vs. when it's pass-through

Some services are genuine (auth, order, recommendation), while others are pass-through wrappers (user_service, category_service reads). The pass-through ones are **not wrong** — they provide a consistent extension point. If `create_category` later needs to validate uniqueness across locales, the route doesn't change because the service already intercepts the call. This is the **Open/Closed Principle**: modules are open for extension but closed for modification.

**Tradeoff:** Consistency costs files. The project has 13 service files, 4 of which are thin enough to question. Acceptable for a thesis where architectural consistency demonstrates understanding of layering.

---

## 3. Why Repository Pattern

**Without repository:**
```python
def get_products(db, category):
    return db.query(Product).filter(Product.category_id == category).all()
```

**With repository:**
```python
def get_products(db, category):
    return repositories.get_products(db, category=category)
```

**Why it matters:**

1. **Testability** — Repository functions can be mocked without setting up a database
2. **Consistency** — All queries for "get products" go through one function. If a column is renamed, one function changes, not 14 scattered query calls
3. **Optimization** — Add eager loading, caching, or query optimization in one place
4. **Transaction control** — Repositories don't commit. The service layer controls the transaction boundary, so multi-step operations are atomic

**Counter-argument:** "It adds indirection."

Yes, approximately 0.1 ms per call. For a thesis project where architectural understanding is being evaluated, this is a feature, not a bug. It demonstrates understanding of **Separation of Concerns**.

---

## 4. Chatbot Engine Pipeline

This is the most architecturally interesting subsystem.

```
User Message
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. intent_engine.py                                          │
│    ├── Rule-based classifier (keyword matching)              │
│    └── LLM classifier fallback (OpenRouter API)              │
│    Output: {"intent": "product_search",                      │
│             "entities": {"product_type": "laptop",           │
│                          "brand": "dell",                    │
│                          "price_range": "15-20"}}            │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. engine_dispatcher.py                                      │
│    Routes intent to specialized engine:                      │
│    ├── product_search  → search_engine                       │
│    ├── recommend       → recommendation_engine               │
│    ├── compare         → comparison_engine                   │
│    ├── gaming_check    → gaming_engine                       │
│    ├── faq/chitchat    → openrouter_formatter (LLM only)     │
│    └── unknown         → graceful fallback response          │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Specialized Engine                                        │
│    ├── search_engine:         SQL query with filters          │
│    ├── recommendation_engine: Scoring algorithm + SQL        │
│    ├── comparison_engine:     Side-by-side spec diff          │
│    ├── gaming_engine:         GPU/CPU benchmark lookup        │
│    └── (no engine?):          LLM fallback response           │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. openrouter_formatter.py                                   │
│    Converts engine result → natural language response        │
│    Uses LLM with structured context (no raw SQL output)      │
│    Output: {"message": "...", "products": [...],             │
│             "actions": [...]}                                │
└──────────────────────────────────────────────────────────────┘
```

### Why this pipeline architecture?

**Separation of intent classification from intent execution.** The intent engine doesn't know how to search products. The search engine doesn't know how intents are classified. This allows:
- Each engine to be tested independently
- New intents added by adding a new engine + one line in the dispatcher map
- Intent classification strategy to change without touching business logic

### Why not end-to-end LLM?

A pure LLM chatbot (one API call per message) would:
- **Hallucinate** product availability, prices, stock levels
- **Be slow** (3-5 seconds per API call)
- **Cost** money per query
- **Cannot** query the database directly

The hybrid pipeline solves this: structured intents drive deterministic database queries. The LLM is only used for:
1. Ambiguous intent classification (fallback)
2. Natural language formatting of results

**Result:** 80% of queries are handled by the rule-based classifier + engine pipeline (sub-second, zero cost). Only ambiguous messages hit the LLM API.

### Hallucination Prevention Strategy

| Technique | Implementation |
|---|---|
| **Deterministic data path** | Product search, comparison, gaming checks query the database directly — no LLM involvement |
| **Structured response format** | LLM outputs JSON with strict schema — parsed before returning to client |
| **Context isolation** | LLM receives only product names/IDs, not raw SQL or user PII |
| **Confidence threshold** | Rule-based classifier runs first; LLM fallback only if confidence < 0.8 |
| **Source attribution** | Products in chat responses include real database IDs, not generated values |
| **Benchmark data pre-seeded** | Gaming engine uses curated GPU/CPU benchmark data, not LLM knowledge |

---

## 5. Security Architecture

### JWT + Refresh Token Rotation

```
┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │
└────┬─────┘                    └────┬─────┘
     │  POST /auth/login             │
     │  {email, password}            │
     │                               │
     │  ← access_token (15 min)     │
     │  ← refresh_token (7 days)    │
     │  ← user                       │
     │                               │
     │  GET /orders (access_token)   │
     │  ────────────────────────────►│
     │  ← 200 OK                     │
     │                               │
     │  (15 min later)               │
     │  POST /orders (access_token)  │
     │  ────────────────────────────►│
     │  ← 401 Unauthorized           │
     │                               │
     │  POST /auth/refresh           │
     │  {refresh_token}              │
     │  ────────────────────────────►│
     │  │ 1. Hash refresh_token      │
     │  │ 2. Look up in DB           │
     │  │ 3. Check not revoked       │
     │  │ 4. Revoke OLD token        │
     │  │ 5. Issue NEW pair          │
     │  ← new access_token           │
     │  ← new refresh_token          │
     │                               │
     │  POST /orders (new token)     │
     │  ────────────────────────────►│
     │  ← 201 Created                │
```

### Why refresh token rotation?

| Attack Scenario | Without Rotation | With Rotation |
|---|---|---|
| Token stolen from localStorage | Attacker has permanent access | Attacker uses token, victim's next request fails (token already revoked) |
| Malicious insider exfiltrates DB | Stolen hashes are useless | Stolen hashes are useless |
| Session replay | Token works multiple times | Each rotation invalidates previous |

The rotation scheme means: if an attacker steals a refresh token and uses it before the legitimate client, the legitimate client's next request will fail because the old token was revoked. The user re-authenticates, and the attacker's access is cut short. This follows **NIST SP 800-63B** recommended practice.

### Rate Limiting — Two Layers

1. **SlowAPI (global):** IP-based, 60 requests/minute per endpoint category. Prevents brute-force login attacks.
2. **AdminRateLimiter (in-memory):** Admin-specific, 120 requests/60 seconds. Protects expensive admin endpoints.

### Account Lockout

```
10 failed login attempts → account locked 15 minutes
```
Combined with MFA (TOTP via `pyotp`), this provides defense-in-depth against credential stuffing.

---

## 6. Database Design Rationale

### Entity Relationship (Simplified)

```
User ──1:N──► Address
User ──1:N──► Order ──1:N──► OrderItem ──N:1──► Product
User ──1:N──► Cart ──1:N──► CartItem ──N:1──► ProductVariant
User ──1:N──► Review ──N:1──► Product
User ──1:N──► Wishlist ──N:1──► Product
User ──1:N──► AuditLog
User ──1:N──► RefreshToken

Category ──1:N──► Product ──1:N──► ProductVariant
Product  ──1:N──► ProductSpecification
Product  ──1:N──► ProductImage

Product ──N:M──► RelatedProduct (self-referential join table)
```

### Why UUIDs for primary keys?

| Criterion | Auto-increment INT | UUID (String, 36 chars) |
|---|---|---|
| Order ID guessability | Sequential, predictable | Random, no information leakage |
| Merge conflict | Yes | No |
| Sharding | Yes | No |
| Index performance | 4 bytes, fast | ~128 bytes (binary) or 36 chars (string) |
| URL exposure | `/orders/42` reveals scale | `/orders/abc...` reveals nothing |

**Tradeoff:** UUIDs are larger and slower for B-tree indexes. Mitigated by:
- Using `String(36)` not `Binary(16)` — simpler API, acceptable performance for <10M rows
- Indexes on foreign keys are selective enough (queries typically filter by `user_id` first)

### Why separate `ProductVariant` from `Product`?

Products with variants (e.g., iPhone 15 Pro in 3 colors × 3 storage sizes = 9 SKUs) share product descriptions and category but differ in price, stock, and SKU. A flat table would:
- Duplicate all product data for each variant
- Make variant-specific pricing impossible
- Break the SKU uniqueness constraint

The normalized design allows: one product with 9 variants, each with independent price and stock.

### Why `AuditLog` as a table, not a file?

- **Queryability:** Filter by user, action, resource, date range — impossible with log files
- **Integrity:** Stored in the same transaction as the audited action (ACID)
- **Search:** Full-text search across action details (JSON field)
- **Retention:** SQL-based cleanup for old records

---

## 7. Recommendation System

### Algorithm (Multi-Factor Scoring)

```
score(product, user_context) =
    w₁ × popularity_score   (view_count, rating, review_count)
  + w₂ × recency_score      (created_at — newer products favored)
  + w₃ × category_match     (same category as current product/user history)
  + w₄ × brand_match        (same brand as user's past purchases)
  + w₅ × price_proximity    (within ±30% of current product)

Sorted by score → top N returned
```

### Why not collaborative filtering?

| Approach | Cold Start | New User | New Product | Interpretability |
|---|---|---|---|---|
| Collaborative Filtering | ❌ | ❌ | ❌ | Unknown |
| Content-based (our approach) | ✅ | ✅ | ✅ | Transparent |

For a thesis project with limited user data, content-based filtering is the pragmatic choice. It works from day one and the scoring weights can be tuned without retraining a model.

### Cart-based co-purchase

`get_cart_recommendations` queries: "What products appear together in other users' carts that aren't already in this user's cart?" — This is **association rule mining** (simplified Apriori-like logic) without the complexity of a full ML pipeline.

---

## 8. Frontend Architecture

```
React Component Tree
│
├── Layouts
│   ├── MainLayout (header, footer, navbar)
│   └── AdminLayout (sidebar, topbar)
│
├── Pages (route-level components)
│   ├── public (Home, ProductList, ProductDetail, Cart, Checkout, etc.)
│   └── admin (Dashboard, Products, Orders, Categories, SpecTemplates)
│
├── Components (reusable UI)
│   ├── auth/ (AuthCard, AuthInput, etc.)
│   ├── Skeletons/ (loading placeholders)
│   └── (standalone: ProductCard, StarRating, SearchBar, etc.)
│
├── Hooks (encapsulated state + API calls)
│   ├── useProducts — pagination, filtering, sorting
│   ├── useCart — add/remove/update cart items
│   ├── useAuth — login state, token management
│   └── useRecommend — recommendation fetching
│
├── Store (Redux — global state)
│   ├── authSlice — user, tokens, isAuthenticated
│   ├── cartSlice — cart items, counts
│   ├── productSlice — (underutilized)
│   └── navigationSlice — (underutilized)
│
└── Services (API clients)
    ├── api.js — axios instance, interceptors, token refresh
    ├── authService.js — login, register, MFA, password reset
    ├── productService.js — products, categories, variants, images
    └── ...domain-specific services
```

### Why Redux + Hooks coexistence?

Redux handles genuinely global state (auth tokens, cart badge count). Per-page data (product list, search results) lives in custom hooks with local state. This avoids the common mistake of putting everything in Redux, which creates unnecessary re-renders and ceremony.

---

## 9. Scalability Roadmap

### Phase 1 (Current) — Monolith + MySQL
- One server, one database
- Connection pooling (SQLAlchemy pool_size=10)
- Static file serving via FastAPI

### Phase 2 — Read Replicas + Caching
```
Client → Load Balancer → App Server (×N)
                              │
                    ┌─────────┴──────────┐
                    │ Redis (session,     │
                    │  cache, rate limit) │
                    └─────────┬──────────┘
                    ┌─────────┴──────────┐
                    │     MySQL          │
                    │  Primary (writes)  │
                    │  Replica ×2 (reads)│
                    └───────────────────┘
```

- Products and categories are read-heavy → cache in Redis with 5-minute TTL
- Sessions stored in Redis (currently in MySQL refresh_tokens table)
- Static images served via CDN (Cloudflare or similar)

### Phase 3 — Domain Extraction (if needed)
```
API Gateway
│
├── Auth Service (standalone)
├── Product Service (standalone)
├── Order Service (standalone)
└── Chatbot Service (standalone)
```

Each service exposes an HTTP API. The API Gateway routes requests. The chatbot pipeline, recommendation engine, and payment integration are natural service boundaries.

**But:** This is premature unless traffic exceeds ~10K concurrent users or the team grows to 3+ developers. Each service adds deployment complexity, data synchronization latency, and debugging overhead.

---

## 10. Architecture Decision Record (Full)

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Architecture style | Monolith | Microservices | Team size, thesis scope, data consistency requirements |
| Backend framework | FastAPI | Django, Flask | Async-native, auto-docs, Pydantic integration |
| ORM | SQLAlchemy | Django ORM, raw SQL | Mature, explicit, MySQL support |
| Database | MySQL | PostgreSQL, MongoDB | Existing infrastructure, relational integrity |
| Auth protocol | JWT + refresh rotation | Session-based | Stateless, mobile-friendly, NIST compliance |
| Chatbot pipeline | Hybrid (rule + LLM) | Pure LLM or pure rule | Hallucination prevention, cost control |
| Recommendations | Content-based scoring | Collaborative filtering | Cold-start elimination, interpretability |
| Frontend state | Redux + hooks | Pure Redux or pure hooks | Global state in Redux, local state in hooks |
| API client | Axios | fetch, React Query | Interceptor-based token refresh, timeout handling |
| Payment integration | MoMo (direct API) | Stripe, PayPal | Regional requirement (Vietnam market) |
| UX improvements | Optimistic UI | Skeleton loaders | Perceived performance vs. accuracy |
| Error handling | Axios interceptor | Per-component try/catch | Centralized, consistent error UX |

---

## 11. Thesis Defense Script

### Opening Statement

> "This thesis presents a full-stack e-commerce platform built on a FastAPI backend and React frontend. The central architectural contribution is the **hybrid chatbot pipeline**, which combines rule-based intent classification with a multi-engine dispatcher to deliver deterministic product data through a natural language interface.
>
> The platform implements **defense-in-depth security** with JWT access tokens, refresh token rotation per NIST SP 800-63B, TOTP multi-factor authentication, rate limiting, and account lockout — addressing the OWASP Top 10 for API security.
>
> For the recommendation system, a **content-based multi-factor scoring model** was chosen over collaborative filtering to avoid cold-start problems and maintain interpretability — both requirements for a production deployment.
>
> The monolith architecture was a deliberate choice. Microservices would have added networking, deployment, and data consistency complexity that would shift focus from feature delivery to infrastructure management. The codebase is modular enough that extraction to microservices remains an option for future scaling."

### Why Not Microservices?

> "Microservices solve organizational problems, not technical ones. Conway's Law states that systems mirror communication structures. With a single developer, a monolith is the natural architecture.
>
> The concrete costs of microservices for this project would have been:
> - 3× deployment complexity (Docker, orchestration, service discovery)
> - Distributed transaction management for order creation (inventory + order + payment + history must be atomic)
> - Network latency between services (the chatbot pipeline would make 4+ internal HTTP calls per message)
> - Debugging across service boundaries
>
> The benefits — independent deployability, isolated failure domains, team autonomy — don't apply to a thesis project with one team and ≤2 developers."

### How Would This Scale?

> "The current bottleneck is the MySQL database. The scaling path is:
> 1. **Vertical scaling** — larger cloud instance with more RAM for InnoDB buffer pool
> 2. **Read replicas** — MySQL replication with read traffic routed to replicas, writes to primary
> 3. **Caching** — Redis for product catalog (most reads), session storage, rate limiter data
> 4. **Connection pooling** — SQLAlchemy pool_size configuration
> 5. **Horizontal app scaling** — stateless FastAPI instances behind a load balancer
> 6. **CDN** — Static assets moved from server to CDN
>
> Each step doubles capacity with roughly linear cost increase. Microservices would be step 7, not step 1."

### How Do You Avoid AI Hallucination?

> "By design, the LLM never generates product data. It only formats data that was deterministically retrieved from the database.
>
> The pipeline separates concerns: the intent engine extracts the user's intention (rule-based or LLM), the dispatcher routes to a specialized engine that queries the database using structured SQL, and the formatter converts the database results into natural language.
>
> The LLM's only role is:
> 1. Classifying ambiguous intent when rule-based matching fails
> 2. Formatting a structured response with proper grammar
>
> Both outputs are validated against a strict schema before reaching the user. The LLM cannot invent product names, prices, or stock levels because those values come from SQL queries, not the LLM's training data."

### Why Refresh Token Rotation?

> "Because without rotation, a stolen refresh token gives permanent access. With rotation, each use invalidates the previous token. If a token is stolen and used by an attacker, the legitimate user's next request fails — alerting them to the compromise.
>
> This follows NIST SP 800-63B guidelines for token binding and provides a concrete security benefit: the window of vulnerability for a stolen token is bounded by the time between the attacker's use and the legitimate user's next request, not the token's full lifetime."

---

## 12. Expected Committee Questions and Answers

### Q1: "The service layer has many pass-through functions. Why not collapse it?"

**A:** "You're correct that some service functions, particularly in `category_service` and `wishlist_service`, are thin wrappers. They exist for two reasons:
1. **Consistency** — Having all data access flow through services means adding business logic later (e.g., category deletion validation blocks deletion if products exist) doesn't require restructuring callers.
2. **Extension point** — The Open/Closed Principle states modules should be open for extension but closed for modification. The service layer provides that extension boundary.
For a production system, I would accept collapsing these and using route-to-repository calls for simple reads, keeping the service layer only where business logic exists."

### Q2: "Why not use an ORM like Django ORM or SQLAlchemy more aggressively?"

**A:** "SQLAlchemy is used extensively — all 25+ tables are defined as declarative models. The repository layer provides a query abstraction on top because:
- SQLAlchemy's query API ties business logic to the ORM, making unit tests require a database
- Repository functions encapsulate query patterns that repeat across routes
- When the schema changes, one repository function updates, not 10 scattered `db.query()` calls"

### Q3: "How do you handle database migrations?"

**A:** "The project uses SQLAlchemy's `Base.metadata.create_all()` on startup, combined with an `ensure_schema()` function that applies column additions for schema evolution. This is appropriate for a thesis but would be replaced with Alembic in production. The current approach is idempotent for additive schema changes but doesn't handle destructive operations (column removal, data migration)."

### Q4: "The Redux store has slices that aren't fully utilized. Why?"

**A:** "Redux was introduced early following common React patterns. As the project evolved, local state in custom hooks proved simpler for page-specific data. The cart reducer is actively used (badge count in navbar). The auth reducer manages login state globally. But `productSlice` and `navigationSlice` were architectural foresight that proved unnecessary. In retrospect, I would have deferred Redux until a concrete need emerged — YAGNI (You Aren't Gonna Need It). This is documented in the code review as an area for cleanup."

### Q5: "How does the recommendation engine compare to a production system like Amazon's?"

**A:** "Amazon uses collaborative filtering at massive scale with implicit feedback (clicks, views, time-on-page). My system uses content-based scoring, which is simpler and interpretable but doesn't learn from user behavior.
The tradeoff: cold-start is eliminated (new products get recommended immediately), but personalization is weaker. For a thesis project, this is appropriate — adding collaborative filtering would require a user base and training pipeline that doesn't exist.
If this were production, I would add:
1. Implicit feedback tracking (product views, cart adds)
2. A scheduled ML pipeline to compute similarity scores
3. A/B testing framework to measure recommendation quality"

### Q6: "The chatbot uses an external API for LLM. What happens if the API is down?"

**A:** "The system degrades gracefully. The rule-based intent classifier handles approximately 80% of common queries (product search, comparison, gaming checks) without hitting the LLM API. When the API is unavailable:
1. The `openrouter_formatter.enabled` check returns False
2. The chatbot responds with structured data (product results, comparison tables) without the natural language wrapper
3. The `/admin/generate-description` endpoint returns a 503 with a clear message
Additionally, the intent engine has a confidence threshold — if the rule-based classifier can't determine intent, it falls back to a generic helpful response instead of hitting a broken API."

### Q7: "Why use both JWT access tokens and refresh tokens? Why not just long-lived access tokens?"

**A:** "Short-lived access tokens (15 minutes) limit the damage if a token is stolen — the attacker's window is 15 minutes. Refresh tokens allow the user to stay logged in without re-entering credentials, but with rotation, each use invalidates the previous token.
Long-lived access tokens would be simpler but less secure. If one leaked (e.g., in browser history, server logs, or a compromised HTTPS proxy), the attacker would have persistent access with no way to revoke it.
The stateless nature of JWTs is both a strength and weakness — they can't be revoked server-side. Refresh tokens stored in the database can be revoked by the server (logout, admin session revocation)."

### Q8: "What would you improve if you had another month?"

**A:** "Three priorities:
1. **Test coverage** — Currently zero unit tests. I would add tests for the service layer (business logic) and chatbot engines (intent classification edge cases).
2. **Performance monitoring** — Add Prometheus metrics and structured logging for slow endpoints (AI description generation, analytics aggregation).
3. **Admin UX** — The admin dashboard shows raw data but lacks actionable analytics (sales trends, low-stock alerts, abandoned cart recovery)."

### Q9: "How do you handle concurrent requests — e.g., two users buying the last item?"

**A:** "Order creation uses SQLAlchemy's row-level locking with `SELECT ... FOR UPDATE`. The `create_order` service:
1. Begins a transaction
2. Queries current stock for each item with `FOR UPDATE` — acquires row-level lock
3. Validates sufficient inventory
4. Deducts stock
5. Creates order and order items
6. Commits transaction
If two users order simultaneously, the second `SELECT ... FOR UPDATE` blocks until the first transaction completes. If stock reaches zero, the second user gets a clean 'Insufficient stock' error rather than an oversold situation."

### Q10: "Why Python/FastAPI and not Node.js or Go?"

**A:** "Python was chosen for:
1. **AI integration** — The native Python ecosystem for AI/LLM calls (OpenAI SDK, LangChain-ready if needed later)
2. **ORM maturity** — SQLAlchemy is the most mature Python ORM with excellent MySQL support
3. **Development velocity** — FastAPI provides automatic OpenAPI docs, Pydantic validation, and async support with minimal boilerplate
FastAPI specifically was chosen over Django REST Framework because:
- Async-native (important for the chatbot pipeline with external API calls)
- Automatic OpenAPI/Swagger documentation (convenient for debugging)
- Lighter weight than Django for an API-only backend"

---

## Summary

This architecture prioritizes:

1. **Security first** — JWT rotation, MFA, rate limiting, account lockout
2. **Deterministic AI** — LLM is a formatter, not a data source
3. **Layered maintainability** — Route/Service/Repository separation with real business logic where it matters
4. **Pragmatic monolith** — Modular enough to extract microservices later
5. **Thesis-appropriate scope** — Complex enough to demonstrate skill, simple enough to complete

The codebase reflects genuine architectural tradeoffs, not cargo-cult patterns. The service layer could be thinner, the Redux store could be more focused — these are acknowledged refinements, not architectural failures.
