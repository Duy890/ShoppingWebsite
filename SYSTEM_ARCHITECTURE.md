# SYSTEM ARCHITECTURE — Electronics E-Commerce Platform

## SYSTEM OVERVIEW

Full-stack electronics e-commerce platform with AI-powered chatbot, MoMo payment gateway, and admin dashboard. Built with FastAPI + React SPA architecture, using SQLAlchemy ORM with MySQL.

---

## SYSTEM PURPOSE

Commerce platform for electronics retail (laptops, phones, tablets, audio, accessories) in Vietnam market. Provides product catalog, shopping cart, checkout, order tracking, AI shopping assistant, gaming performance checker, and full admin product/order management.

---

## TECH STACK

| Layer               | Technology              | Version  |
| ------------------- | ----------------------- | -------- |
| Backend Framework   | FastAPI                 | 0.116.0  |
| ASGI Server         | Uvicorn                 | 0.24.0   |
| ORM                 | SQLAlchemy              | 2.0.22   |
| Validation          | Pydantic                | 2.8.0    |
| Settings            | pydantic-settings       | 2.8.0    |
| Auth                | python-jose (JWT) + passlib (bcrypt) | — |
| Database Driver     | PyMySQL                 | 1.1.0    |
| Email               | aiosmtplib              | 3.0.1    |
| LLM Client          | openai SDK              | 1.54.3   |
| Rate Limiting       | slowapi                 | 0.1.9    |
| Frontend            | React 18 + Vite + TypeScript | —    |
| State               | Redux Toolkit           | —        |
| Styling             | Tailwind CSS            | —        |
| i18n                | react-i18next           | EN + VI  |
| Payment             | MoMo (test gateway)     | —        |

---

