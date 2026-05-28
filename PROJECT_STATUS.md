# Tình Trạng Dự Án — Project Status

> File này ghi lại trạng thái thực tế của toàn bộ codebase,
> phân loại từng module theo mức độ hoàn thiện.

---

## Phân Loại

| Nhãn | Ý Nghĩa | Màu |
|---|---|---|
| ✅ **Đã hoàn thiện** | Chạy được, đủ logic, sẵn sàng demo | Xanh |
| ⚠️ **Đang dở** | Có logic nhưng còn thiếu hoặc chưa ổn định | Vàng |
| 🧟 **Dead code** | Không được dùng đến, có thể xoá an toàn | Đỏ |
| 🎪 **Demo được** | Chạy được demo nhưng chưa đủ cho production | Tím |
| 🏗️ **Architecture intention** | Được thiết kế/hiện thực nhưng chưa bao giờ dùng | Xám |

---

## 1. Authentication & Authorization

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Đăng ký / Đăng nhập | ✅ Đã hoàn thiện | Email + password, hashing bcrypt |
| JWT access token (15 phút) | ✅ Đã hoàn thiện | python-jose, RS256 |
| Refresh token (7 ngày) | ✅ Đã hoàn thiện | Lưu hash trong DB, có rotation |
| Token refresh flow (Axios interceptor) | ✅ Đã hoàn thiện | Queue pattern tránh race condition |
| Đăng xuất (revoke token) | ✅ Đã hoàn thiện | Revoke refresh token trong DB |
| Logout all sessions | ✅ Đã hoàn thiện | `revoke_all_user_refresh_tokens` |
| Multi-factor authentication (TOTP) | ✅ Đã hoàn thiện | `pyotp`, setup/verify/disable flow |
| MFA challenge flow | ✅ Đã hoàn thiện | JWT challenge token + TOTP code |
| Forgot password | ✅ Đã hoàn thiện | Gửi email, reset token 1 giờ |
| Change email | ✅ Đã hoàn thiện | Xác nhận qua email |
| Change password | ✅ Đã hoàn thiện | Yêu cầu mật khẩu cũ |
| Login history tracking | ✅ Đã hoàn thiện | IP, user-agent, success/fail |
| Account lockout (10 lần fail) | ✅ Đã hoàn thiện | Lock 15 phút |
| `require_admin` dependency | ✅ Đã hoàn thiện | Check `is_admin` flag |
| `require_admin_role` | ✅ Đã hoàn thiện | Đã xoá — trùng logic với `require_admin` |
| `controllers.py` (legacy auth) | ✅ Đã hoàn thiện | Đã xoá — superseded bởi `routes/auth.py` |

---

## 2. Product Management

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Product CRUD (create/read/update/delete) | ✅ Đã hoàn thiện | Service layer + audit logging |
| Product listing với filter/sort/pagination | ✅ Đã hoàn thiện | Category, search, product_type, brand |
| Product detail | ✅ Đã hoàn thiện | Includes specs, variants, reviews, images |
| Product images (upload + replace) | ✅ Đã hoàn thiện | Upload to /uploads/, CRUD qua API |
| Product variants (SKU, color, RAM, storage) | ✅ Đã hoàn thiện | Mỗi variant có giá riêng |
| Product specifications (key-value) | ✅ Đã hoàn thiện | Grouped by group_name |
| Bulk update specifications | ✅ Đã hoàn thiện | `replace_product_specifications` |
| Spec templates (template cho từng loại) | ✅ Đã hoàn thiện | product_type → template |
| SKU uniqueness check | ⚠️ Đang dở | Endpoint tồn tại nhưng frontend `CompareButton` gọi hàm không tồn tại |
| `update_product_images` | ⚠️ Đang dở | **Không có auth check** — thiếu `current_user` |
| `ProductHotspot` model | 🏗️ Architecture intention | Model tồn tại trong DB, không route/service nào dùng |
| `RelatedProduct` model | 🏗️ Architecture intention | Model tồn tại, không route nào expose |
| Product embedding (JSON vector) | 🏗️ Architecture intention | Cột `embedding` trong DB, chưa có ML pipeline |

---

## 3. Order Management

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Create order (multi-step workflow) | ✅ Đã hoàn thiện | Validate stock, deduct inventory, tạo order + items |
| Order listing (user) | ✅ Đã hoàn thiện | `get_user_orders` |
| Order listing (admin) | ✅ Đã hoàn thiện | `get_all_orders` |
| Order status update with history | ✅ Đã hoàn thiện | State machine + audit trail |
| Order tracking + timeline | ✅ Đã hoàn thiện | Status history endpoint |
| Simulate next status (dev tool) | ✅ Đã hoàn thiện | Tự động tìm transition hợp lệ |
| `update_order_status` (không history) | 🧟 Dead code | Đã bị thay thế bởi `_with_history` |
| `update_order_tracking` repository | 🧟 Dead code | Không được gọi ở đâu |

