# Architecture Diagrams — Thesis Defense Explanations

## Slide 1: Layered Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  ROUTE LAYER (routes/)                                           │
│                                                                  │
│  HTTP concerns only:                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ auth.py  │ │products  │ │ orders   │ │ admin    │            │
│  │          │ │.py       │ │ .py      │ │ .py      │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│  Responsibilities:                                               │
│  • Parse HTTP request → extract path params, query strings       │
│  • Delegate to service layer                                     │
│  • Translate exceptions → HTTP status codes                      │
│  • Return serialized response                                    │
│  • NO business logic, NO database queries                        │
├──────────────────────────────────────────────────────────────────┤
│  SERVICE LAYER (services/)                                       │
│                                                                  │
│  Business logic lives here:                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐       │
│  │  auth    │ │  order   │ │  payment │ │recommendation│       │
│  │_service  │ │_service  │ │_service  │ │_service      │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘       │
│  Responsibilities:                                              │
│  • Orchestrate multi-step workflows (order creation)            │
│  • Validate business rules (stock > 0, valid transitions)       │
│  • Manage transactions (commit/rollback)                        │
│  • Coordinate between repositories                               │
│  • NO HTTP concerns, NO route-specific logic                    │
├──────────────────────────────────────────────────────────────────┤
│  REPOSITORY LAYER (repositories.py)                              │
│                                                                  │
│  Data access abstraction:                                        │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  60+ functions: get_user_by_email, create_order,          │    │
│  │  get_products, add_cart_item, ...                        │    │
│  └──────────────────────────────────────────────────────────┘    │
│  Responsibilities:                                              │
│  • Encapsulate SQLAlchemy queries                                │
│  • Single source of truth for each data access pattern           │
│  • No business logic, no transaction boundaries                  │
│  • Return ORM model instances                                    │
├──────────────────────────────────────────────────────────────────┤
│  MODEL LAYER (models.py)                                        │
│                                                                  │
│  Database schema definition:                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│  │ User │ │Product│ │Order │ │ Cart │ │Audit │ │  ... │        │
│  │      │ │      │ │      │ │      │ │ Log  │ │      │        │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘        │
│  Responsibilities:                                              │
│  • Define tables, columns, relationships                        │
│  • Enforce constraints (foreign keys, unique, nullable)         │
│  • Provide ORM navigation (user.orders, product.category)       │
└──────────────────────────────────────────────────────────────────┘
```

### Speaking Notes

> "The architecture has four distinct layers, each with a single responsibility. This separation is not theoretical — it solves concrete problems we encountered during development."
>
> "The **route layer** handles HTTP. When we changed our API from returning camelCase to snake_case, we only modified route files. The service layer didn't change."
>
> "The **service layer** contains all business logic. Order creation requires a seven-step workflow: validate stock, deduct inventory, create order, create line items, log status history, clear cart, and commit. If any step fails, everything rolls back. This orchestration belongs in the service layer, not scattered across routes."
>
> "The **repository layer** might seem like unnecessary indirection until you need to debug a slow query. Every 'get products' call goes through one function. When we added eager loading to fix the N+1 problem, we changed one file."
>
> "The key insight: each layer can be tested independently. Routes → integration tests with HTTP client. Services → unit tests with mocked repositories. Repositories → integration tests with a test database. This layered isolation makes the 0% test coverage we have today fixable — we can add tests layer by layer without rewriting the system."

### Why This Layer Exists

| Layer | If Removed | Consequence |
|---|---|---|
| Route | Merge into services | Services would need to handle HTTP exceptions, response formatting — violates SRP. Testing a service now requires mocking the request object. |
| Service | Merge into routes | Routes become 200+ line monoliths. Two routes needing the same logic (e.g., `set_order_status` for admin and payment callback) would duplicate code. Transactions become error-prone. |
| Repository | Merge into services | `db.query(Product).filter(...)` scattered across 14 files. Schema rename requires hunting through every call site. No central place to add query optimization. |

### Defense Question

**Q:** "Why not use an `AbstractRepository` interface with dependency injection?"

**A:** "That would be textbook clean architecture. For this project, it would add:
- 25+ interface definitions (one per repository concept)
- A DI container wiring with 60+ bindings
- Zero practical benefit (we use one database, one ORM)

The tradeoff: abstracting the repository behind an interface is valuable when you have multiple data sources (PostgreSQL + Redis + Elasticsearch). We have one MySQL database. The concrete `repositories.py` file is the right abstraction level for this project — it decouples query logic from business logic without introducing the ceremony of interfaces."

---

## Slide 2: Sequence Diagram — Order Creation

```
Client               Route               Service              Repository            MySQL
  │                    │                    │                     │                    │
  │  POST /orders      │                    │                     │                    │
  │  {items, address,  │                    │                     │                    │
  │   payment_method}  │                    │                     │                    │
  │───────────────────►│                    │                     │                    │
  │                    │  validate payload  │                     │                    │
  │                    │  (Pydantic schema) │                     │                    │
  │                    │                    │                     │                    │
  │                    │  require_admin()   │                     │                    │
  │                    │  (or get_current)  │                     │                    │
  │                    │                    │                     │                    │
  │                    │ create_order(...)  │                     │                    │
  │                    │───────────────────►│                     │                    │
  │                    │                    │                     │                    │
  │                    │                    │ BEGIN TRANSACTION   │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │                    │
  │                    │                    │  FOR EACH item:     │                    │
  │                    │                    │  validate_stock()   │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │  SELECT quantity    │
  │                    │                    │                     │  FROM products      │
  │                    │                    │                     │  WHERE id = ?      │
  │                    │                    │                     │  FOR UPDATE         │
  │                    │                    │                     │◄───────────────────│
  │                    │                    │                     │  row locked         │
  │                    │                    │                     │                    │
  │                    │                    │  deduct_stock()     │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │  UPDATE products    │
  │                    │                    │                     │  SET stock = ?      │
  │                    │                    │                     │  WHERE id = ?       │
  │                    │                    │                     │◄───────────────────│
  │                    │                    │                     │                    │
  │                    │                    │  create_order()     │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │  INSERT INTO        │
  │                    │                    │                     │  orders (...)       │
  │                    │                    │                     │◄───────────────────│
  │                    │                    │                     │                    │
  │                    │                    │  FOR EACH item:     │                    │
  │                    │                    │  create_item()      │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │  INSERT INTO        │
  │                    │                    │                     │  order_items (...)  │
  │                    │                    │                     │◄───────────────────│
  │                    │                    │                     │                    │
  │                    │                    │  log_status()       │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │  INSERT INTO        │
  │                    │                    │                     │  order_status_     │
  │                    │                    │                     │  history (...)     │
  │                    │                    │                     │◄───────────────────│
  │                    │                    │                     │                    │
  │                    │                    │ COMMIT              │                    │
  │                    │                    │─────────────────────│───────────────────►│
  │                    │                    │                     │                    │
  │                    │     return order   │                     │                    │
  │                    │◄───────────────────│                     │                    │
  │                    │                    │                     │                    │
  │  ← 201 Created    │                    │                     │                    │
  │  {order}          │                    │                     │                    │
  │◄──────────────────│                    │                     │                    │