## HIGH LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React SPA)                      │
│  Vite dev server on :5173, served via Nginx in production   │
│                                                             │
│  Pages → Hooks → Services (Axios) → REST API               │
│  State: Redux Toolkit (auth, cart, navigation, products)    │
│  i18n: react-i18next (EN/VI)                                │
│  Theme: dark/light via React Context + localStorage         │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP (JSON)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               Backend (FastAPI on :8000)                     │
│                                                             │
│  Middleware: CORS, Rate Limiter, Error Handlers              │
│                                                             │
│  ┌───────────┐  ┌──────────┐  ┌─────────────────────────┐  │
│  │ Routes    │→ │ Services │→ │ Repositories (DB Layer)  │  │
│  │controllers│  │services  │  │ repositories             │  │
│  │ routes/   │  │chatbot/  │  │                          │  │
│  └─────┬─────┘  └────┬─────┘  └──────────┬──────────────┘  │
│        │              │                   │                 │
│        ▼              ▼                   ▼                 │
│  ┌───────────┐  ┌──────────┐  ┌─────────────────────────┐  │
│  │ Auth      │  │ AI/Chat  │  │ Database (MySQL)        │  │
│  │ JWT/BCrypt│  │OpenRouter│  │ 18 tables               │  │
│  │ Rate Limit│  │ 7 engines│  │                         │  │
│  └───────────┘  └──────────┘  └─────────────────────────┘  │
│                                                             │
│  External: MoMo Payment API, SMTP Email                     │
└─────────────────────────────────────────────────────────────┘
```

---

## FRONTEND MODULES

### Pages (22 user + 6 admin)

**Public:**
| Page | Purpose |
|------|---------|
| `Home` | Hero carousel, featured products, recommendations, SEO banners |
| `ProductList` | Filterable grid with category/brand/price/sort |
| `CategoryPage` | Category-filtered product list |
| `ProductDetail` | Image gallery, variant selector, specs, reviews, similar products |
| `SearchResults` | Query results grid |
| `Cart` | Items with qty controls, summary, frequently-bought-together |
| `Checkout` | Address selection, shipping method, COD/MoMo payment |
| `PaymentResult` | MoMo redirect landing (success/failure) |
| `OrderTracking` | Visual timeline + progress bar + shipping details |
| `Profile` | Orders history + address management + settings |
| `EditProfile` | Avatar, name, email verification, password change |
| `Wishlist` | Saved items |
| `CompareProducts` | Side-by-side spec comparison table |
| `Login` / `Register` / `ForgotPassword` / `ResetPassword` | Auth forms |
| `NotFound` (404) / `AccessDenied` (403) / `ServerError` (500) / `Maintenance` (503) | Error pages |

**Admin:**
| Page | Purpose |
|------|---------|
| `Dashboard` | Stats cards + revenue charts + analytics |
| `Products` | CRUD table with search/filter/pagination |
| `AddProduct` | Full form with AI description generation |
| `EditProduct` | Tabbed: basic, variants, specs, images with hotspots |
| `Categories` | Tree management with expand/collapse |
| `Orders` | Table with status updates + simulate next status |

### Services (API layer via Axios)

| Service          | Base Path                | Key Methods |
|------------------|--------------------------|-------------|
| `api.js`         | —                        | Axios instance, JWT interceptor, 401 auto-logout, offline detection |
| `authService`    | `/auth/*`                | login, register, forgot/reset password, email change |
| `productService` | `/products/*`            | CRUD, specs, variants, wishlist, compare, categories, templates |
| `cartService`    | `/cart/*`                | CRUD, clear |
| `orderService`   | `/orders/*`              | CRUD, tracking, timeline, status |
| `addressService` | `/addresses/*`           | CRUD, set-default |
| `adminService`   | `/admin/*`               | Stats, revenue, AI description generation |
| `aiService`      | `/api/chat`              | Chatbot message |
| `locationService`| `/api/locations/*`       | Province, district, ward |
| `paymentService` | `/payment/momo/create`   | MoMo payment initiation |
| `shippingService`| —                        | Shipping config/methods/fees |

### State Management (Redux Toolkit)

| Slice              | State                                        | Async Thunks |
|--------------------|----------------------------------------------|-------------|
| `authSlice`        | user, token, isAuthenticated, loading, error | login, register, fetchProfile |
| `cartSlice`        | items, total, syncStatus                     | fetchCart, addItem, updateItem, removeItem, clearCart |
| `navigationSlice`  | categoryTree, megaMenu                       | fetchCategoryTree, fetchMegaMenu |
| `productSlice`     | items, pagination, filters, loading          | fetchProducts |

### Hooks (Logic layer)

| Hook                 | Purpose |
|----------------------|---------|
| `useAuth`            | Auth lifecycle: signIn/signUp/signOut/updateProfile, singleton guard |
| `useCart`            | Cart with API sync, optimistic updates |
| `useChatbot`         | Chat state with localStorage persistence |
| `useEditProduct`     | Product editing: variants/specs/images/hotspots/breadcrumbs |
| `useNavigation`      | Category tree + mega menu data |
| `useProductDetail`   | Product detail: variants, reviews, specs |
| `useProducts`        | Listing with filters, pagination, CRUD |
| `useProfile`         | User profile: orders, addresses, confirm dialogs |
| `useRecommend`       | Product recommendations |

### Key Components

| Component | Purpose |
|-----------|---------|
| `Navbar` | Sticky header: logo, search with suggestions, mega menu (3-level), cart badge, user dropdown, i18n toggle, theme toggle |
| `CategoryMegaMenu` | Full-width: L1 sidebar + L2/L3 grid with hover delay |
| `Chatbot` | Floating button → slide-up panel → message list → product cards/comparison tables/gaming badges |
| `ProductCard` | Grid card: image, rating stars, brand, price, wishlist heart, add-to-cart |
| `VariantSelector` | Color swatches + version with cross-availability |
| `SpecificationEditor` | Grouped spec table editor with templates |
| `AdminVariantManager` | Variant CRUD table with auto-color suggestions |
| `AIDescriptionGenerator` | AI-powered description with copy-to-form |
| `AddressSelector` / `AddressFormModal` | Cascading province→district→ward comboboxes |
| `ErrorBoundary` | Class-based with dev details, retry/reload |
| `OfflineBanner` | Connection monitor with auto-hide |

---

## BACKEND MODULES

### Layer Architecture

```
controllers.py  →  services.py  →  repositories.py  →  models.py (SQLAlchemy)
     │                 │                  │
     ▼                 ▼                  ▼
  schemas.py      chatbot/            database.py
  (Pydantic)      (7 engines)         (SQLAlchemy engine)
```

### Routes (controllers.py)

Managed by `APIRouter()` with 70+ endpoints across modules:

**Auth** (`/auth/*`):

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | User registration (rate-limited) |
| POST | `/auth/login` | Login, returns JWT + user (5/min) |
| GET | `/auth/me` | Current user profile |
| POST | `/auth/forgot-password` | Email reset link (3/min) |
| POST | `/auth/reset-password` | Token-based reset |
| POST | `/auth/request-email-change` | Verify new email |
| GET | `/auth/verify-email-change` | Apply email change via link |
| POST | `/auth/change-password` | Current password → new |

**Products** (`/products/*`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List with filters, search, sort, pagination |
| GET | `/products/{id}` | Detail with eager-loaded specs, variants, reviews |
| POST | `/products` | Create (admin) |
| PUT | `/products/{id}` | Update (admin) |
| DELETE | `/products/{id}` | Delete (admin) |
| GET | `/products/{id}/specifications` | Grouped specs |
| POST | `/products/{id}/specifications` | Add spec (admin) |
| PUT | `/products/{id}/specifications` | Bulk replace (admin) |
| GET | `/products/{id}/reviews` | Reviews |
| POST | `/products/{id}/reviews` | Add review |
| GET | `/products/{id}/variants` | Variants |
| GET | `/products/{id}/similar` | Similar products |

**Cart** (`/cart/*`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cart` | Get/create cart + items |
| POST | `/cart/items` | Add item (qty merge) |
| PATCH | `/cart/items/{id}` | Update quantity |
| DELETE | `/cart/items/{id}` | Remove item |
| DELETE | `/cart/clear` | Clear cart |

**Orders** (`/orders/*`):

| Method | Path | Description |
|--------|------|-------------|
| POST | `/orders` | Create from cart |
| GET | `/orders` | User's orders |
| GET | `/orders/{id}` | Order detail |
| PUT | `/orders/{id}/status` | Update status (admin) |
| GET | `/orders/{id}/tracking` | Tracking info |
| GET | `/orders/{id}/timeline` | Status history |

**Admin** (`/admin/*`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/orders` | All orders |
| GET | `/admin/stats` | Dashboard stats |
| GET | `/admin/revenue/monthly` | Monthly revenue |
| GET | `/admin/revenue/yearly` | Yearly revenue |
| POST | `/admin/orders/{id}/simulate-next` | Next status (dev tool) |
| POST | `/admin/generate-description` | AI product description |
| GET | `/admin/analytics/top-searches` | Top search queries |
| GET | `/admin/analytics/top-viewed` | Most viewed products |
| GET | `/admin/analytics/cart-abandonment` | Abandoned cart analysis |

**System** (`routes/system.py`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/system/health` | Health check |

**Locations** (`routes/locations.py`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/locations/provinces` | 63 provinces |
| GET | `/api/locations/districts/{code}` | Districts by province |
| GET | `/api/locations/wards/{code}` | Wards by district |
| GET | `/api/locations/search` | Search locations |

**Navigation** (`routes/navigation.py`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/navigation/category-tree` | Category tree |
| GET | `/api/navigation/mega-menu` | Mega menu structure |
| GET | `/api/navigation/categories` | Flat categories |
| GET | `/api/navigation/brands` | Brands by category |

**Other**:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Chatbot message |
| POST | `/upload-image` | Image upload (admin) |
| POST | `/upload-avatar` | Avatar upload |
| POST | `/payment/momo/create` | Create MoMo payment |
| POST | `/payment/momo/ipn` | MoMo IPN callback |
| GET | `/categories` | Flat categories |
| GET | `/categories/tree` | Category tree |
| POST | `/categories` | Create (admin) |
| DELETE | `/categories/{id}` | Delete (admin) |
| GET | `/search/suggestions` | Search autocomplete |
| GET | `/recommendations` | Personalized recommendations |
| GET | `/cart/recommendations` | Co-purchase recommendations |
| GET | `/addresses` | User's addresses |
| POST | `/addresses` | Create address |
| PUT | `/addresses/{id}` | Update address |
| DELETE | `/addresses/{id}` | Delete address |
| PATCH | `/addresses/{id}/set-default` | Set default address |
| GET | `/wishlist` | Wishlist items |
| GET | `/wishlist/ids` | Wishlist product IDs |
| POST | `/wishlist/{id}` | Add to wishlist |
| DELETE | `/wishlist/{id}` | Remove from wishlist |
| GET | `/spec-templates/{type}` | Spec templates by product type |
| GET | `/products/{id}/variants` | Product variants |
| POST | `/admin/products/{id}/variants` | Create variant |
| PUT | `/admin/variants/{id}` | Update variant |
| DELETE | `/admin/variants/{id}` | Delete variant |
| PUT | `/specifications/{id}` | Update spec (admin) |
| DELETE | `/specifications/{id}` | Delete spec (admin) |
| PUT | `/users/me` | Update profile |

### Chatbot Engine (7 files)

**Flow:**

```
POST /api/chat
  → chat_service.classify_intent() → OpenRouter (classifier model)
  → intent_engine.dispatch(intent, entities)
     → comparison_engine | gaming_engine | search_engine | recommendation_engine
  → openrouter_formatter.format_response(system_prompt, data)
  → OpenRouter (chat model) → markdown response
```

**Intent Classification:** `meta-llama/llama-3.1-8b-instruct` → JSON `{intent, entities}`

- intents: `product_search`, `product_compare`, `gaming_check`, `spec_query`, `faq`, `order_support`, `recommendation`, `chitchat`, `greeting`
- entities: product_type, brand, budget_max/min, use_case, game_name, compare_products, spec_query, order_id

**Engines:**

| Engine | Purpose |
|--------|---------|
| `intent_engine.py` | Routes to correct engine based on classified intent |
| `search_engine.py` | Product search with fuzzy matching + NLP normalization |
| `comparison_engine.py` | Side-by-side spec extraction |
| `gaming_engine.py` | GPU/CPU benchmark comparison vs game requirements |
| `recommendation_engine.py` | ML-like scoring (collaborative + content-based signals) |
| `openrouter_formatter.py` | Prompt building, system prompts per intent, API call |
| `product_utils.py` | Product data helpers |

**ConversationMemory:** OrderedDict-based, max 8 turns, max 500 sessions, LRU eviction.

---

## DATABASE DESIGN

18 tables. All use UUIDv4 string primary keys.

### Entity-Relationship Summary

```
User ──┬── Address (1:N)
       ├── Cart (1:1) ── CartItem (1:N) ── Product
       ├── Order (1:N) ──┬── OrderItem (1:N) ── Product
       │                  ├── OrderStatusHistory (1:N)
       │                  └── Address (N:1)
       ├── Review (1:N) ── Product
       ├── Wishlist (1:N) ── Product
       ├── PasswordResetToken (1:N)
       └── EmailChangeToken (1:N)

Category ──┬── Category (self-referencing, parent_id)
           └── Product (1:N)

Product ──┬── ProductSpecification (1:N) [grouped key-value]
          ├── ProductVariant (1:N) [color/version/price/stock]
          ├── ProductHotspot (1:N)
          ├── RelatedProduct (N:M self via join table)
          ├── SpecTemplate (by product_type)
          ├── GpuBenchmark / CpuBenchmark (reference data)
          └── GameRequirement (reference data)
```

### Key Tables

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `users` | id, email (unique), hashed_password, role, is_admin | Authentication |
| `categories` | id, name, slug (unique), parent_id (FK self), level, path | Hierarchical taxonomy |
| `products` | id, name, price, stock, category_id (FK), brand, sku (unique), product_type, rating, featured, status, embedding (JSON) | Core product entity |
| `product_variants` | id, product_id (FK), color_name, color_code, ram, storage, price, stock, is_default | SKU-level variants |
| `product_specifications` | id, product_id (FK), group_name, spec_key, spec_value, unit, display_order | Dynamic grouped specs |
| `product_hotspots` | id, product_id (FK), label, type, x_percent, y_percent | Image annotation |
| `carts` | id, user_id (FK unique) | One cart per user |
| `cart_items` | id, cart_id (FK), product_id (FK), variant_id (FK nullable), quantity | Cart line items |
| `orders` | id, user_id (FK), total_amount, status, shipping_address, payment_method, tracking_code, shipping_provider | Order entity |
| `order_items` | id, order_id (FK), product_id (FK), variant_id (FK nullable), quantity, price | Order line items |
| `order_status_history` | id, order_id (FK), old_status, new_status, note, changed_by (FK user) | Audit trail |
| `addresses` | id, user_id (FK), full_name, phone, street, province, district, ward, is_default | User addresses |
| `reviews` | id, user_id (FK), product_id (FK), rating (1-5), comment | Product reviews |
| `wishlists` | id, user_id (FK), product_id (FK) | Saved items |
| `search_logs` | id, user_id (FK nullable), query, results_count | Analytics |
| `password_reset_tokens` | id, token (unique), user_id (FK), expires_at, used | Password reset |
| `email_change_tokens` | id, token (unique), user_id (FK), new_email, expires_at, used | Email verification |
| `gpu_benchmarks` | id, name (unique), aliases, score | GPU reference scores |
| `cpu_benchmarks` | id, name (unique), aliases, score | CPU reference scores |
| `game_requirements` | id, game_name (unique), min/recommended/ultra gpu_score, cpu_score, ram_gb | Game hardware reqs |
| `spec_templates` | id, product_type, group_name, spec_key, default_order | Spec presets |
| `related_products` | id, product_id (FK), related_product_id (FK) | Manual relations |

---

## AUTHENTICATION FLOW

```
1. POST /auth/register
   → hash_password (passlib bcrypt PBKDF2-SHA256)
   → create user in DB
   → return JWT + user

2. POST /auth/login (5/min rate limit)
   → verify_password
   → create_access_token(user.id, expires=1440min via JWT HS256)
   → return { access_token, token_type, user }

3. Every subsequent request:
   → Authorization: Bearer <token>
   → oauth2_scheme extracts token
   → decode_access_token → user_id
   → get_current_user → middleware dependency

4. JWT payload: { sub: user_id, exp: timestamp }
   Algorithm: HS256 (configurable)
```

---

## AUTHORIZATION (RBAC)

Two-tier: `role` column in users table.

| Role | Capabilities |
|------|-------------|
| `user` (default) | Browse, cart, checkout, own orders, own profile, reviews, wishlist |
| `admin` | All user + CRUD products, manage orders (status transitions), manage categories, view analytics, generate AI descriptions |

**Enforcement:** `require_admin()` dependency checks `user.is_admin` (derived from `role == "admin"`).

**Order access:** Users see own orders only; admins see all. Enforced via `order.user_id != current_user.id && !current_user.is_admin` in controllers.

---

## ORDER FLOW

```
Cart → POST /orders → create_order()
  │
  ├── Validate stock (product.stock -= quantity)
  ├── Build items from cart or direct payload
  ├── Create Order (status: "pending")
  ├── Create OrderItems
  ├── Clear cart items
  └── Return OrderRead

Status Machine (VALID_STATUS_TRANSITIONS):
  pending → confirmed → processing → shipped → out_for_delivery → delivered → return_requested → returned → refunded
  pending → cancelled / payment_failed

Shipped → auto-generate tracking_code (TK + 9 digits),
          shipping_provider (random from GHN/GHTK/Viettel Post/FedEx),
          estimated_delivery (+2-7 days)
```

---

## PAYMENT FLOW (MoMo)

```
POST /payment/momo/create
  → Build HMAC-SHA256 signature from:
    accessKey, amount, extraData, ipnUrl, orderId, orderInfo,
    partnerCode, redirectUrl, requestId, requestType
  → POST to MoMo test gateway
  → Return { payUrl, resultCode, message }
  → Frontend redirects to payUrl

MoMo → POST /payment/momo/ipn (server-to-server callback)
  → Verify signature
  → resultCode == 0 → order status = "confirmed"
  → else → order status = "payment_failed"

Frontend redirects to /payment/result after MoMo redirect
```

---

## AI / CHATBOT FLOW

```
User message → POST /api/chat

1. classify_intent():
   → OpenRouter (meta-llama/llama-3.1-8b-instruct, 200 tokens, temp=0.1)
   → Returns JSON: { intent, entities }

2. Engine dispatch based on intent:
   - product_search → search_engine.py
   - product_compare → comparison_engine.py
   - gaming_check → gaming_engine.py (vs GPU/CPU benchmarks)
   - spec_query → direct spec lookup
   - recommendation → recommendation_engine.py
   - faq / order_support / chitchat → LLM only

3. format_response():
   → System prompt per intent
     (6 variants: search, recommend, compare, gaming, spec_explain, order_help, unknown)
   → User prompt: <customer_message> + <detected_entities> + <backend_data>
   → OpenRouter (configured model, 1024 max_tokens, temp=0.3)
   → Return markdown

4. Response cached in ConversationMemory
   (8-turn history, LRU 500 sessions)
```

**Backend data serialization:** Compact JSON with capped products (max 5), trimmed spec values (120 chars), removed nulls.

**Gaming evaluation:** Compares product GPU → GPU benchmark score → game requirement thresholds (min/recommended/ultra).

---

## ADMIN WORKFLOW

```
Dashboard:
  ├── Total products, orders, revenue, users
  ├── Monthly/Yearly revenue charts
  ├── Top search queries (today)
  ├── Most viewed products
  └── Cart abandonment analysis

Product Management:
  └── CRUD + image upload + AI description generation
      └── Variants: color/version/ram/storage/price/stock
      └── Specs: grouped key-value with templates
      └── Images: upload with hotspot annotations
      └── Breadcrumbs: SEO paths

Category Management:
  └── Tree: add/delete with parent-child validation
      └── No delete if has children or products

Order Management:
  └── List all orders
      └── Status transition dropdown
      └── Simulate next status (dev tool)
      └── Timeline view
```

---

## BUSINESS RULES

1. **Stock:** Each product has `stock`; decremented on order creation; validated before order.
2. **Reviews:** One review per user per product; update if exists.
3. **Rating:** Computed as average of all review ratings.
4. **Shipping:** 3 tiers: standard (3d/15k), express (1d/35k), same-day (0d/75k) VND.
5. **Address:** One default address per user; setting new default unsets old.
6. **Cart:** One cart per user; item quantity merge on re-add.
7. **Category hierarchy:** `level` column; `path` column for breadcrumbs; prevent delete if has children or products.
8. **Password reset:** Token expires in 1 hour; one-time use.
9. **Email change:** Requires verification via token link.
10. **Search logging:** Logs queries with user_id (if authenticated) + result count for analytics.
11. **Order status transitions:** Strict finite state machine; invalid transitions rejected.
12. **Image uploads:** Max 5MB, allowed formats: jpg, jpeg, png, webp, gif; stored as `static/images/{uuid}.ext`.
13. **Specifications grouped:** Dynamic key-value store grouped by `group_name`, ordered by `display_order`.

---

## SECURITY DESIGN

| Mechanism | Implementation |
|-----------|---------------|
| Password hashing | passlib bcrypt (PBKDF2-SHA256) |
| JWT signing | HS256 with configurable secret |
| Rate limiting | slowapi: 5/min login, 3/min forgot-password |
| CORS | Whitelist: localhost:5173, 127.0.0.1:5173 |
| Input validation | Pydantic schemas (min_length, max_length, regex) |
| Authorization | `require_admin()` decorator + user ownership checks |
| SQL injection | SQLAlchemy ORM (parameterized queries) |
| Token expiration | JWT `exp` claim + DB token `expires_at` + `used` flag |
| File upload | Extension whitelist + content-type check + size limit |

---

## MIDDLEWARES

### Backend (order in main.py)

1. `CORSMiddleware` — FastAPI built-in
2. `SlowAPIMiddleware` — Rate limit enforcement
3. Exception handlers:
   - `RateLimitExceeded` → 429
   - `HTTPException` → 4xx/5xx (custom format `{detail, error_code}`)
   - `SQLAlchemyError` → 500 database error
   - `Exception` → 500 general error

### Frontend

- Axios interceptor: attach JWT `Authorization` header
- 401 response → auto-logout + redirect to login
- `ErrorBoundary` React component catches render errors
- `OfflineBanner` detects connection state via `navigator.onLine` + `online`/`offline` events

---

## EXTERNAL INTEGRATIONS

| Service | Integration | Authentication |
|---------|-------------|---------------|
| OpenRouter (LLM) | OpenAI-compatible REST at `openrouter.ai/api/v1` | API key in `.env` |
| MoMo Payment | REST API (test endpoint) | HMAC-SHA256 signing with partner/access/secret keys |
| SMTP Email | aiosmtplib (Google SMTP) | App password |
| Google Maps (optional) | Places Autocomplete | API key in config |
| Vietnam Location Data | Static JSON (63 provinces, ~700 districts, ~10k wards) | Built-in |

---

## ERROR HANDLING

**API errors:** All routes wrapped in try/except; errors propagated via `HTTPException` with Pydantic-validated detail.

```python
# Custom error format via middleware:
{ "detail": "message", "error_code": 404 }
```

**Error handler middleware:**
- `http_exception_handler` — HTTPExceptions (validation, auth, not found)
- `validation_exception_handler` — Pydantic `RequestValidationError`
- `database_exception_handler` — SQLAlchemy errors → 500 + sanitized message
- `general_exception_handler` — Unhandled → 500 + generic message

**Frontend:**
- Toast notifications for success/error
- `ErrorBoundary` catches React render errors with retry/reload buttons
- `OfflineBanner` shows when connection lost

---

## DEPLOYMENT STRUCTURE

```
project/
├── Backend/
│   ├── .env                  # Environment config (DB, JWT, MoMo, SMTP, OpenRouter)
│   ├── .venv/                # Python virtual environment
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # Entry: uvicorn app.main:app --reload
│       ├── core/             # Config, DB, Security, Email, Rate Limit
│       ├── routes/           # Health, Locations, Navigation
│       ├── middleware/       # Error handlers
│       ├── chatbot/          # AI engine (7 modules)
│       ├── static/           # Uploaded images
│       └── data/             # Vietnam location JSON files
├── Frontend/
│   ├── .env / .env.example
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx          # Entry
│       ├── App.jsx           # Router + layouts
│       ├── components/       # 36 reusable components
│       ├── pages/            # 28 pages (22 user + 6 admin)
│       ├── hooks/            # 9 custom hooks
│       ├── services/         # 11 API service modules
│       ├── store/            # Redux (5 slices)
│       ├── contexts/         # ThemeContext
│       ├── layouts/          # MainLayout, AdminLayout
│       ├── locales/          # i18n (en, vi)
│       └── utils/            # Constants, formatters, validators
└── package.json              # Root workspace config
```

---

## ACTORS

| Actor | Description | Permissions |
|-------|-------------|-------------|
| Guest | Unauthenticated visitor | Browse products, search, view details, register, use chatbot (limited) |
| Customer | Authenticated user | Guest + login, manage profile, cart, checkout (COD/MoMo), orders, reviews, wishlist, full chatbot |
| Admin | Staff with elevated role | Customer + dashboard, product CRUD, category management, order management, analytics, AI description generation |
| OpenRouter AI | External LLM service | Intent classification, chat response generation, product description generation |
| MoMo Gateway | External payment processor | Payment request processing, IPN callback |
| Email Server | SMTP service | Password reset emails, email change verification |

---

## USE CASE CANDIDATES

**Guest:**
- Browse product catalog with filters
- Search products
- View product details and specs
- Compare products side-by-side
- Register a new account
- Use chatbot for product inquiries

**Customer:**
- Login/logout
- Manage profile (avatar, name, email, password)
- Manage shipping addresses (CRUD, set default)
- Manage shopping cart (add, update, remove, clear)
- Checkout with COD or MoMo payment
- View order history and track delivery status
- Write product reviews
- Manage wishlist
- Use chatbot with conversation history

**Admin:**
- View dashboard with sales analytics
- Manage products (create, edit, delete)
- Generate AI product descriptions
- Manage product variants (color, version, price, stock)
- Manage product specifications (grouped key-value)
- Upload product images with hotspot annotations
- Manage product categories (tree CRUD)
- View and manage all orders
- Simulate order status transitions
- View analytics (top searches, top viewed, cart abandonment)

---

## SEQUENCE FLOW CANDIDATES

### Checkout Flow

```
User → POST /orders
  → services.create_order()
    → validate stock
    → decrement stock
    → create Order (status: pending)
    → create OrderItems
    → clear cart
  → if payment_method = "momo":
    → POST /payment/momo/create
    → return { payUrl }
    → User redirected to MoMo
    → MoMo → POST /payment/momo/ipn → update order status
    → MoMo → redirect to /payment/result
  → if payment_method = "cod":
    → return order confirmation
```

### Chatbot Flow

```
User → POST /api/chat { message, session_id, history }
  → chat_service.classify_intent()
    → OpenRouter classify → { intent, entities }
  → fetch_products_for_chat / fetch_benchmark_context
  → build_system_prompt(intent, entities, products, benchmarks)
  → call_openrouter(system_prompt, messages)
    → OpenRouter chat → response text
  → memory_store.add_turn(session_id, user_msg, response)
  → return ChatResponse { intent, message, products, comparison, actions }
```

### Password Reset Flow

```
User → POST /auth/forgot-password { email }
  → services.create_reset_token_and_send_email()
    → generate token (secrets.token_urlsafe(32))
    → store in password_reset_tokens (expires: 1 hour)
    → send email with reset link
  → User clicks link → /reset-password?token=...
  → POST /auth/reset-password { token, new_password }
    → validate token (exists, not used, not expired)
    → update user password
    → mark token as used
```

---

## ACTIVITY FLOW CANDIDATES

### Admin Product Edit

```
1. Navigate to /admin/products/edit/:id
2. Fetch product GET /products/:id
3. Fetch specs GET /products/:id/specifications
4. Populate form (basic, variants, specs, images)
5. User edits tabs (basic/variants/specs/images)
6. Submit:
   a. PUT /products/:id (basic info)
   b. PUT /products/:id/specifications (bulk replace specs)
   c. OPTIONALLY: variant CRUD (individual POST/PUT/DELETE)
7. Navigate back to /admin/products
```

### Product Recommendation

```
1. GET /recommendations?user_id=X&limit=8
2. Fetch user's purchase history (ordered product IDs, categories, brands)
3. Fetch all active products
4. Score each product:
   - Popularity: log(view_count) + order_count*3 + cart_count*1.5 + rating*1
   - Personalization: category match+5, brand match+3, wishlist+2
   - Abandonment: in cart+4
5. Sort by score DESC, return top N
```

---

## COMPONENT DIAGRAM CANDIDATES

```
Backend Components:
├── Web Layer (FastAPI routes)
│   ├── AuthController
│   ├── ProductController
│   ├── CartController
│   ├── OrderController
│   ├── AdminController
│   ├── ChatController
│   └── SystemController (health, locations, navigation)
├── Business Layer
│   ├── AuthService
│   ├── ProductService
│   ├── OrderService
│   ├── PaymentService
│   ├── EmailService
│   ├── RecommendationEngine
│   └── ChatbotEngine
│       ├── IntentClassifier
│       ├── SearchEngine
│       ├── ComparisonEngine
│       ├── GamingEngine
│       └── OpenRouterFormatter
├── Data Layer
│   ├── Repositories (CRUD per entity)
│   ├── SQLAlchemy Models (18 tables)
│   └── Database Session Manager
└── Infrastructure
    ├── Config (pydantic-settings)
    ├── Security (JWT + bcrypt)
    ├── Rate Limiter (slowapi)
    ├── Error Middleware
    └── Email Client (aiosmtplib)

Frontend Components:
├── Pages (28)
├── Layouts (MainLayout, AdminLayout)
├── Components (36 reusable)
│   ├── Product (Card, VariantSelector, SpecsTable, Compare button)
│   ├── Cart (Item, Summary)
│   ├── Checkout (AddressSelector, ShippingSelector, PaymentSelector)
│   ├── Chatbot (Floating button, Panel, Message list)
│   ├── Auth (Login form, Register form, ForgotPassword)
│   ├── Admin (Dashboard, ProductForm, VariantManager, CategoryTree)
│   └── Common (Navbar, Footer, Breadcrumbs, StarRating, ErrorBoundary)
├── Services (11 API modules via Axios)
├── State (Redux: auth, cart, navigation, product slices)
├── Hooks (9 custom hooks)
└── Utils (i18n, constants, formatters, validators)
```

---

## DEPLOYMENT DIAGRAM CANDIDATES

```
                    Internet
                       │
                  ┌────┴────┐
                  │  Nginx  │  (reverse proxy, SSL termination)
                  └────┬────┘
                       │
           ┌───────────┴───────────┐
           │                       │
    ┌──────┴──────┐        ┌──────┴──────┐
    │  Frontend   │        │  Backend    │
    │ (Vite/React)│        │ (FastAPI)   │
    │ :5173 dev   │        │ :8000       │
    │ :80 prod    │        │             │
    └─────────────┘        └──────┬──────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
              ┌──────┴──────┐         ┌────────┴────────┐
              │   MySQL     │         │   SMTP Server   │
              │  Database   │         │  (Gmail SMTP)   │
              └─────────────┘         └─────────────────┘
                     │
              ┌──────┴──────┐
              │  MoMo API   │  (external)
              └─────────────┘
              ┌─────────────┐
              │ OpenRouter  │  (external API)
              └─────────────┘
```

---

## KEY SYSTEM COMPONENTS

1. **Config Module** (`core/config.py`): Singleton `Settings` via pydantic-settings from `.env`. Auto-reloads when `.env` mtime changes. Fields: DB, JWT, MoMo, SMTP, OpenRouter, CORS.

2. **Security Module** (`core/security.py`): JWT `create_access_token(subject)` / `decode_access_token(token)`. Password `hash_password` / `verify_password` using passlib bcrypt.

3. **Database Module** (`core/database.py`): SQLAlchemy `engine` + `SessionLocal` factory + `get_db` dependency generator. Uses PyMySQL driver.

4. **Email Module** (`core/email.py`): Async SMTP via aiosmtplib. Template functions: `build_reset_password_email`, `build_verify_email_change_email`.

5. **Rate Limiter** (`core/rate_limit.py`): slowapi `Limiter` with in-memory storage.

6. **Error Handlers** (`middleware/error_handlers.py`): 4 handler functions returning `JSONResponse` with `{detail, error_code}`.

7. **Seed System** (`seed.py` + `seed_data.py`): Populates categories, products, variants, specs from constants. Guards against re-seeding with `category_id` existence check.

8. **Recommendation Engine** (`services.py`): Scoring algorithm combining popularity (views, orders, cart adds, rating) with personalization (category/brand history, wishlist, cart abandonment). Fallback to popularity-only for anonymous users.

9. **Order Status Machine** (`services.py`): Finite state machine with `VALID_STATUS_TRANSITIONS` dict. Each status has explicit valid next states. Includes auto-generated tracking info on "shipped" transition.