---

## 4. Cart & Wishlist

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Cart CRUD (add/remove/update/clear) | ✅ Đã hoàn thiện | 1 cart/user |
| Cart với variant support | ✅ Đã hoàn thiện | Có thể chọn variant khi add |
| Wishlist CRUD | ✅ Đã hoàn thiện | add/remove/list |
| Wishlist product IDs check | ✅ Đã hoàn thiện | `get_wishlist_product_ids` |
| `is_in_wishlist` repository | 🧟 Dead code | Không được gọi |

---

## 5. Categories

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Category CRUD (create/delete) | ✅ Đã hoàn thiện | Hierarchical tree |
| Category tree | ✅ Đã hoàn thiện | `parent_id` self-reference |
| Category deletion validation | ✅ Đã hoàn thiện | Chặn xoá nếu có children/products |
| Search suggestions | ✅ Đã hoàn thiện | Dựa trên category + product |

---

## 6. Payment (MoMo)

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| MoMo payment request | ✅ Đã hoàn thiện | Tạo signature, gọi API MoMo |
| MoMo IPN (webhook callback) | ✅ Đã hoàn thiện | Xác thực signature, cập nhật order status |
| Payment result handling | ✅ Đã hoàn thiện | Frontend page `/payment/result` |
| `payment_service` | ✅ Đã hoàn thiện | Pure business logic, không dependency vào repository |

---

## 7. Admin Dashboard

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Admin stats (products, orders, users, revenue) | ✅ Đã hoàn thiện | `get_admin_stats` — 4 repo calls |
| Revenue by month/year | ✅ Đã hoàn thiện | Analytics endpoints |
| Top searches analytics | ✅ Đã hoàn thiện | Từ search_logs |
| Top viewed products | ✅ Đã hoàn thiện | Sort by view_count |
| Cart abandonment analysis | ✅ Đã hoàn thiện | Cart vs. order comparison |
| AI description generation | ✅ Đã hoàn thiện | OpenRouter LLM + structured prompt |
| Audit log viewer | ✅ Đã hoàn thiện | Paginated, filterable |
| Session management (admin) | ✅ Đã hoàn thiện | List + revoke sessions |
| Spec template admin CRUD | ✅ Đã hoàn thiện | Đã thêm audit logging |
| `get_audit_logs_for_user` | ✅ Đã hoàn thiện | Đã xoá — không được route nào gọi |
| `get_login_history_for_user` (analytics) | ✅ Đã hoàn thiện | Đã xoá — trùng với `auth_service`'s version |

---

## 8. Chatbot (AI)

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Intent engine (rule-based) | ✅ Đã hoàn thiện | Keyword matching, confidence scoring |
| Intent engine (LLM fallback) | ✅ Đã hoàn thiện | OpenRouter khi confidence < 0.8 |
| Engine dispatcher | ✅ Đã hoàn thiện | Intent → engine routing |
| Search engine | ✅ Đã hoàn thiện | SQL query từ entities |
| Recommendation engine | ✅ Đã hoàn thiện | Content-based scoring |
| Comparison engine | ✅ Đã hoàn thiện | Side-by-side spec diff |
| Gaming check engine | ✅ Đã hoàn thiện | GPU/CPU benchmark lookup |
| Response formatter (LLM) | ✅ Đã hoàn thiện | JSON-structed output |
| Conversation memory | ✅ Đã hoàn thiện | In-memory session store |
| Chat schemas (Pydantic) | ✅ Đã hoàn thiện | `ChatRequest`, `ChatResponse` |
| Chat schemas (dataclass, nội bộ) | ⚠️ Đang dở | Trùng với Pydantic — cần hợp nhất |
| Graceful degradation (LLM offline) | ✅ Đã hoàn thiện | `openrouter_formatter.enabled` check |
| `chat_service.py` (orchestration) | ✅ Đã hoàn thiện | Điều phối toàn bộ pipeline |
| GPU/CPU benchmark seed data | ✅ Đã hoàn thiện | `seed_data.py` |
| Game requirements seed data | ✅ Đã hoàn thiện | `seed_data.py` |

---

