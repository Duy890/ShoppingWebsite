# SYSTEM ARCHITECTURE — Electronics E-Commerce Platform

**STATUS:** Evidence-based reconstruction from production codebase.
**NOTICE:** Every architectural statement below is backed by actual implementation files. Sections marked `[PLANNED]` are documented in code comments or UI stubs but have no backend implementation.

---

## SYSTEM OVERVIEW

Full-stack electronics e-commerce platform with AI-powered chatbot, MoMo payment gateway, and admin dashboard. Built as FastAPI + React SPA, using SQLAlchemy ORM with MySQL. Single-server deployment with no microservices, no cache layer, no message queue.

---

## SYSTEM PURPOSE

Commerce platform for electronics retail (laptops, phones, tablets, audio, accessories) in Vietnam market. Provides product catalog, shopping cart, checkout, order tracking, AI shopping assistant with layered engine pipeline (intent classification, product search, comparison, gaming benchmark, recommendations), and full admin product/order management with spec templates. Recently extended with enterprise security features: refresh token rotation, TOTP MFA, account lockout, admin audit logging, login history tracking.

---

## IMPLEMENTED FEATURES

| Feature | Evidence | Status |
|---------|----------|--------|
| Product CRUD | `controllers.py` lines 738-759, `services.py` lines 144-159 | ✅ Fully |
| Cart (1 per user) | `controllers.py` lines 797-831, `services.py` lines 261-298 | ✅ Fully |
| Order with status machine | `controllers.py` lines 834-928, `services.py` lines 301-462 | ✅ Fully |
| MoMo payment | `controllers.py` lines 360-406, `services.py` lines 655-753 | ✅ Fully |
| AI chatbot | `chat_service.py` (orchestration) + 10 modules in `chatbot/` (engines, memory, dispatcher, formatter) | ✅ Fully |
| Gaming benchmark check | `chatbot/gaming_engine.py` | ✅ Fully |
| Product comparison | `chatbot/comparison_engine.py` | ✅ Fully |
| Recommendation engine | `services.py` lines 756-1038 | ✅ Fully |
| Spec templates | `controllers.py` lines 601-671, `repositories.py` spec section | ✅ Fully |
| SKU uniqueness check | `controllers.py` lines 518-535 | ✅ Fully |
| AI product description gen | `controllers.py` lines 949-1039 | ✅ Fully |
| Email (reset, change) | `core/email.py`, `services.py` lines 532-652 | ✅ Fully |
| Categories tree | `services.py` lines 78-118, `models.py` lines 132-147 | ✅ Fully |
| Address management | `controllers.py` lines 423-457, `services.py` lines 49-75 | ✅ Fully |
| Reviews / Wishlist | `controllers.py` lines 698-735, `services.py` lines 229-258 | ✅ Fully |
| Search logging + analytics | `repositories.py` search log, analytics endpoints | ✅ Fully |
| Image upload | `controllers.py` lines 66-112 | ✅ Fully |
| Password reset flow | `controllers.py` lines 293-315, `services.py` lines 532-652 | ✅ Fully |
| Email change flow | `controllers.py` lines 318-344, `services.py` lines 560-612 | ✅ Fully |
| Profile update | `controllers.py` lines 409-415 | ✅ Fully |
| JWT access token (24h) | `core/security.py` line 21-30 | ✅ Fully |
| Refresh token rotation | `core/security.py` lines 33-44, `services.py` lines 1045-1067 | ✅ Fully |
| TOTP MFA | `controllers.py` lines 224-283, `core/security.py` line 72 | ✅ Fully |
| Account lockout (10 attempts) | `core/admin_security.py` lines 28-58 | ✅ Fully |
| Admin audit logging | `core/admin_security.py` lines 65-87, `controllers.py` lines 1148-1156 | ✅ Fully |
| Login history tracking | `repositories.py` lines 1058-1069, `controllers.py` lines 288-290 | ✅ Fully |
| Admin rate limiter (120/min) | `core/admin_security.py` lines 156-184 | ✅ Fully |
| Session management (list/revoke) | `controllers.py` lines 1161-1206 | ✅ Fully |
| slowapi rate limiter (3/min register, 5/min login, 3/min forgot) | `controllers.py` lines 116, 137, 294 | ✅ Fully |
| Frontend refresh interceptor | `api.js` lines 96-136 | ✅ Fully |
| Frontend MFA/audit/lh services | `authService.js` lines 98-121 | ✅ Fully |

---

## PARTIALLY IMPLEMENTED FEATURES

| Feature | Gap | Evidence |
|---------|-----|----------|
| Admin audit decorator | `audit_admin_action` decorator exists but is NOT used on any endpoint | `admin_security.py` lines 102-149; no `@audit_admin_action` found in `controllers.py` |
| `require_admin_with_audit` | Function body is `pass` — never used as dependency | `admin_security.py` lines 90-99 |
| MFA verify on login | MFA is enabled/disabled but login does NOT enforce 2FA challenge | No MFA check in `login()` at line 139 |
| Frontend MFA UI | No actual MFA setup/verify page exists; only service methods defined | No MFA components in `components/` or `pages/` |
| Frontend session/audit pages | `adminService.js` has no session/audit methods; no admin pages for these | `adminService.js` checked |
| `pyotp` import | Imported inline inside endpoint handlers (not at module top) | `controllers.py` lines 249, 273 |

---

## PLANNED FEATURES (code comments / UI stubs)

| Feature | Evidence |
|---------|----------|
| Frontend MFA setup page | `authService.js` has `setupMFA`/`verifyMFA`/`disableMFA` |
| Frontend admin audit logs page | `SYSTEM_ARCHITECTURE.md` lists `AuditLogs` as admin page |
| Frontend admin sessions page | `SYSTEM_ARCHITECTURE.md` lists `Sessions` as admin page |
| CSRF protection | Not implemented anywhere |
| IP allowlist for admin | Not implemented anywhere |

---

## TECH STACK

**Backend:**
- FastAPI 0.116.0 (Python 3.11+)
- SQLAlchemy 2.0.22 ORM + PyMySQL 1.1.0 driver
- Pydantic 2.8.0 + pydantic-settings 2.8.0
- Auth: python-jose 3.3.0 (JWT HS256) + passlib 1.7.4 (bcrypt PBKDF2-SHA256)
- Rate limiting: slowapi 0.1.9
- MFA: pyotp 2.9.0 (TOTP)
- AI: openai SDK 1.54.3 + OpenRouter API
- Payment: MoMo test gateway (HMAC-SHA256)
- Email: aiosmtplib 3.0.1
- ASGI: Uvicorn 0.24.0