```

### Speaking Notes

> "This sequence diagram shows the concrete flow of our most complex write operation: order creation."
>
> "Two critical design decisions are visible here."
>
> "First, **SELECT ... FOR UPDATE**. When we validate stock, we acquire a row-level lock on the product row. This means if two users buy the last item simultaneously, the second `SELECT ... FOR UPDATE` blocks until the first transaction completes. The first user sees stock = 1 → deducts → commits. The second user sees stock = 0 → raises 'Insufficient stock' → rolls back. No overselling."
>
> "Second, **the service controls the transaction boundary**. The service calls `BEGIN TRANSACTION`, orchestrates all six repository calls, then `COMMIT` or `ROLLBACK`. Repositories never commit. This is the difference between the repository pattern and raw SQLAlchemy — transactions belong to the business workflow, not the data access layer."
>
> "Notice that the route is completely unaware of this complexity. It receives a validated Pydantic payload, calls one service function, and returns the result. The route could be replaced with a GraphQL resolver or a CLI command without changing the service."

### Key Architecture Insights

1. **Row-level locking** (`FOR UPDATE`) prevents overselling without pessimistic table locks
2. **Single service function** orchestrates six repository calls — the route sees one abstraction
3. **Transactional atomicity** — any failure before COMMIT rolls back all changes
4. **Repository isolation** — each repository function does exactly one thing (validate stock, create order, insert item)

---

## Slide 3: Chatbot Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  USER MESSAGE: "Tìm laptop Dell dưới 20 triệu"                                      │
└──────────────────────────┬──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: INTENT ENGINE (intent_engine.py)                                          │
│                                                                                    │
│  ┌────────────────────────────────────────────┐                                    │
│  │  Rule-Based Classifier (Primary Path)       │                                    │
│  │                                            │                                    │
│  │  Input: "Tìm laptop Dell dưới 20 triệu"    │  ┌──────────────────────┐          │
│  │                                            │  │  LLM Classifier      │          │
│  │  Keywords found:                           │  │  (Fallback)          │          │
│  │  ├── "tìm"         → search intent         │  │                      │          │
│  │  ├── "laptop"      → product_type=laptop    │  │  Triggered when:     │          │
│  │  ├── "Dell"        → brand=DELL            │  │  • No keywords match │          │
│  │  └── "dưới 20"     → max_price=20,000,000  │  │  • Confidence < 0.8  │          │
│  │                                            │  │  • Complex query     │          │
│  │  Confidence: 0.95 > 0.8 → RULE-BASED PATH  │  └──────────────────────┘          │
│  └────────────────────────────────────────────┘                                    │
│                                                                                    │
│  Output: IntentResult(intent="product_search", entities={...})                     │
└──────────────────────────────────┬────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ENGINE DISPATCHER (engine_dispatcher.py)                                  │
│                                                                                    │
│  Intent → Engine Map:                                                              │
│  ┌─────────────────────┬─────────────────────────────┐                             │
│  │ Intent              │ Engine                      │                             │
│  ├─────────────────────┼─────────────────────────────┤                             │
│  │ product_search      │ SearchEngine                │                             │
│  │ search_product      │ SearchEngine                │                             │
│  │ recommendation      │ RecommendationEngine        │                             │
│  │ gaming_check        │ GamingEngine                │                             │
│  │ compare_products    │ ComparisonEngine            │                             │
│  │ faq / chitchat      │ (No engine → LLM formatter) │                             │
│  └─────────────────────┴─────────────────────────────┘                             │
│                                                                                    │
│  "product_search" → SearchEngine.handle()                                          │
└──────────────────────────────────┬────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: SEARCH ENGINE (search_engine.py)                                          │
│                                                                                    │
│  Builds SQL query from entities:                                                   │
│                                                                                    │
│  SELECT p.id, p.name, p.price, p.brand, p.image_url                               │
│  FROM products p                                                                   │
│  WHERE p.product_type = 'laptop'                                                   │
│    AND p.brand = 'Dell'                                                            │
│    AND p.price <= 20000000                                                         │
│    AND p.status = 'active'                                                         │
│  ORDER BY p.created_at DESC                                                        │
│  LIMIT 5                                                                           │
│                                                                                    │
│  Result: [ProductCard, ProductCard, ...]                                           │
└──────────────────────────────────┬────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: RESPONSE FORMATTER (openrouter_formatter.py)                              │
│                                                                                    │
│  Converts structured data → natural language:                                      │
│                                                                                    │
│  LLM Prompt:                                                                       │
│  """                                                                               │
│  You are a Vietnamese e-commerce assistant.                                        │
│  Format these products into a helpful response.                                    │
│  DO NOT add information not in the provided data.                                  │
│                                                                                    │
│  Products: [5 ProductCard objects from DB]                                         │
│  """                                                                               │
│                                                                                    │
│  LLM Response:                                                                     │
│  {                                                                                 │
│    "message": "Mình tìm thấy 5 laptop Dell dưới 20 triệu cho bạn:...",            │
│    "products": [...],                                                              │
│    "actions": [{"label": "Xem thêm", "url": "/search?..."}]                        │
│  }                                                                                 │
└──────────────────────────────────┬────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  RESPONSE TO USER: structured JSON with message + products + actions                │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaking Notes

> "This is the most architecturally interesting subsystem. Let me walk through each step."
>
> "**Step 1: Intent Engine.** We use a two-tier classifier. The rule-based path matches keywords against a curated dictionary — 'tìm' signals search, 'laptop' is a product type, 'Dell' is a brand. This runs in under 10 milliseconds with zero cost. Only when the rule-based classifier's confidence is below 0.8 do we fall back to the LLM API. In practice, 80% of queries are handled by rules."
>
> "**Step 2: Engine Dispatcher.** Once we know the intent, the dispatcher routes to a specialized engine. Each engine is a Python class with a `handle(ctx)` method. Adding a new feature means: write a new engine class, add one line to the dispatcher map. No other code changes."
>
> "**Step 3: Specialized Engine.** The search engine builds a SQL query from extracted entities. It does NOT call the LLM. The gaming engine looks up GPU/CPU benchmark data. The comparison engine does a side-by-side spec diff. Each engine produces structured data, not natural language."
>
> "**Step 4: Response Formatter.** Only here does the LLM touch the response. The LLM receives the structured product data and formats it into natural language Vietnamese. The prompt explicitly forbids adding information not in the provided data. The output is validated against a JSON schema before reaching the user."
>
> "The key insight: **the LLM never generates data. It only formats data.** This is our hallucination prevention strategy. If the LLM says 'this laptop has 32GB RAM,' that value came from a database query, not the LLM's training data."

### Why This Architecture (Not End-to-End LLM)

| Concern | Pure LLM | Hybrid Pipeline |
|---|---|---|
| Response time | 3-5 seconds | ~200 ms (80% of queries) |
| Cost per query | ~$0.002 | ~$0.0004 (20% hit LLM) |
| Hallucination risk | High (invents prices, stock) | Zero (data from database) |
| Database integration | Cannot query without tools | Native SQL access |
| Offline capability | Zero (API must be up) | 80% works without LLM |

### Defense Question

**Q:** "What happens when the LLM API is unavailable?"

**A:** "The system degrades gracefully. The `openrouter_formatter.enabled` flag returns False when the API is unreachable or the API key is missing. When disabled:
- Step 4 skips the LLM entirely
- The chatbot returns structured data directly (product cards, comparison tables) using a template
- The user sees formatted product information without the conversational wrapper
- The admin AI description generator returns a 503 'AI service not configured'

Approximately 80% of the pipeline's value comes from steps 1-3 (finding the right products). Step 4 (natural language formatting) is a UX enhancement, not a core requirement."

---

## Slide 4: Authentication Flow (Registration)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │  Route   │     │ Service  │     │   Repo   │     │  MySQL   │
│  (React) │     │(auth.py) │     │(auth_    │     │(repo-    │     │          │
│          │     │          │     │service)  │     │sitories) │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │  POST /auth/register            │                │                │
     │  {email, password, full_name}   │                │                │
     │────────────────►               │                │                │
     │                 │               │                │                │
     │            Validate payload     │                │                │
     │            (Pydantic schema)    │                │                │
     │                 │               │                │                │
     │            register_user(...)   │                │                │
     │                 │──────────────►│                │                │
     │                 │               │                │                │
     │                 │          Check email           │                │
     │                 │          uniqueness            │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  SELECT * FROM │
     │                 │               │                │  users WHERE   │
     │                 │               │                │  email = ?     │
     │                 │               │                │───────────────►│
     │                 │               │                │◄───────────────│
     │                 │               │                │  None (no dup) │
     │                 │               │                │                │
     │                 │          Hash password         │                │
     │                 │          (passlib/bcrypt)       │                │
     │                 │               │                │                │
     │                 │          Create user           │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  INSERT INTO   │
     │                 │               │                │  users (...)   │
     │                 │               │                │───────────────►│
     │                 │               │                │◄───────────────│
     │                 │               │                │  User object   │
     │                 │               │◄───────────────│                │
     │                 │               │                │                │
     │                 │          Create access token   │                │
     │                 │          (JWT, 15min expiry)   │                │
     │                 │               │                │                │
     │                 │          Create refresh token  │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  INSERT INTO   │
     │                 │               │                │  refresh_tokens│
     │                 │               │                │───────────────►│
     │                 │               │◄───────────────│                │
     │                 │               │                │                │
     │                 │     {user, tokens}             │                │
     │                 │◄──────────────│                │                │
     │                 │               │                │                │
     │  ← 201 Created │               │                │                │
     │  {             │               │                │                │
     │    user: {...},│               │                │                │
     │    access_token,│               │                │                │
     │    refresh_token               │                │                │
     │  }             │               │                │                │
     │◄────────────────│               │                │                │
     │                 │               │                │                │
     │  Store tokens in               │                │                │
     │  localStorage                  │                │                │
     │  (shop_token,                   │                │                │
     │   shop_refresh_token)           │                │                │
     │                 │               │                │                │
```