## 9. Security Infrastructure

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Password hashing (pbkdf2_sha256) | ✅ Đã hoàn thiện | passlib |
| JWT creation + verification | ✅ Đã hoàn thiện | python-jose |
| Rate limiting (SlowAPI) | ✅ Đã hoàn thiện | 60 requests/min |
| Admin rate limiter (custom) | ✅ Đã hoàn thiện | Đã enforce qua `check_admin_rate_limit` dependency |
| CORS middleware | ✅ Đã hoàn thiện | Configurable origins |
| Exception handlers (HTTP, DB, general) | ✅ Đã hoàn thiện | Error boundary cho mọi request |
| `audit_admin_action` decorator | 🧟 Dead code | **Đã xoá** — buggy, chưa từng được dùng |
| `log_admin_action` function | ✅ Đã hoàn thiện | Đã apply cho 18 endpoints |

---

## 10. System & Infrastructure

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Health check (`/health`) | ✅ Đã hoàn thiện | Load balancer monitoring |
| System status (`/status`) | ✅ Đã hoàn thiện | Database connectivity check |
| Maintenance mode (`/maintenance`) | ✅ Đã hoàn thiện | Auth + middleware 503 + `maintenance-status` endpoint |
| Database migration (`ensure_schema`) | ⚠️ Đang dở | Chỉ handle additive changes, không có Alembic |
| Seed data on startup | ✅ Đã hoàn thiện | Admin user, categories, benchmarks |
| Static file serving (uploads) | ✅ Đã hoàn thiện | FastAPI StaticFiles mount |
| Locations API (provinces/districts/wards) | ✅ Đã hoàn thiện | JSON file cache |
| Navigation API (tree, categories, brands) | ✅ Đã hoàn thiện | `/navigation/*` endpoints |

---

## 11. Frontend Services

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| `api.js` (axios interceptor + token refresh) | ✅ Đã hoàn thiện | Queue pattern, 401 handling, toastOnce dedup |
| `authService.js` | ✅ Đã hoàn thiện | Login, register, MFA, password |
| `productService.js` | ✅ Đã hoàn thiện | Products, categories, variants, images |
| `cartService.js` | ✅ Đã hoàn thiện | Cart CRUD |
| `orderService.js` | ✅ Đã hoàn thiện | Order creation, tracking |
| `adminService.js` | ✅ Đã hoàn thiện | Stats, analytics, AI description |
| `addressService.js` | ✅ Đã hoàn thiện | Address CRUD |
| `locationService.js` | ✅ Đã hoàn thiện | Provinces/districts/wards |
| `paymentService.js` | ✅ Đã hoàn thiện | MoMo payment |
| `templateService.js` | ✅ Đã hoàn thiện | Spec templates |
| `aiService.js` | ✅ Đã hoàn thiện | `getRecommendations` gọi API `/recommendations/{productId}` |
| **`shippingService.js`** | 🧟 **Dead code** | **Gọi endpoint `/shipping-addresses` không tồn tại, không được import ở đâu** |

---

## 12. Frontend Pages & Components

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| Home page | ✅ Đã hoàn thiện | Hero, featured products, categories |
| Product list với filter/sort | ✅ Đã hoàn thiện | Category, search, brand, type |
| Product detail | ✅ Đã hoàn thiện | Specs, variants, reviews, images |
| Cart page | ✅ Đã hoàn thiện | Quantity, remove, checkout; module-level loadCart guard fix request storm |
| Checkout page | ✅ Đã hoàn thiện | Address, payment method |
| Order tracking page | ✅ Đã hoàn thiện | Timeline |
| Payment result page | ✅ Đã hoàn thiện | Success/fail |
| Login / Register | ✅ Đã hoàn thiện | Form validation |
| Profile / Edit profile | ✅ Đã hoàn thiện | Avatar, name, email |
| Forgot / Reset password | ✅ Đã hoàn thiện | Email flow |
| Wishlist page | ✅ Đã hoàn thiện | Add/remove |
| WishlistButton (global store + no duplicate API) | ✅ Đã hoàn thiện | Dùng Redux wishlistSlice, module-level guard |
| Compare products | ✅ Đã hoàn thiện | Side-by-side |
| Admin Dashboard | ✅ Đã hoàn thiện | Stats, revenue charts |
| Admin Products | ✅ Đã hoàn thiện | CRUD, variants, specs, images |
| Admin Orders | ✅ Đã hoàn thiện | Status management |
| Admin Categories | ✅ Đã hoàn thiện | Tree management |
| Admin SpecTemplates | ✅ Đã hoàn thiện | CRUD |
| Search results page | ✅ Đã hoàn thiện | Query-based |
| Category page | ✅ Đã hoàn thiện | Category tree |
| Chatbot UI | ✅ Đã hoàn thiện | Message interface |
| Compare button (`CompareButton.jsx:23`) | ✅ Đã hoàn thiện | Đã xoá — crash runtime |
| `/verify-email-change` route | ✅ Đã hoàn thiện | Đã tạo `VerifyEmailChange.jsx` page hoàn chỉnh |
| `navigationSlice.js` (Redux) | 🏗️ Architecture intention | Actions không được dispatch |
| `productSlice.js` (Redux) | 🏗️ Architecture intention | Minimal usage, hooks thay thế |