**Frontend:**
- React 18 + Vite + TypeScript (JSX in .jsx files)
- Redux Toolkit (5 slices)
- Axios HTTP client
- Tailwind CSS
- react-i18next (EN + VI)
- react-router-dom v6
- react-hot-toast

---

## HIGH LEVEL ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│                  Frontend (React SPA)                         │
│  Vite dev server :5173, served via Nginx in production        │
│  Pages → Hooks (9) → Services (12 via Axios) → REST API      │
│  State: Redux Toolkit (auth, cart, navigation, product)       │
│  i18n: react-i18next (EN/VI)                                 │
│  Theme: dark/light via React Context + localStorage            │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP (JSON)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                Backend (FastAPI :8000)                         │
│  Middleware: CORS, slowapi rate limiter, error handlers        │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────────┐  │
│  │ Routes   │→ │ Services │→ │ Repositories (DB Layer)     │  │
│  │controllers│  │services   │  │ repositories                │  │
│  │ routes/  │  │chatbot/   │  │ SQLAlchemy models (21)     │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬─────────────────┘  │
│       │              │                   │                    │
│       ▼              ▼                   ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────────┐  │
│  │ Auth     │  │ AI/Chat  │  │ Database (MySQL)            │  │
│  │ JWT+BCrypt│  │ OpenRouter│  │ 21 tables, UUID PKs        │  │
│  │ MFA+TOTP │  │ 7 modules│  │                            │  │
│  │ Rate Lim │  │ 3 engines│  │                            │  │
│  │ Lockout  │  │          │  │                            │  │
│  └──────────┘  └──────────┘  └────────────────────────────┘  │
│                                                               │
│  External: MoMo Payment API, SMTP Email (Google)              │
└──────────────────────────────────────────────────────────────┘
```

---

## FRONTEND ARCHITECTURE

### Pages (29 total: 22 user-facing + 7 admin)

**Public (14):** Home, ProductList, ProductDetail, CategoryPage, SearchResults, Login, Register, ForgotPassword, ResetPassword, CompareProducts, NotFound (404), AccessDenied (403), ServerError (500), Maintenance (503)

**Protected (5):** Cart, Checkout, OrderTracking, Profile, EditProfile, Wishlist, PaymentResult

**Admin (7):** Dashboard, Products, AddProduct, EditProduct, Categories, Orders, SpecTemplates

Protected by `ProtectedRoute` component at `AppRoutes.jsx:35-56` which checks `isAuthenticated` (redirects to `/login`) and optionally `user.role === 'admin'` (redirects to `/403`).

### Services (12 modules via Axios)

| Service | Base Path | Key Methods | Evidence |
|---------|-----------|-------------|----------|
| `api.js` | — | Axios instance, JWT interceptor, refresh token rotation queue, 423/429 handling | `api.js:1-191` |
| `authService` | `/auth/*` | signIn/signUp/signOut, forgot/reset pwd, email change, MFA, login history, logoutAllSessions | `authService.js:1-130` |
| `productService` | `/products/*` | CRUD, specs, variants, wishlist, compare, categories | Filesystem |
| `cartService` | `/cart/*` | CRUD, clear | Filesystem |
| `orderService` | `/orders/*` | CRUD, tracking, timeline, status | Filesystem |
| `addressService` | `/addresses/*` | CRUD, set-default | Filesystem |
| `adminService` | `/admin/*` | Stats, revenue, AI description | Filesystem |
| `aiService` | `/api/chat` | Chatbot message | Filesystem |
| `locationService` | `/api/locations/*` | Province, district, ward | Filesystem |
| `paymentService` | `/payment/momo/create` | MoMo payment initiation | Filesystem |
| `shippingService` | — | Shipping config/methods/fees | Filesystem |
| `templateService` | `/admin/spec-templates/*` | Spec template CRUD, list types, reorder | Filesystem |

### State Management (Redux Toolkit, 5 slices)

| Slice | State | Evidence |
|-------|-------|----------|
| `authSlice` | user, token, isAuthenticated, loading, error | `store/authSlice.js` |
| `cartSlice` | items, total, syncStatus | `store/cartSlice.js` |
| `navigationSlice` | categoryTree, megaMenu | `store/navigationSlice.js` |
| `productSlice` | items, pagination, filters, loading | `store/productSlice.js` |
| `store/index.js` | Root reducer combining all slices | `store/index.js` |

### Custom Hooks (9)

| Hook | Purpose | Evidence |
|------|---------|----------|
| `useAuth` | Auth lifecycle with singleton init guard | `hooks/useAuth.js:9-77` |
| `useCart` | Cart with API sync, optimistic updates | Filesystem |
| `useChatbot` | Chat state with localStorage persistence | Filesystem |
| `useEditProduct` | Product editing form state | Filesystem |
| `useNavigation` | Category tree + mega menu | Filesystem |
| `useProductDetail` | Product detail with variants, reviews, specs | Filesystem |
| `useProducts` | Listing with filters, pagination | Filesystem |
| `useProfile` | User profile with orders, addresses | Filesystem |
| `useRecommend` | Product recommendations | Filesystem |

---

## BACKEND ARCHITECTURE

### Layer Architecture

```
controllers.py (routes)
    ↓ HTTP request parsing, auth checks, response formatting
services.py (business logic)
    ↓ transaction coordination, cross-entity operations
repositories.py (data access)
    ↓ SQLAlchemy ORM queries
models.py (schema)
    ↓
core/database.py (engine + session factory)
```

### Core Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Config | `core/config.py` | Singleton `Settings` via pydantic-settings, auto-reload on `.env` change |
| Security | `core/security.py` | JWT create/decode (access+refresh), password hash/verify, TOTP secret, token hash |
| Admin Security | `core/admin_security.py` | Account lockout, audit logging decorator, admin rate limiter (in-memory token bucket) |
| Database | `core/database.py` | SQLAlchemy engine, SessionLocal factory, `get_db` dependency |
| Email | `core/email.py` | Async SMTP via aiosmtplib, HTML template builders |
| Rate Limit | `core/rate_limit.py` | slowapi `Limiter` instance with `get_remote_address` key |
| Error Handlers | `middleware/error_handlers.py` | HTTPException, SQLAlchemyError, RateLimitExceeded, generic Exception → JSONResponse |

### Dependency Injection Pattern

```
get_db() → Session dependency (per-request)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") → extracts Bearer token
get_current_user(token, db) → User | 401
  → decode_access_token() → user_id or None
  → services.get_user(db, user_id) → User or None
get_optional_user(token, db) → User | None (no 401)
require_admin(user) → raises 403 if not user.is_admin
```

**Evidence:** `controllers.py` lines 22-47.

---

## DATABASE DESIGN

### 21 Tables — All use UUIDv4 string primary keys

### Entity-Relationship

```
User ──┬── Address (1:N)
       ├── Cart (1:1) ── CartItem (1:N) ── Product
       ├── Order (1:N) ──┬── OrderItem (1:N) ── Product
       │                  ├── OrderStatusHistory (1:N)
       │                  └── Address (N:1)
       ├── Review (1:N) ── Product
       ├── Wishlist (1:N) ── Product
       ├── PasswordResetToken (1:N)
       ├── EmailChangeToken (1:N)
       ├── RefreshToken (1:N)         ← NEW
       ├── AuditLog (1:N)             ← NEW
       └── LoginHistory (1:N)         ← NEW

Category ──┬── Category (self-referencing, parent_id)
           └── Product (1:N)

Product ──┬── ProductSpecification (1:N) [grouped key-value]
          ├── ProductVariant (1:N) [color/version/price/stock]
          ├── ProductHotspot (1:N)
          ├── ProductImage (1:N)
          ├── RelatedProduct (N:M self via join table)
          ├── SpecTemplate (by product_type only, no FK)
          ├── GpuBenchmark / CpuBenchmark (reference data)
          └── GameRequirement (reference data)

SearchLog (no FK relationship — logs anonymous + authenticated searches)
```

### Table Inventory

**Core:** `users`, `categories`, `products`

**Product sub-entities:** `product_variants`, `product_specifications`, `product_hotspots`, `product_images`, `related_products`, `spec_templates`

**Commerce:** `carts`, `cart_items`, `orders`, `order_items`, `order_status_history`, `addresses`

**User sub-entities:** `reviews`, `wishlists`, `password_reset_tokens`, `email_change_tokens`, `search_logs`

**Security (new):** `refresh_tokens`, `audit_logs`, `login_history`

**Reference:** `gpu_benchmarks`, `cpu_benchmarks`, `game_requirements`

### User Table Columns (21 total)

```python
id, email (unique), hashed_password, full_name, avatar_url, is_admin,
role (default "user"), mfa_secret (nullable), mfa_enabled (default False),
last_login_at (nullable), last_login_ip (nullable),
failed_login_attempts (default 0), locked_until (nullable),
created_at
```

### Key Constraints

| Table | Constraint | Purpose |
|-------|------------|---------|
| `users.email` | Unique | Login identity |
| `products.sku` | Unique | Product identifier |
| `categories.slug` | Unique | URL-friendly path |
| `categories.parent_id` | FK → `categories.id` | Self-referencing tree |
| `products.category_id` | FK → `categories.id` nullable | Category membership |
| `order_status_history.changed_by` | FK → `users.id` nullable | Who changed status |
| `refresh_tokens.token_hash` | Indexed | Lookup by hash |
| `audit_logs.user_id` | Indexed | Query by admin |
| `login_history.user_id` | Indexed | Query by user |

**Evidence:** Full model definitions in `models.py` lines 1-431.

---

## AUTHENTICATION FLOW

### Registration (`POST /auth/register`, 3/min rate limit)

```
User submits email + password + full_name
  → hash_password (passlib bcrypt PBKDF2-SHA256)
  → create user in DB (role="user", is_admin=False)
  → create_access_token(user.id) — 1440min, HS256, jti=uuid, type="access"
  → create_refresh_token(user.id) — 10080min, raw token returned, SHA256 hash stored
  → return { access_token, refresh_token, token_type, user }
```

**Evidence:** `controllers.py:115-134`, `services.py:19-24`, `repositories.py:24-35`

### Login (`POST /auth/login`, 5/min rate limit)

```
User submits email + password
  → authenticate_user: find by email → verify_password
    → fail: record_failed_login(db, user) → increment attempts counter
           → if attempts >= 10: set locked_until = now + 15min
           → record_login_attempt(success=False)
           → raise 401
  → check_account_locked() — if locked_until > now, raise 423 with remaining minutes
  → reset_failed_login_count() — clear attempts + locked_until
  → create_access_token(user.id)
  → create_refresh_token_for_user(user.id, device_info, ip_address)
  → record_login_attempt(success=True)
  → update last_login_at, last_login_ip
  → return { access_token, refresh_token, token_type, user }
```

**Evidence:** `controllers.py:137-172`, `core/admin_security.py:32-58`, `services.py:27-31`

### Token Refresh (`POST /auth/refresh`)

```
Client sends { refresh_token }
  → hash_token(refresh_token) → SHA256
  → lookup in refresh_tokens table (not revoked, not expired)
  → revoke old token (revoked=True)
  → create new access_token (24h) + refresh_token (7d)
  → return { access_token, refresh_token }
```

**Evidence:** `controllers.py:175-199`, `repositories.py:981-1017`

### Protected Request

```
Every Axios request:
  → interceptor attaches Authorization: Bearer <access_token>
  → oauth2_scheme extracts token
  → decode_access_token() → checks type != "refresh", decodes sub=user_id
  → get_current_user() → User object
  → endpoint proceeds

On 401:
  → if refresh token exists and not already retrying:
    → queue concurrent requests
    → POST /auth/refresh
    → on success: update stored tokens, retry queued requests
    → on failure: clear tokens, redirect /login
```

**Evidence:** `core/security.py:47-54`, `api.js:96-136`

---

## AUTHORIZATION FLOW

### Two-tier RBAC

| Role | `role` column | `is_admin` column |
|------|---------------|-------------------|
| `user` | "user" | `False` |
| `admin` | "admin" | `True` |

Enforcement: `is_admin` derived from `role == "admin"` at user creation (`repositories.py:31`). Both columns are checked inconsistently — some endpoints use `require_admin()` (which checks `is_admin`), others check `current_user.role != "admin"` directly.

### Protected Resources

| Resource | Auth | Admin-Only | How |
|----------|------|------------|-----|
| Cart, Checkout, Profile, Orders | Required | No | `ProtectedRoute` / `get_current_user` |
| Wishlist, Reviews | Required | No | `get_current_user` |
| Create/Edit/Delete Product | Required | Yes | `require_admin()` |
| Manage Orders (all) | Required | Yes | `require_admin()` |
| Manage Categories | Required | Yes | `require_admin()` |
| Manage Spec Templates | Required | Yes | `require_admin()` or role check |
| Admin Analytics | Required | Yes | `require_admin()` |
| Admin Audit Logs | Required | Yes | `require_admin()` |
| Admin Sessions | Required | Yes | `require_admin()` |
| Upload Image | Required | Yes | `require_admin()` |
| Upload Avatar | Required | No | `get_current_user` |
| AI Description Generate | Required | Yes | `current_user.role != "admin"` check |
| MFA Endpoints | Required | No | `get_current_user` |

**Inconsistency:** `list_spec_template_types` and `delete_spec_template_type` at `controllers.py:627-646` use `current_user.role != "admin"` check instead of `require_admin()`. No functional difference but breaks the pattern.

---

## ADMIN SYSTEM

### Admin Workflows

**Dashboard:**
- Total products, orders, revenue, users (`GET /admin/stats`)
- Monthly/yearly revenue (`GET /admin/revenue/monthly`, `/yearly`)
- Top searches (today) (`GET /admin/analytics/top-searches`)
- Most viewed products (`GET /admin/analytics/top-viewed`)
- Cart abandonment analysis (`GET /admin/analytics/cart-abandonment`)

**Product Management:**
- CRUD + image upload + AI description generation
- Variants: color/version/ram/storage/price/stock
- Specs: grouped key-value with templates
- ApplyTemplateBar: preview & apply spec template from admin-managed presets
- Images: upload with hotspot annotations
- SKU: real-time format validation + debounced uniqueness check

**Category Management:**
- Tree: add/delete with parent-child validation
- Cannot delete if has children or products

**Spec Template Management:**
- Dynamic product_type tabs loaded from DB
- Add/delete spec rows per type
- Dialog to create new template type with preset suggestions
- Delete entire template type with confirmation

**Order Management:**
- List all orders, status transition dropdown
- Simulate next status (dev tool), timeline view

**Security Management:**
- Audit logs: paginated admin action trail (`GET /admin/audit-logs`)
- Active sessions: list with device/IP info (`GET /admin/sessions`)
- Revoke individual session (`DELETE /admin/sessions/{id}`)

---

## AI SYSTEM

### Architecture: Layered Engine Pipeline

The chatbot was refactored from a monolithic `chat_service.py` (which duplicated all logic inline) into a proper layered architecture. All engines are now wired into the pipeline via an `EngineDispatcher`. `chat_service.py` serves as a thin orchestration layer only — it classifies intent, dispatches to engines, formats the response, and persists memory.

```
chat_service.py (orchestration)
  ↓ classify() → intent_engine.py (LLM + regex fallback)
  ↓ dispatch() → engine_dispatcher.py
      ├── search_engine.py       (product search + entity filtering)
      ├── comparison_engine.py   (side-by-side spec comparison)
      ├── gaming_engine.py       (GPU/CPU benchmark vs game reqs)
      ├── recommendation_engine.py (scoring-based recommendations)
      └── fallback → search_engine (default)
  ↓ format()  → openrouter_formatter.py (prompt building + LLM call)
  ↓ persist() → memory.py (ConversationMemory, LRU eviction)
```

### Pipeline Flow

```
POST /api/chat { message, history, session_id }
  → process_chat_request() in chat_service.py
    → 1. Guard: check OpenRouter availability
    → 2. Context: resolve session, build ChatContext
    → 3. Classify: intent_engine.handle(ctx)
         → OpenRouter LLM classifier (meta-llama/llama-3.1-8b-instruct, 200 tok, temp=0.1)
         → fallback regex classifier if LLM fails
         → returns intent + entities on ctx.intent_result
    → 4. Fetch: engine_dispatcher.handle(ctx)
         → routes to correct ChatEngine based on intent
         → each engine reads ctx, sets engine_result.response_context
         → fallback: search_engine for unknown intents
    → 5. Format: openrouter_formatter.format_response()
         → builds intent-specific system prompt
         → calls OpenRouter chat completion
         → returns response text (or fallback message)
    → 6. Persist: memory_store.add_turn(session_id, user_msg, response)
    → 7. Return ChatResponse { intent, entities, message, products, comparison, ... }
```

**Intent classification inputs:** 9 valid intents (`product_search`, `product_compare`, `gaming_check`, `spec_query`, `faq`, `order_support`, `recommendation`, `chitchat`, `greeting`) with JSON entity extraction.

**ConversationMemory:** `chatbot/memory.py` — OrderedDict-based, max 8 turns (16 messages), max 500 sessions, LRU eviction. Singleton `memory_store` instance.

**Fallback:** If OpenRouter API key not configured, returns "Chatbot dang bao tri".

### Module Inventory

| Module | Path | Responsibility |
|--------|------|----------------|
| **Orchestrator** | `chat_service.py` | Thin coordination: classify → dispatch → format → persist. No business logic. |
| **Schemas** | `chatbot/schemas.py` | `ChatContext`, `IntentResult`, `EngineResult`, `ProductCard` dataclasses |
| **Base** | `chatbot/base.py` | `ChatEngine` ABC: `handle()`, `requires_db()`, `actions_for()` |
| **Memory** | `chatbot/memory.py` | `ConversationMemory` with LRU eviction, singleton `memory_store` |
| **Intent Engine** | `chatbot/intent_engine.py` | LLM classifier (OpenRouter) + regex fallback, entity extraction |
| **Search Engine** | `chatbot/search_engine.py` | Domain-aware product search with entity filtering |
| **Comparison Engine** | `chatbot/comparison_engine.py` | Side-by-side spec extraction across 7+ fields |
| **Gaming Engine** | `chatbot/gaming_engine.py` | GPU/CPU benchmark comparison vs game requirements |
| **Recommendation Engine** | `chatbot/recommendation_engine.py` | Scoring-based product recommendations |
| **Product Utils** | `chatbot/product_utils.py` | `serialize_product`, `spec_matches`, `product_cards_from_list` |
| **OpenRouter Formatter** | `chatbot/openrouter_formatter.py` | `OpenRouterFormatter` singleton — builds intent-specific system prompts (7 variants), handles LLM call (direct urllib for classifier, openai SDK for response), all data serialization |
| **Engine Dispatcher** | `chatbot/engine_dispatcher.py` | Maps intents → engines, fallback to search, `actions_for()` |

**Evidence:** `chat_service.py` (now ~150 lines, pure orchestration), `chatbot/` (10 modules, all wired via `engine_dispatcher.py`).

### AI Description Generation (`POST /admin/generate-description`)

Used in admin panel. Sends product data to OpenRouter with a strict prompt to avoid hallucination. Returns structured JSON (short_description, key_highlights, full_description, performance_summary, seo_description). Vietnamese language.

**Evidence:** `controllers.py:949-1039`

### Recommendation Engine (in `services.py`)

Scoring algorithm combining popularity (views, orders, cart adds, rating) with personalization (category/brand history, wishlist, cart abandonment). Fallback to popularity-only for anonymous users. Similar products scored by category/brand/type/price proximity. Cart recommendations via co-purchase analysis.

**Evidence:** `services.py:756-1038`

---

## PAYMENT SYSTEM

### MoMo Integration

```
POST /payment/momo/create
  → HMAC-SHA256 signature from 10 fields
  → POST to test gateway
  → Return { payUrl, resultCode, message }
  → Frontend redirects to payUrl

MoMo → POST /payment/momo/ipn (server-to-server)
  → Verify HMAC-SHA256 signature
  → resultCode == 0 → order status = "confirmed"
  → else → order status = "payment_failed"
```

**Evidence:** `services.py:655-753`, `controllers.py:360-406`

### COD (Cash on Delivery)

If `payment_method = "cod"`, order is created with status "pending" without payment gateway interaction.

---

## ORDER MANAGEMENT

### Order Status Machine

```
VALID_STATUS_TRANSITIONS = {
    "pending": ["confirmed", "cancelled", "payment_failed"],
    "confirmed": ["processing"],
    "processing": ["shipped"],
    "shipped": ["out_for_delivery"],
    "out_for_delivery": ["delivered"],
    "delivered": ["return_requested"],
    "return_requested": ["returned"],
    "returned": ["refunded"],
    "cancelled": [],           # terminal
    "payment_failed": [],      # terminal
    "refunded": [],            # terminal
}
```

on `shipped`: auto-generates `tracking_code` ("TK" + 9 digits) + `shipping_provider` (random: GHN/GHTK/Viettel Post/FedEx) + `estimated_delivery` (+2-7 days).

**Evidence:** `services.py:397-409, 412-443`

---

## API STRUCTURE

### 80+ endpoints across modules

**Auth** (`/auth/*` — 16 endpoints):
`POST register`, `POST login`, `POST refresh`, `POST logout`, `POST logout-all`, `GET me`, `GET mfa/status`, `POST mfa/setup`, `POST mfa/verify`, `POST mfa/disable`, `GET login-history`, `POST forgot-password`, `POST reset-password`, `POST request-email-change`, `GET verify-email-change`, `POST change-password`

**Products** (`/products/* — 14 endpoints):
`GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`, `GET /{id}/specifications`, `POST /{id}/specifications`, `PUT /{id}/specifications`, `GET /{id}/reviews`, `POST /{id}/reviews`, `GET /{id}/variants`, `GET /{id}/similar`, `GET /{id}/images`, `PUT /admin/{id}/images`

**Cart** (5 endpoints): `GET /cart`, `POST /cart/items`, `PATCH /cart/items/{id}`, `DELETE /cart/items/{id}`, `DELETE /cart/clear`

**Orders** (7 endpoints): `POST /orders`, `GET /orders`, `GET /orders/{id}`, `PUT /orders/{id}/status`, `GET /orders/{id}/tracking`, `GET /orders/{id}/timeline`, `POST /admin/orders/{id}/simulate-next`

**Admin** (15 endpoints): `GET /admin/orders`, `GET /admin/stats`, `GET /admin/revenue/monthly`, `GET /admin/revenue/yearly`, `POST /admin/orders/{id}/simulate-next`, `POST /admin/generate-description`, `GET /admin/analytics/top-searches`, `GET /admin/analytics/top-viewed`, `GET /admin/analytics/cart-abandonment`, `GET /admin/check-sku`, `GET /admin/spec-templates`, `GET /admin/spec-templates/types`, `POST /admin/spec-templates`, `DELETE /admin/spec-templates/{id}`, `DELETE /admin/spec-templates/type/{type}`, `PUT /admin/spec-templates/reorder`, `GET /admin/audit-logs`, `GET /admin/sessions`, `DELETE /admin/sessions/{id}`

**File Upload** (2): `POST /upload-image`, `POST /upload-avatar`

**Chat** (1): `POST /api/chat`

**Payment** (2): `POST /payment/momo/create`, `POST /payment/momo/ipn`

**System** (4 in `routes/system.py`): health check

**Locations** (4 in `routes/locations.py`): provinces, districts, wards, search

**Navigation** (4 in `routes/navigation.py`): category tree, mega menu, flat categories, brands

**Other** (10+): addresses CRUD, categories CRUD, wishlist CRUD, reviews, recommendations, cart recommendations, spec templates public, profile update, search suggestions

---

## BUSINESS RULES

1. **SKU:** 3-50 chars, only A-Z/0-9/-/_ enforced by DB unique constraint + debounced API check
2. **Stock:** Decrement on order creation; validated before order
3. **Reviews:** One per user per product; update if exists
4. **Rating:** Average of all review ratings
5. **Shipping:** 3 tiers: standard (3d/15k VND), express (1d/35k), same-day (0d/75k)
6. **Address:** One default per user; setting new default unsets old
7. **Cart:** One per user; item quantity merge on re-add
8. **Category hierarchy:** `level` column, `path` column for breadcrumbs; prevent delete if has children or products
9. **Password reset:** Token expires 1h, one-time use
10. **Email change:** Requires verification via token link
11. **Search logging:** Logs queries with user_id (if authenticated) + result count
12. **Order status transitions:** Strict FSM; invalid transitions rejected
13. **Image uploads:** Max 5MB, allowed: jpg/jpeg/png/webp/gif; stored as `static/images/{uuid}.ext`
14. **Account lockout:** 10 consecutive failed logins → 15-min lock (`locked_until`). Successful login resets counter.
15. **Refresh token rotation:** Each use revokes old token and issues new pair. Old tokens cannot be reused.
16. **Audit logging:** Admin actions logged in `audit_logs` with user, action, target, IP, timestamp (backend functions exist; decorator not wired to endpoints).

---

## SECURITY ARCHITECTURE

### Implemented Mechanisms

| Mechanism | Implementation | Status |
|-----------|---------------|--------|
| Password hashing | passlib bcrypt (PBKDF2-SHA256) | ✅ |
| JWT signing | HS256 with configurable secret, `jti` + `type` claims | ✅ |
| Token refresh rotation | Refresh token SHA-256 hash in DB, old revoked on use | ✅ |
| Multi-factor auth | TOTP via pyotp (setup/verify/disable) | ✅ Partially — no login enforcement |
| Account lockout | 10 failed → 15-min lock (HTTP 423) | ✅ |
| Admin audit logging | `audit_logs` table + `log_admin_action()` function | ✅ Partially — decorator not wired |
| Login history tracking | `login_history` table (success + fail) | ✅ |
| Rate limiting (slowapi) | 3/min register, 5/min login, 3/min forgot-pwd | ✅ |
| Admin rate limiting | In-memory token bucket 120 req/min | ✅ |
| CORS | Whitelist: localhost:5173, 127.0.0.1:5173 | ✅ |
| Input validation | Pydantic schemas (min_length, max_length, regex) | ✅ |
| Authorization | `require_admin()` dependency + role checks | ✅ |
| SQL injection | SQLAlchemy ORM (parameterized queries) | ✅ |
| Token expiration | JWT `exp` claim + refresh `expires_at` + `revoked` flag | ✅ |
| Session management | List + revoke by ID | ✅ |
| File upload | Extension whitelist + content-type + size (5MB) | ✅ |
| Frontend auto-refresh | Axios interceptor queues + retries on 401 | ✅ |
| Frontend error pages | 403/404/500/503 pages | ✅ |
| Frontend rate limit UX | Toast for 423 (locked) + 429 (rate limited) | ✅ |

### Not Implemented (no code evidence)

| Mechanism | Notes |
|-----------|-------|
| CSRF protection | No CSRF token, no double-submit cookie |
| IP allowlist for admin | No middleware or config |
| Login MFA enforcement | MFA can be enabled but login doesn't require 2FA code |
| Rate limit on register endpoint | Added as of this analysis (3/min) |
| HTTPS enforcement | Not in application code (expected at reverse proxy) |
| Security headers | No HSTS, CSP, X-Frame-Options headers |
| API key rotation | Manual via `.env` |
| Device fingerprinting | No device tracking beyond user-agent |

---

## EXTERNAL INTEGRATIONS

| Service | Type | Auth Method | Evidence |
|---------|------|-------------|----------|
| OpenRouter (LLM) | OpenAI-compatible REST at `openrouter.ai/api/v1` | API key in `.env` | `chatbot/openrouter_formatter.py` (singleton), `chatbot/intent_engine.py` (classifier) |
| MoMo Payment | REST API (test endpoint) | HMAC-SHA256 signing with 3 keys | `services.py:655-753` |
| SMTP Email | aiosmtplib (Google SMTP) | App password | `core/email.py:1-143` |
| Vietnam Location Data | Static JSON (63 provinces, ~700 districts, ~10k wards) | Built-in | `routes/locations.py` |

---

## DATA FLOW

### Checkout Flow
```
User → POST /orders { items, address_id, payment_method, shipping_method }
  → services.create_order()
    → validate stock (product.stock -= quantity per item)
    → calculate total_amount (items + shipping_fee)
    → create Order (status: "pending")
    → create OrderItems
    → clear cart items
  → if payment_method = "momo":
    → POST /payment/momo/create → payUrl
    → return { payUrl }
    → Frontend redirects to MoMo
    → MoMo → POST /payment/momo/ipn → update order status
    → MoMo → redirect to /payment/result
  → if payment_method = "cod":
    → return order confirmation
```

### Chatbot Flow
```
User → POST /api/chat { message, history, session_id }
  → chat_service.process_chat_request()
    → 1. Guard: check OpenRouter availability
    → 2. Context: resolve session from memory or payload history
    → 3. Classify: intent_engine.handle(ctx)
         → LLM classifier or regex → { intent, entities }
    → 4. Dispatch: engine_dispatcher.handle(ctx)
         → routes to search / comparison / gaming / recommendation engine
    → 5. Format: openrouter_formatter.format_response()
         → intent-specific system prompt → OpenRouter → response text
    → 6. Persist: memory_store.add_turn(session_id, msg, response)
    → 7. Return ChatResponse { intent, entities, message, products, ... }
```

### Password Reset Flow
```
User → POST /auth/forgot-password { email }
  → services.create_reset_token_and_send_email()
    → generate token (secrets.token_urlsafe(32))
    → store in password_reset_tokens (expires: 1 hour)
    → send email with reset link via SMTP
  → User clicks link → /reset-password?token=...
  → POST /auth/reset-password { token, new_password }
    → validate token (exists, not used, not expired)
    → update user password (hash_password)
    → mark token as used
```

---

## EVENT FLOW

No event-driven architecture. All flows are synchronous request-response. No message queue (RabbitMQ, Redis pub/sub, Celery) or background task system. MoMo IPN is the only external callback (synchronous HTTP POST handled inline).

---

## ERROR HANDLING

### Backend

```python
# Custom error format via middleware:
{ "detail": "message", "error_code": status_code }

# 4 handlers registered in main.py:
- RateLimitExceeded → 429 (via slowapi built-in)
- HTTPException → status code from exception
- SQLAlchemyError → 500 + sanitized message
- Exception → 500 + "Internal server error"
```

**Evidence:** `main.py:48-51`, `middleware/error_handlers.py`

### Frontend

- Axios interceptor handles all HTTP errors with toast notifications
- `ErrorBoundary` React component catches render errors with retry/reload
- `OfflineBanner` detects connection state via `navigator.onLine` + events
- Status code handling: 400 (toast), 401 (auto-refresh or logout), 403 (redirect to /403), 404 (redirect to /404), 422 (per-field toasts), 423 (locked toast), 429 (rate limit toast), 5xx (redirect to error pages)

**Evidence:** `api.js:61-188`

---

## DEPLOYMENT STRUCTURE

```
project/
├── Backend/
│   ├── .env                  # DB, JWT, MoMo, SMTP, OpenRouter, CORS
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # Entry: uvicorn (auto-migrate + seed)
│       ├── core/             # Config, DB, Security + AdminSecurity, Email, RateLimit
│       ├── routes/           # Health, Locations, Navigation
│       ├── middleware/       # Error handlers
│       ├── chatbot/          # 10 modules (engines, memory, dispatcher, formatter, schemas)
│       ├── static/           # Uploaded images
│       ├── controllers.py    # All entity routes (~80 endpoints)
│       ├── services.py       # Business logic + recommendations (1096 lines)
│       ├── repositories.py   # Data access (1069 lines)
│       ├── models.py         # 21 SQLAlchemy models
│       ├── schemas.py        # Pydantic schemas (568 lines)
│       ├── chat_service.py   # Active chat pipeline (500 lines)
│       ├── breadcrumb_service.py
│       ├── seed.py + seed_data.py
│       └── data/             # Vietnam location JSON
├── Frontend/
│   └── src/
│       ├── main.jsx          # Entry
│       ├── App.jsx           # Router + layouts
│       ├── components/       # 38 reusable (incl. SkuInput, ApplyTemplateBar)
│       ├── pages/            # 29 pages (22 user + 7 admin)
│       ├── hooks/            # 9 custom hooks
│       ├── services/         # 12 API modules
│       ├── store/            # Redux (5 slices)
│       ├── routes/           # AppRoutes.jsx
│       ├── layouts/          # MainLayout, AdminLayout
│       ├── contexts/         # ThemeContext
│       ├── locales/          # i18n (en, vi)
│       └── utils/            # Constants, formatters, validators
└── package.json
```

---

## ACTORS

| Actor | Auth | Permissions |
|-------|------|-------------|
| **Guest** | None (unauthenticated) | Browse products, search, view details, register, use chatbot (limited), compare products |
| **Customer** | JWT (access + refresh) | Guest + profile management, cart, checkout (COD/MoMo), orders, reviews, wishlist, full chatbot, MFA management, own login history |
| **Admin** | JWT (is_admin=True / role="admin") | Customer + all admin CRUD, analytics, AI description, spec templates, all orders, audit logs, user sessions |
| **OpenRouter AI** | External API key | Intent classification, chat response, product description generation |
| **MoMo Gateway** | External via HMAC-SHA256 | Payment request processing, IPN callback |
| **SMTP Server** | External via app password | Password reset emails, email change verification |

---

## USE CASE CANDIDATES

### Guest
- Browse product catalog with filters (category, search, featured, sort, product_type, brand)
- Search products with autocomplete suggestions
- View product details, specs (grouped), variants, reviews, similar products
- Compare products side-by-side
- Register new account
- Use chatbot for product inquiries

### Customer
- Login/logout with refresh token rotation
- Manage profile (avatar, name, email change via verification, password change)
- Manage shipping addresses (CRUD, set default)
- Manage shopping cart (add/update/remove/clear with variant support)
- Checkout with COD or MoMo payment
- View order history and track delivery status (timeline)
- Write product reviews (one per product)
- Manage wishlist
- Use chatbot with conversation history (8-turn)
- Enable/disable MFA for own account
- View personal login history (last 20 attempts)

### Admin
- View dashboard with sales analytics (stats, monthly/yearly revenue)
- Manage products (create, edit, delete with SKU validation)
- Manage product variants (color/version/ram/storage/price/stock)
- Manage product specifications (grouped key-value with bulk replace)
- Manage product images (multi-image with primary/sort)
- Manage spec templates (create/edit/delete by product_type)
- Upload product images with hotspot annotations
- Manage categories (tree CRUD)
- View and manage all orders (status transitions with FSM)
- Simulate order status transitions (dev tool)
- Generate AI product descriptions
- View analytics (top searches, top viewed, cart abandonment)
- View admin audit logs
- List/revoke active sessions

---

## SEQUENCE DIAGRAM CANDIDATES

### Token Refresh Sequence
```
Client                    Frontend (Axios)              Backend
  │                            │                           │
  │  Any API call              │                           │
  │ ──────────────────────────►│                           │
  │                            │ POST /some/resource       │
  │                            │ ─────────────────────────►│
  │                            │ 401 Unauthorized          │
  │                            │◄──────────────────────────│
  │                            │                           │
  │                            │ POST /auth/refresh        │
  │                            │ { refresh_token }         │
  │                            │ ─────────────────────────►│
  │                            │                           │→ hash_token()
  │                            │                           │→ get_refresh_token_by_hash()
  │                            │                           │→ revoke old token
  │                            │                           │→ create new access + refresh
  │                            │ 200 { access, refresh }   │
  │                            │◄──────────────────────────│
  │                            │                           │
  │                            │ Retry original request    │
  │                            │ ─────────────────────────►│
  │                            │ 200 OK                    │
  │  Response                  │◄──────────────────────────│
  │ ◄──────────────────────────│                           │
```

### Account Lockout Sequence
```
Client                    Backend
  │                           │
  │ POST /auth/login (1-9x)   │
  │ ─────────────────────────►│→ verify_password fails
  │                           │→ record_failed_login()
  │                           │  → failed_login_attempts++
  │ 401 Invalid credentials   │
  │◄──────────────────────────│
  │                           │
  │ POST /auth/login (10th)   │
  │ ─────────────────────────►│→ verify_password fails
  │                           │→ failed_login_attempts >= 10
  │                           │→ locked_until = now + 15min
  │ 401 Invalid credentials   │
  │◄──────────────────────────│
  │                           │
  │ POST /auth/login (11th)   │
  │ ─────────────────────────►│→ check_account_locked()
  │ 423 Account locked,       │   locked_until > now
  │ try again in X min        │
  │◄──────────────────────────│
```

---

## ACTIVITY DIAGRAM CANDIDATES

### Admin Product Edit
```
1. Navigate to /admin/products/edit/:id
2. Fetch product (GET /products/:id)
3. Fetch specs (GET /products/:id/specifications)
4. Populate form (basic, variants, specs, images)
5. User edits tabs:
   a. Basic: name, description, price, stock, category, brand, SKU, status
   b. Variants: color/version/ram/storage/price/stock
   c. Specs: grouped key-value with templates
   d. Images: URLs with primary/sort/hotspots
6. SKU input: real-time format validation + debounced uniqueness check
7. Submit:
   → PUT /products/:id (basic info)
   → PUT /products/:id/specifications (bulk replace)
   → Individual variant POST/PUT/DELETE
8. Navigate back to /admin/products
```

---

## COMPONENT DIAGRAM CANDIDATES

```
Backend Components:
├── Web Layer (FastAPI routes)
│   ├── AuthController (16 endpoints)
│   ├── ProductController (14 endpoints)
│   ├── CartController (5 endpoints)
│   ├── OrderController (7 endpoints)
│   ├── AdminController (19 endpoints)
│   ├── ChatController (1 endpoint)
│   └── SystemController (health, locations, navigation)
├── Business Layer
│   ├── AuthService (register, authenticate, create/rotate/revoke refresh tokens)
│   ├── ProductService (CRUD, specs, variants, search, recommendations)
│   ├── OrderService (create, FSM, tracking, simulate)
│   ├── PaymentService (MoMo create + verify signature)
│   ├── EmailService (reset password, email change)
│   ├── RecommendationEngine (popularity + personalization + co-purchase)
│   ├── ChatService (orchestration: classify → dispatch → format → persist)
│   └── Chatbot Engines (intent, search, comparison, gaming, recommendation, formatter, memory)
├── Data Layer
│   ├── Repositories (CRUD per entity, 1069 lines)
│   ├── SQLAlchemy Models (21 tables)
│   └── Database Session Manager
└── Infrastructure
    ├── Config (pydantic-settings with auto-reload)
    ├── Security (JWT HS256 + bcrypt + TOTP + refresh rotation)
    ├── Admin Security (lockout + audit log + rate limiter)
    ├── Rate Limiter (slowapi)
    ├── Error Middleware
    └── Email Client (aiosmtplib)

Frontend Components:
├── Pages (29)
├── Layouts (MainLayout, AdminLayout)
├── Components (38 reusable)
│   ├── Product: Card, VariantSelector, SpecsTable, CompareButton
│   ├── Cart: Item, Summary
│   ├── Checkout: AddressSelector, ShippingSelector, PaymentSelector
│   ├── Chatbot: Floating button, Panel, Message list
│   ├── Auth: Login, Register, ForgotPassword
│   ├── Admin: Dashboard, ProductForm, VariantManager, CategoryTree
│   ├── Template: ApplyTemplateBar, SpecTemplatesPage
│   └── Common: Navbar, Footer, Breadcrumbs, StarRating, ErrorBoundary, SkuInput
├── Services (12 API modules via Axios)
├── State (Redux: auth, cart, navigation, product)
├── Hooks (9 custom hooks)
└── Utils (i18n, constants, formatters, validators)
```

---

## DEPLOYMENT DIAGRAM CANDIDATES

Single-server deployment:

```
Internet
   │
┌──┴──┐
│Nginx│ (reverse proxy, SSL termination, static file serving for production)
└──┬──┘
   │
┌──┴────────────────┐
│   Application Server  │
│                       │
│  ┌─────────────────┐  │
│  │ Frontend (React)  │  │  :5173 dev / :80 prod
│  │ Vite/Nginx       │  │
│  └────────┬────────┘  │
│           │ HTTP JSON │
│  ┌────────▼────────┐  │
│  │ Backend (FastAPI)│  │  :8000
│  │ Uvicorn         │  │
│  └────────┬────────┘  │
│           │            │
│  ┌────────▼────────┐  │
│  │ MySQL Database  │  │
│  └─────────────────┘  │
└────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼────┐
│ MoMo API│ │OpenRouter│ (external)
└─────────┘ └─────────┘
┌──────────┐
│ SMTP     │ (Google/Gmail)
└──────────┘
```

---

## ERD CANDIDATES

See "Database Design" section above for complete entity-relationship description.

---

## SECURITY DIAGRAM CANDIDATES

```
                    ┌─────────────────────────┐
                    │   Client Browser         │
                    │ localStorage:            │
                    │  shop_token (access JWT) │
                    │  shop_refresh_token      │
                    │  shop_user               │
                    └───────────┬─────────────┘
                                │ HTTPS
                    ┌───────────▼─────────────┐
                    │   FastAPI Middleware      │
                    │                          │
                    │ 1. CORSMiddleware         │
                    │ 2. SlowAPIMiddleware      │
                    │    (3/min reg, 5/min     │
                    │     login, 3/min forgot) │
                    │ 3. Error handlers         │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
   ┌──────────▼────────┐ ┌─────▼──────┐ ┌─────────▼─────────┐
   │ Auth Layer         │ │Admin Layer │ │ Rate Limit Layer   │
   │                    │ │            │ │                    │
   │ oauth2_scheme      │ │ require_   │ │ AdminRateLimiter   │
   │ decode_access_token│ │ admin()    │ │ (120 req/min,     │
   │ get_current_user   │ │ role check │ │  in-memory)       │
   │                    │ │ audit_     │ │                    │
   │ MFA: TOTP/pyotp   │ │ admin_     │ │ Account lockout    │
   │ Refresh rotation   │ │ action()   │ │ (10 failed → 15m) │
   └────────────────────┘ └────────────┘ └────────────────────┘
```

---

## ARCHITECTURE INCONSISTENCIES

| # | Issue | Severity | Evidence |
|---|-------|----------|----------|
| 1 | **Inconsistent admin role checks** — Most endpoints use `require_admin()` (checks `is_admin`), but `list_spec_template_types` and `delete_spec_template_type` check `current_user.role != "admin"` directly. | Medium | `controllers.py:627-646` vs `controllers.py:45-47` |
| 2 | **`is_admin` is derived but stored** — `is_admin` column is set at creation from `role == "admin"` but is never synced if `role` changes. | Low | `repositories.py:31` |
| 3 | **MFA not enforced on login** — MFA can be enabled but login endpoint never checks or requires 2FA code. | Medium | `controllers.py:137-172` has no MFA verification step |
| 4 | **admin_security.py decorator not used** — `audit_admin_action` decorator exists but is not applied to any endpoint. `require_admin_with_audit` has empty body. | Medium | Grep shows zero usage in `controllers.py` |
| 5 | **Frontend page counts outdated** — SYSTEM_ARCHITECTURE lists 29 pages but actual file count is 29 (22 user + 7 admin). Matches now. | Resolved | Filesystem check |
| 6 | **`MFAVerifyRequest.token` field is unused** — Field exists in schema but `mfa_verify()` handler never reads it (only verifies code). | Low | `schemas.py:37-39`, `controllers.py:246-261` |

---

## OUTDATED IMPLEMENTATION DETAILS

| Detail | Previously Claimed | Actual Implementation |
|--------|-------------------|----------------------|
| Chatbot engine pipeline | `chat_service.py` did everything directly; `chatbot/` modules were dormant | Refactored: `chat_service.py` is thin orchestration, 10 `chatbot/` modules wired via `engine_dispatcher.py` |
| `openrouter_formatter.py` is chat formatter | Only used for admin AI product description | Refactored: now the unified formatter for both chatbot responses and admin AI description |
| 18 database tables | Original count before security additions | Now 21 tables (+3 security tables) |
| Auth: single JWT, no refresh | Original impl | Now dual-token with rotation |
| Rate limit: 2 endpoints | 5/min login + 3/min forgot | +3/min register (just added) |
| Security: no MFA/lockout/audit | Original state | All implemented now |

---

## VERIFIED IMPLEMENTATION DETAILS

All architectural statements in this document are verified against the codebase at commit time. Key verification sources:

- `main.py`: Entry point, middleware stack, auto-migration
- `controllers.py`: All 80+ endpoints, auth flow, admin logic (1206 lines)
- `services.py`: Business logic, recommendations, refresh/MFA/audit services (1096 lines)
- `repositories.py`: Data access, CRUD operations (1069 lines)
- `models.py`: 21 SQLAlchemy models (431 lines)
- `schemas.py`: All Pydantic schemas (568 lines)
- `core/security.py`: JWT create/decode, password hash, TOTP secret (73 lines)
- `core/admin_security.py`: Account lockout, audit logging, rate limiter (184 lines)
- `chat_service.py`: Chatbot orchestration layer (~150 lines, refactored)
- `chatbot/`: 10 modules (schemas, base, memory, intent, search, comparison, gaming, recommendation, product_utils, openrouter_formatter, engine_dispatcher)
- `Frontend/src/services/api.js`: Axios instance with refresh interceptor
- `Frontend/src/services/authService.js`: Auth API with MFA methods
- `Frontend/src/routes/AppRoutes.jsx`: All frontend routes
- `Frontend/src/hooks/useAuth.js`: Auth hook with logoutAllSessions
- `Frontend/src/pages/admin/`: 7 admin page components