### Speaking Notes

> "This diagram shows the registration flow, which establishes the security foundation for all subsequent requests."
>
> "**Step 1: Route validation.** The route uses Pydantic to validate the payload before any business logic runs. This means malformed requests (missing fields, invalid email format, password too short) are rejected at the HTTP layer without touching the database."
>
> "**Step 2: Service orchestration.** The service layer coordinates everything: email uniqueness check, password hashing, user creation, token generation. The route sees one function call. The repository sees four independent operations."
>
> "**Step 3: Two-token model.** We issue two tokens. The access token is a short-lived (15 minute) JWT that authorizes API requests. The refresh token is a long-lived (7 day) opaque token stored in the database. This hybrid approach gives us the statelessness of JWTs (fast verification, no database lookup on each request) with the revocability of server-side sessions (admin can force logout, password change invalidates all tokens)."
>
> "**Step 4: Token storage.** The client stores both tokens in localStorage. The access token is sent in the `Authorization: Bearer` header. The refresh token is sent to `/auth/refresh` when the access token expires. Tokens are never stored in cookies, avoiding CSRF vulnerabilities."

### Why Password Hashing?

> "Passwords are hashed using `passlib` with the `pbkdf2_sha256` algorithm. We never store plaintext passwords. If the database is compromised, attackers get hashes, not passwords. The hashing is done in the service layer, not the route or the repository, because it's a business concern — how we transform credentials before storage is a policy decision, not a data access concern."