---

## 13. Layout, Store & Routing

| Module | Trạng Thái | Ghi Chú |
|---|---|---|
| MainLayout (header + footer) | ✅ Đã hoàn thiện | Navbar, category mega menu |
| AdminLayout (sidebar) | ✅ Đã hoàn thiện | Navigation + content |
| Redux store: authSlice | ✅ Đã hoàn thiện | User state, isAuthenticated |
| Redux store: cartSlice | ✅ Đã hoàn thiện | Cart items count (badge) |
| Redux store: productSlice | 🏗️ Architecture intention | Actions defined, minimal usage |
| Redux store: navigationSlice | 🏗️ Architecture intention | Actions defined, không được dispatch |
| Redux store: wishlistSlice | ✅ Đã hoàn thiện | Global wishlist IDs, initialized flag |
| AppRoutes | ✅ Đã hoàn thiện | 30+ routes, protected routes, admin guard |
| i18n (en/vi) | ✅ Đã hoàn thiện | Locale files + React integration |

---

## 14. Legacy & Dead Files

| File | Dòng | Trạng Thái | Ghi Chú |
|---|---|---|---|
| `Backend/app/controllers.py` | 1206 | ✅ Đã hoàn thiện | Đã xoá — legacy superseded bởi `routes/` |
| `Backend/app/services_old.py` | 1096 | ✅ Đã hoàn thiện | Đã xoá — legacy superseded bởi `services/` |
| `Backend/app/breadcrumb_service.py` | 94 | ✅ Đã hoàn thiện | Đã xoá — không được import |
| `Frontend/src/services/shippingService.js` | 48 | ✅ Đã hoàn thiện | Đã xoá — gọi API không tồn tại |

---

## 15. Service Layer — Phân Tích Chi Tiết

| Service | Trạng Thái | Giá Trị | Ghi Chú |
|---|---|---|---|
| `auth_service` (215 dòng) | ✅ Đã hoàn thiện | Cao | Logic đăng ký, đăng nhập, MFA, token |
| `order_service` (149 dòng) | ✅ Đã hoàn thiện | Cao | State machine, stock validation |
| `payment_service` (108 dòng) | ✅ Đã hoàn thiện | Cao | MoMo API integration |
| `recommendation_service` (287 dòng) | ✅ Đã hoàn thiện | Cao | Scoring algorithm |
| `product_service` (152 dòng) | ✅ Đã hoàn thiện | Trung bình | Pagination, spec grouping |
| `address_service` (32 dòng) | ✅ Đã hoàn thiện | Trung bình | Ownership validation |
| `cart_service` (45 dòng) | ✅ Đã hoàn thiện | Thấp | Thin wrapper, validation cơ bản |
| `category_service` (48 dòng) | ✅ Đã hoàn thiện | Thấp | Delete validation, còn lại pass-through |
| `wishlist_service` (24 dòng) | ✅ Đã hoàn thiện | Thấp | Thin wrapper |
| `session_service` (24 dòng) | ✅ Đã hoàn thiện | Thấp | `create_refresh_token_for_user`, `revoke_all_sessions`, `rotate_refresh_token` |
| `analytics_service` (32 dòng) | ✅ Đã hoàn thiện | Thấp | `get_admin_stats`, `get_audit_logs`, `get_audit_logs_for_user`, `get_login_history_for_user` |
| `user_service` (9 dòng) | ✅ Đã hoàn thiện | **Zero** | `update_profile` pass-through tới repository |

---

## 16. Repository Layer — Dead Functions

| Function | Dòng | Trạng Thái | Ghi Chú |
|---|---|---|---|
| `get_spec_template` (single) | 555 | ✅ Đã hoàn thiện | Đã xoá — không được gọi |
| `create_spec_template` | 567 | ✅ Đã hoàn thiện | Đã xoá — `_with_check` thay thế |
| `update_order_tracking` | 965 | ✅ Đã hoàn thiện | Đã xoá — không được gọi |
| `is_in_wishlist` | 706 | ✅ Đã hoàn thiện | Đã xoá — `get_wishlist_product_ids` thay thế |
| `get_audit_logs_by_user` | 1067 | ✅ Đã hoàn thiện | Đã tạo lại — dùng cho admin audit logs filter |