---

## Slide 5: Token Refresh Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │  Axios   │     │  Route   │     │   Repo   │     │  MySQL   │
│          │     │ Intercep.│     │(auth.py) │     │(repo-    │     │          │
│          │     │          │     │          │     │sitories) │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │  API request (expired token)    │                │                │
     │────────────────►               │                │                │
     │                 │               │                │                │
     │  ← 401 Unauthorized             │                │                │
     │◄────────────────│               │                │                │
     │                 │               │                │                │
     │  Interceptor detects 401        │                │                │
     │  Checks: refresh token exists   │                │                │
     │  Checks: not already refreshing │                │                │
     │  Sets: isRefreshing = true      │                │                │
     │                 │               │                │                │
     │  POST /auth/refresh             │                │                │
     │  {refresh_token}                │                │                │
     │────────────────────────────────►│                │                │
     │                 │               │                │                │
     │                 │          Hash token             │                │
     │                 │          (SHA-256)              │                │
     │                 │               │                │                │
     │                 │          Lookup token           │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  SELECT * FROM │
     │                 │               │                │  refresh_tokens│
     │                 │               │                │  WHERE         │
     │                 │               │                │  token_hash = ?│
     │                 │               │                │───────────────►│
     │                 │               │                │◄───────────────│
     │                 │               │                │  Token row     │
     │                 │               │                │                │
     │                 │          Validate:              │                │
     │                 │          • not revoked          │                │
     │                 │          • not expired          │                │
     │                 │          • belongs to device    │                │
     │                 │               │                │                │
     │                 │          REVOKE old token       │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  UPDATE         │
     │                 │               │                │  refresh_tokens │
     │                 │               │                │  SET revoked=1  │
     │                 │               │                │  WHERE id = ?   │
     │                 │               │                │───────────────►│
     │                 │               │                │                │
     │                 │          CREATE new pair        │                │
     │                 │          (access + refresh)     │                │
     │                 │               │                │                │
     │                 │          Store new refresh      │                │
     │                 │               │───────────────►│                │
     │                 │               │                │  INSERT INTO   │
     │                 │               │                │  refresh_tokens│
     │                 │               │                │───────────────►│
     │                 │               │                │                │
     │                 │  ← {new tokens}                │                │
     │                 │◄──────────────│                │                │
     │                 │               │                │                │
     │  Interceptor stores tokens      │                │                │
     │  Retries original request       │                │                │
     │  with new access token          │                │                │
     │                 │               │                │                │
     │  Original API request (retry)   │                │                │
     │────────────────►   (success)    │                │                │
```

### Speaking Notes

> "Token refresh is implemented in the Axios interceptor, not in application code. This is an architectural decision: every API call gets automatic token refresh without any route or component needing to handle 401 errors."
>
> "**The critical security mechanism is rotation.** When we receive a refresh token, we don't just validate it — we revoke it and issue a completely new pair. This means a stolen refresh token can only be used once. If an attacker uses it before the legitimate client, the client's next request will fail because the old token is already revoked."
>
> "**Concurrent request handling.** Multiple API calls may fail simultaneously due to expiry. The interceptor uses a queue pattern: the first failed request triggers refresh, all other failed requests wait in a queue. When refresh completes, the queue is resolved with the new token. Without this, we would send N simultaneous refresh requests, causing race conditions."
>
> "**Why hash refresh tokens?** We store `SHA-256(token_hash)` in the database, not the raw token. If the database is compromised, attackers get hashes. They cannot turn a hash into a valid token because hashing is one-way. The raw token exists only on the client and in the request body during refresh."

### Security Boundaries

| What | Stored Where | Leak Impact |
|---|---|---|
| Access Token (15 min) | Client localStorage | Limited window, revoked on rotation |
| Refresh Token (7 days) | Client localStorage + DB (SHA-256 hash) | DB leak: useless. Client leak: mitigated by rotation |
| Password | DB (pbkdf2_sha256 hash) | No plaintext exposure |
| MFA Secret | DB (encrypted) | Requires second factor |
| Audit Log | DB | Read-only, no credentials stored |

---

## Slide 6: Order Status Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORDER STATUS STATE MACHINE                            │
│                                                                         │
│                         ┌──────────┐                                     │
│                         │ pending  │                                     │
│                         └────┬─────┘                                     │
│                              │                                           │
│                              │ payment confirmed                         │
│                              ▼                                           │
│                         ┌──────────┐                                     │
│                    ┌───►│confirmed │◄──── admin override                 │
│                    │    └────┬─────┘                                     │
│                    │         │                                           │
│                    │         │ processing started                        │
│                    │         ▼                                           │
│                    │    ┌──────────┐                                     │
│                    │    │processing│                                     │
│                    │    └────┬─────┘                                     │
│                    │         │                                           │
│                    │         │ shipped                                   │
│                    │         ▼                                           │
│                    │    ┌──────────┐                                     │
│                    │    │ shipped  │──┐                                  │
│                    │    └────┬─────┘  │                                  │
│                    │         │        │                                  │
│                    │         │ delivered                                 │
│                    │         ▼        │                                  │
│                    │    ┌──────────┐  │                                  │
│                    │    │delivered │  │                                  │
│                    │    └──────────┘  │                                  │
│                    │                  │                                  │
│                    │    ┌──────────┐  │                                  │
│                    └────│cancelled │◄─┘  (at any 'active' state)         │
│                         └──────────┘                                     │
│                                                                         │
│    VALID_TRANSITIONS = {                                                │
│        "pending":    ["confirmed", "cancelled"],                        │
│        "confirmed":  ["processing", "cancelled"],                       │
│        "processing": ["shipped", "cancelled"],                          │
│        "shipped":    ["delivered", "cancelled"],                        │
│        "delivered":  [],                                                │
│        "cancelled":  [],                                                │
│    }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ set_order_status│     │ update_order_    │     │  simulate_next_ │
│ (simple update) │     │ status_with_     │     │  order_status   │
│                 │     │ history          │     │  (dev tool)     │
│ DEPRECATED      │     │                  │     │                 │
│ No audit trail  │     │ Validates trans. │     │ Finds next valid│
│ No transition   │     │ Creates history  │     │ transition from │
│ validation      │     │ Logs audit entry │     │ state machine   │
│                 │     │ Updates tracking │     │ Calls update_   │
│                 │     │                  │     │ with_history    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Speaking Notes

> "The order status workflow is implemented as a **state machine**, not a free-form status field. This is a deliberate architectural choice to prevent invalid transitions."
>
> "The `VALID_STATUS_TRANSITIONS` dictionary defines exactly which transitions are allowed. You cannot go from 'processing' back to 'confirmed'. You cannot go from 'delivered' to 'shipped'. The state machine enforces this."
>
> "We have two functions. `update_order_status_with_history` is the production path — it validates transitions, creates a status history record, updates the tracking code, and logs to the audit table. `simulate_next_order_status` is a developer tool that queries the state machine for the next valid transitions and applies them automatically — useful during testing."
>
> "The deprecated `update_order_status` function exists without transition validation or history. It was the original implementation. Routes still import it, but all callers use the `with_history` version. This is dead code that should be removed."
>
> "The `OrderStatusHistory` model records old_status, new_status, changed_by, and a note. This gives us a complete audit trail of every status change, viewable on the order timeline endpoint."

### Why State Machine Over Free-Form Status

| Approach | Flexibility | Correctness | Debugging |
|---|---|---|---|
| Free-form string | Maximum | Zero (any transition possible) | Requires manual log analysis |
| State machine | Constrained | Enforced at code level | Invalid transition → clear error |

---

## Slide 7: Deployment Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION DEPLOYMENT                           │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        DNS / CDN (Cloudflare)                       │  │
│  │   domain.com → load balancer                                       │  │
│  │   static.domain.com → CDN edge cache for images                    │  │
│  └────────────────────────────────┬────────────────────────────────────┘  │
│                                   │                                       │
│                                   ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    LOAD BALANCER (Nginx / Caddy)                    │  │
│  │                                                                     │  │
│  │  /api/* → FastAPI backend (port 8000)                              │  │
│  │  /*     → React SPA (port 3000)                                    │  │
│  │                                                                     │  │
│  │  SSL termination at this layer                                     │  │
│  └────────────────────────────────┬────────────────────────────────────┘  │
│                                   │                                       │
│                    ┌──────────────┴──────────────┐                       │
│                    │                              │                       │
│                    ▼                              ▼                       │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐     │
│  │     React SPA (Vite build)   │  │   FastAPI Server (Uvicorn)   │     │
│  │                              │  │                              │     │
│  │  Static files served by      │  │  Stateless — any number of   │     │
│  │  load balancer or CDN        │  │  instances can run behind    │     │
│  │                              │  │  the load balancer           │     │
│  │  .env: VITE_API_URL          │  │                              │     │
│  └──────────────────────────────┘  │  App instance:               │     │
│                                    │  ├── 8 workers (CPU bound)   │     │
│                                    │  ├── 10 DB pool size         │     │
│                                    │  └── 30s request timeout     │     │
│  ┌──────────────────────────────┐  └──────────────┬───────────────┘     │
│  │   Static Files (uploads/)    │                 │                      │
│  │                              │                 │                      │
│  │  Product images              │                 │                      │
│  │  User avatars                │                 ▼                      │
│  │  Uploaded via /upload-image  │  ┌──────────────────────────────┐     │
│  └──────────────────────────────┘  │       MySQL Database         │     │
│                                    │                              │     │
│  ┌──────────────────────────────┐  │  shopping_web (primary)      │     │
│  │   External Services          │  │  ├── 25+ tables              │     │
│  │                              │  │  ├── InnoDB engine           │     │
│  │  MoMo Payment API            │  │  ├── UTF-8 charset           │     │
│  │  OpenRouter LLM API          │  │  └── Connection: pymysql     │     │
│  │  SMTP Email Server           │  │                              │     │
│  │  Google Maps Geocoding       │  │  Scale path:                 │     │
│  └──────────────────────────────┘  │  1. Larger instance          │     │
│                                    │  2. Read replicas            │     │
│  ┌──────────────────────────────┐  │  3. Redis cache              │     │
│  │   Local Development          │  └──────────────────────────────┘     │
│  │                              │                                       │
│  │  Vite dev server :5173       │                                       │
│  │  Uvicorn reload :8000        │                                       │
│  │  MySQL :3306 (local/WSL)     │                                       │
│  └──────────────────────────────┘                                       │
└───────────────────────────────────────────────────────────────────────────┘
```