---

## 17. Summary Dashboard

### Bảng Tổng Quan

| Trạng Thái | Số Lượng | Diện Tích (dòng) |
|---|---|---|
| ✅ Đã hoàn thiện | ~70 modules | ~8000 dòng |
| ⚠️ Đang dở | 4 modules | ~100 dòng |
| 🧟 Dead code | 0 mục (đã xoá) | 0 dòng |
| 🎪 Demo được | Toàn bộ flow chính | — |
| 🏗️ Architecture intention | 5 mục | ~150 dòng |

### Dead Code Đã Xoá Trong Đợt Này

| Mục | Hành động |
|---|---|
| `CompareButton.jsx` | 🗑️ Xoá file — gọi function không tồn tại, crash runtime |
| `shippingService.js` | 🗑️ Xoá file — gọi endpoint không tồn tại |
| `controllers.py` (1206 dòng) | 🗑️ Xoá file — legacy |
| `services_old.py` (1096 dòng) | 🗑️ Xoá file — legacy |
| `breadcrumb_service.py` (94 dòng) | 🗑️ Xoá file — không được import |
| `user_service.py` (9 dòng) | 🔄 Đã tạo lại — cần cho `services/__init__.py` import |
| `require_admin_role` trong `deps.py` | 🗑️ Xoá function — trùng logic với `require_admin` |
| `get_spec_template` (single) trong `repositories.py` | 🗑️ Xoá function — không được gọi |
| `create_spec_template` trong `repositories.py` | 🗑️ Xoá function — `_with_check` thay thế |
| `update_order_tracking` trong `repositories.py` | 🗑️ Xoá function — không được gọi |
| `is_in_wishlist` trong `repositories.py` | 🗑️ Xoá function — `get_wishlist_product_ids` thay thế |
| `get_audit_logs_by_user` trong `repositories.py` | 🔄 Đã tạo lại — dùng cho admin audit logs filter |
| `rotate_refresh_token` trong `session_service.py` | 🗑️ Xoá function — không được route nào gọi |
| `get_audit_logs_for_user` trong `analytics_service.py` | 🗑️ Xoá function — không được route nào gọi |
| `get_login_history_for_user` trong `analytics_service.py` | 🗑️ Xoá function — trùng với auth_service |
| `update_order_status` (old) trong `order_service.py` | 🗑️ Xoá function — `_with_history` thay thế |

### Bug/Issue Đã Fix

| Vấn đề | Fix |
|---|---|
| `AdminRateLimiter.check()` không enforced | ✅ Thêm `check_admin_rate_limit` dependency vào admin router |
| `toggle_maintenance` không có auth | ✅ Thêm `current_user` + `is_admin` check, tạo `state.py` |
| `toggle_maintenance` không ảnh hưởng API | ✅ Thêm middleware trả 503 khi maintenance bật |
| `update_product_images` không có auth | ✅ Thêm `get_current_user` + `require_admin` |
| `aiService.getRecommendations()` tự fetch random | ✅ Gọi đúng endpoint `/recommendations/{productId}` |
| `/verify-email-change` route trống | ✅ Tạo `VerifyEmailChange.jsx` page hoàn chỉnh |
| Cart request storm (8662 requests) | ✅ Module-level guard + concurrent lock trong `useCart` |
| Wishlist request storm | ✅ Global Redux store + module-level guard trong `useWishlist` |
| Toast error spam trong api.js | ✅ `toastOnce` dedup với TTL 5s |

### Tính Năng Demo Được

1. **User flow:** Đăng ký → Login → Xem sản phẩm → Add to cart → Checkout → Thanh toán MoMo → Xem order tracking
2. **Admin flow:** Login admin → Dashboard stats → Quản lý sản phẩm (CRUD + variants + specs + images) → Quản lý đơn hàng (cập nhật status) → Quản lý categories → Spec templates
3. **Chatbot:** Hỏi tìm sản phẩm → So sánh sản phẩm → Kiểm tra gaming capability → Gợi ý sản phẩm
4. **Security:** MFA setup → Password reset → Email change → Session management
5. **Analytics:** Revenue charts → Top searches → Top viewed → Cart abandonment

### Tính Năng KHÔNG Demo Được (hoặc chưa ổn định)

1. **Product hotspot:** Model tồn tại nhưng không có UI
2. **Related products:** Model tồn tại nhưng không có endpoint
3. **Product embedding:** Chưa có ML pipeline

---

*Cập nhật lần cuối: 28/05/2026*