### Speaking Notes

> "The deployment architecture is straightforward because the monolith allows it to be. One backend server, one database, one frontend build."
>
> "**The backend is stateless.** All session data lives in refresh tokens stored in the database. This means we can horizontally scale the FastAPI instances behind a load balancer without sticky sessions or distributed session stores. Each instance is identical."
>
> "**The frontend is a static SPA.** The Vite build produces HTML, CSS, and JS files served by the load balancer. No Node.js server is needed in production. `VITE_API_URL` points to the backend domain."
>
> "**Static uploads** — product images, user avatars — are stored on the server filesystem. This is the one stateful element. In a production scale-up, these would move to S3-compatible object storage (MinIO, Cloudflare R2) with CDN distribution."
>
> "**External services** — MoMo payment, OpenRouter AI, SMTP email — are integrated via API calls. They have no direct database access. The worst case of an external service failure is a 503 response to the user, not data corruption."
>
> "**Database** — The single MySQL instance is the scaling bottleneck. The connection pool is configured for 10 concurrent connections, which is appropriate for a server with 8 workers. Beyond that, the database would need a larger instance, read replicas, or a caching layer."

### Local Development vs Production

| Resource | Development | Production |
|---|---|---|
| Backend | `uvicorn app.main:app --reload` | `uvicorn app.main:app --workers 8` |
| Database | Local MySQL | Cloud SQL / managed MySQL |
| Frontend | `vite` dev server (HMR) | `vite build` → static files |
| API URL | `http://localhost:8000` | `https://api.domain.com` |
| Environment | `.env` file | System environment variables |

---

## Slide 8: Entity-Relationship Diagram

```
┌───────────────────────────────┐
│           USER                │
│───────────────────────────────│
│ id (PK, UUID)                │──────┐
│ email (UNIQUE)               │      │
│ hashed_password              │      │
│ full_name                    │      │
│ is_admin / role              │      │
│ mfa_secret / mfa_enabled     │      │
│ failed_login_attempts        │      │
│ locked_until                 │      │
│ last_login_at / ip           │      │
│ created_at                   │      │
└───────┬───────┬───────┬──────┘      │
        │       │       │             │
        │       │       │             │
        ▼       ▼       ▼             │
┌──────────┐ ┌──────┐ ┌────────┐     │
│  ORDER   │ │ CART │ │REVIEW  │     │
│──────────│ │──────│ │────────│     │
│ id (PK)  │ │id(PK)│ │ id(PK) │     │
│ user_id  │◄┘userid│ │ user_id│─────┘
│ total    │ │      │ │ prod_id│
│ status   │ │items │ │ rating │
│ shipping │ │  │   │ │ comment│
│ payment  │ │  │   │ └────────┘
│ tracking │ │  │   │
│ created  │ │  │   │
└─────┬────┘ │  │   │
      │      │  │   │
      ▼      │  │   │
┌──────────┐ │  │   │  ┌─────────────────┐
│ORDER_ITEM│ │  │   │  │  WISHLIST       │
│──────────│ │  │   │  │─────────────────│
│ id (PK)  │ │  │   │  │ id (PK)          │
│ order_id │ │  │   │  │ user_id ────────┘
│ prod_id  │ │  │   │  │ product_id
│ var_id   │ │  │   │  │ created_at
│ quantity │ │  │   │  └─────────────────┘
│ price    │ │  │   │
└────┬─────┘ │  │   │
     │       │  │   │
     │  ┌────┘  │   │    ┌──────────────────────┐
     │  │ ┌─────┘   │    │   AUDIT_LOG          │
     ▼  ▼ ▼         │    │──────────────────────│
┌─────────────────┐  │    │ id (PK)              │
│    PRODUCT      │  │    │ user_id ─────────────┘
│─────────────────│  │    │ action
│ id (PK, UUID)   │  │    │ resource_type
│ name            │  │    │ resource_id
│ description     │  │    │ details (JSON)
│ price / stock   │  │    │ ip_address
│ category_id ────┼──┼──┐ │ created_at
│ brand           │  │  │ └──────────────────────┘
│ sku (UNIQUE)    │  │  │
│ product_type    │  │  │ ┌──────────────────────┐
│ rating          │  │  │ │   REFRESH_TOKEN      │
│ featured/status │  │  │ │──────────────────────│
│ view_count      │  │  │ │ id (PK)              │
│ embedding (JSON)│  │  │ │ user_id ─────────────┘
│ created_at      │  │  │ │ token_hash
└───┬───┬───┬───┬─┘  │  │ │ device_info / ip
    │   │   │   │    │  │ │ expires_at
    │   │   │   │    │  │ │ revoked
    │   │   │   │    │  │ │ created_at
    │   │   │   │    │  │ └──────────────────────┘
    │   │   │   │    │  │
    ▼   ▼   ▼   ▼    │  │  ┌──────────────────────┐
┌────┐ ┌───┐ ┌───┐ ┌──┴──┼──┤   ADDRESS           │
│VAR │ │SPEC│ │IMG │ │CAT  │  │─────────────────────│
│IANT│ │    │ │    │ │EGORY│  │ id (PK)              │
│────│ │────│ │────│ │─────│  │ user_id ────────────┘
│id  │ │id  │ │id  │ │id   │  │ full_name / phone
│prod│ │prod│ │prod│ │name │  │ street / province
│sku │ │gpnm│ │url │ │slug │  │ district / ward
│clr │ │key │ │prim│ │desc │  │ country / is_default
│ram │ │val │ │sort│ │lvl  │  └──────────────────────┘
│str │ │unit│ │ordr│ │parid│
│prce│ │ordr│ │    │ └─────┘
│stck│ │    │ └────┘
└────┘ └───┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ GPU_BENCHMARK   │  │ CPU_BENCHMARK   │  │GAME_REQUIREMENT │
│─────────────────│  │─────────────────│  │─────────────────│
│ id (PK)          │  │ id (PK)          │  │ id (PK)          │
│ name (UNIQUE)    │  │ name (UNIQUE)    │  │ game (UNIQUE)    │
│ aliases          │  │ aliases          │  │ min_gpu_score    │
│ score            │  │ score            │  │ min_cpu_score    │
│ created_at       │  │ created_at       │  │ min_ram          │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Speaking Notes

> "The database has 21 tables organized around four domain clusters."
>
> "**User cluster** — `users` is the central entity, with relationships to orders, cart, reviews, wishlist, addresses, refresh tokens, and audit logs. Every security-critical operation is traceable to a user ID."
>
> "**Product cluster** — The product entity has four child tables: `product_variants` (SKU-level pricing), `product_specifications` (key-value attributes grouped by category), `product_images` (multiple images with sort order), and `related_products` (self-referential many-to-many). This normalized structure supports the complex product pages with variants, specs tabs, and image galleries."
>
> "**Order cluster** — Order has child `order_items` (line items with frozen price), `order_status_history` (audit trail of status changes), and a relationship to `address` (shipping address snapshotted at checkout time)."
>
> "**Chatbot cluster** — `gpu_benchmarks`, `cpu_benchmarks`, and `game_requirements` are reference data tables seeded for the gaming performance check engine. These are read-only in production, populated by the seed script."
>
> "**Key design decision: JSON fields.** `products.embedding` stores a vector embedding for future ML-based similarity search. `audit_logs.details` stores arbitrary structured data per action. These JSON columns give us schema flexibility without join tables for features that are still experimental."

### Relationship Cardinality Summary

| Relationship | Type | Business Meaning |
|---|---|---|
| User → Address | 1:N | Users can have multiple shipping addresses |
| User → Order | 1:N | Users can place many orders |
| User → Cart | 1:1 | One active cart per user |
| Product → Variant | 1:N | One product, many SKUs |
| Product → Specification | 1:N | Grouped key-value attributes |
| Product → Image | 1:N | Multiple display images |
| Order → Item | 1:N | Each order has line items |
| Category → Product | 1:N | Products belong to categories |
| Category → Category | Self-ref | Hierarchical category tree via parent_id |

---

## Summary Table: All Diagrams

| Diagram | Key Insight | Defense Talking Point |
|---|---|---|
| Layered Architecture | Each layer is independently testable | "Routes don't query the database. Services don't parse HTTP requests." |
| Sequence (Order) | `SELECT ... FOR UPDATE` prevents overselling | "Two users buying the last item — one succeeds, one gets 'Insufficient stock'." |
| Chatbot Pipeline | LLM formats, doesn't generate data | "The LLM never creates data. It only formats database results." |
| Auth Flow | Two-token model (JWT + refresh) | "Stateless verification + server-side revocability." |
| Token Refresh | Rotation invalidates previous token | "A stolen token works once. Then the user gets alerted." |
| Order Workflow | State machine prevents invalid transitions | "You cannot ship a cancelled order." |
| Deployment | Stateless backend, scale horizontally | "No sticky sessions. No distributed state. Just add instances." |
| ERD | 21 tables, 4 domain clusters | "Normalized for integrity, JSON fields for flexibility." |
