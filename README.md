# 🛒 e-shop. — Hệ thống Thương mại Điện tử Bán Đồ Điện tử

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://react.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Hệ thống thương mại điện tử full-stack bán đồ điện tử (laptop, gaming gear, phụ kiện), được xây dựng với **FastAPI** (backend) và **React + Vite + Redux Toolkit** (frontend), sử dụng **MySQL** làm cơ sở dữ liệu.

<!-- screenshot -->
<p align="center">
  <em>🚧 Screenshot sẽ được bổ sung sau</em>
</p>

---

## ✨ Tính năng nổi bật

- 🔐 **Authentication & Bảo mật**: Đăng ký, đăng nhập, JWT access/refresh token, MFA (TOTP), forgot/reset password, đổi email, rate limiting, account lockout
- 📱 **MFA (Xác thực hai lớp)**: TOTP qua Google Authenticator / Authy — setup trong profile, verify khi login
- 🛍️ **Sản phẩm**: CRUD, variants (màu sắc / RAM / ổ cứng), specifications, multiple images, AI sinh mô tả sản phẩm
- 🛒 **Giỏ hàng & Thanh toán**: Cart, Checkout, MoMo e-wallet (IPN callback), COD
- 📦 **Quản lý đơn hàng**: State machine (pending → confirmed → shipped → delivered), tracking timeline, huỷ đơn
- ❤️ **Wishlist & So sánh sản phẩm**
- 🤖 **Chatbot AI**: Rule-based + LLM fallback (OpenRouter / Gemini)
- 🎯 **Recommendation Engine**: Cá nhân hoá, phổ biến, tương tự (cosine similarity), co-purchase
- 🛡️ **Admin Panel**: Dashboard thống kê, biểu đồ doanh thu, quản lý sản phẩm / đơn hàng / danh mục, audit logs, session management
- 🌐 **Đa ngôn ngữ**: Tiếng Việt & Tiếng Anh (react-i18next)

---

## 🏗️ Kiến trúc & Tech Stack

### Backend

| Thành phần | Công nghệ | Version |
|---|---|---|
| Runtime | Python | 3.12 |
| Web framework | FastAPI | 0.116.0 |
| ASGI server | Uvicorn | 0.24.0 |
| ORM | SQLAlchemy (sync) | 2.0.22 |
| DB driver | PyMySQL | 1.1.0 |
| Database | MySQL | 8.x |
| Validation | Pydantic | 2.8.0 |
| Settings | pydantic-settings | 2.8.0 |
| Auth | python-jose (JWT) + passlib[bcrypt] | 3.3.0 + 1.7.4 |
| MFA (TOTP) | pyotp | 2.9.0 |
| Rate limiter | slowapi | 0.1.9 |
| Payment | MoMo test gateway | — |
| AI/LLM client | openai (via OpenRouter) | 1.54.3 |
| SMTP | aiosmtplib | 3.0.1 |
| HTTP client | requests | 2.32.3 |

### Frontend

| Thành phần | Công nghệ | Version |
|---|---|---|
| Bundler | Vite | ^5.4.2 |
| UI library | React | ^18.3.1 |
| State management | Redux Toolkit | ^2.11.2 |
| React-Redux | react-redux | ^9.2.0 |
| Routing | react-router-dom | ^7.13.2 |
| Form | react-hook-form | ^7.73.1 |
| CSS | Tailwind CSS | ^3.4.1 |
| HTTP | Axios | ^1.14.0 |
| i18n | i18next + react-i18next | ^26.0.6 / ^17.0.4 |
| Maps | @react-google-maps/api | ^2.20.8 |
| Icons | lucide-react | ^0.344.0 |
| QR Code | qrcode.react | ^4.2.0 |
| Toast | react-hot-toast | ^2.6.0 |
| Language | TypeScript | ^5.5.3 |

---

## 📋 Yêu cầu hệ thống

- **Python** 3.12+
- **Node.js** 18+ & npm
- **MySQL** 8.x
- **Git**

---

## 🚀 Hướng dẫn cài đặt nhanh (Quick Start)

### Bước 1: Clone repository

```bash
git clone <repo-url>
cd e-shop
```

### Bước 2: Cài đặt và chạy Backend

```bash
# 2a: Tạo virtual environment
cd Backend
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # macOS/Linux

# 2b: Cài dependencies
pip install -r requirements.txt

# 2c: Tạo file .env
# Tạo file Backend/.env với nội dung bên dưới (xem cấu hình chi tiết ở phần ⚙️)

# 2d: Chạy backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Lưu ý:** Database `ShoppingWeb` sẽ được tự động tạo nếu chưa tồn tại (nhờ `ensure_mysql_database_exists` trong `database.py`). Schema cũng được tạo tự động bởi `Base.metadata.create_all()`.

Backend sẽ chạy tại **http://localhost:8000**.  
Swagger UI: **http://localhost:8000/docs**  
Admin seed tự động: **admin@example.com / adminpass**

### Bước 3: Cài đặt và chạy Frontend

```bash
# Mở terminal mới, cd về thư mục gốc
cd Frontend

# 3a: Cài dependencies
npm install

# 3b: Tạo file .env
# Tạo file Frontend/.env:
echo VITE_API_BASE_URL=http://localhost:8000 > .env
echo VITE_GOOGLE_MAPS_API_KEY=your-key-here >> .env

# 3c: Chạy dev server
npm run dev
```

Frontend sẽ chạy tại **http://localhost:5173**.

### Bước 4: Truy cập hệ thống

| URL | Mô tả |
|---|---|
| http://localhost:5173 | Trang chủ |
| http://localhost:5173/login | Đăng nhập |
| http://localhost:8000/docs | Swagger UI (API docs) |
| http://localhost:8000/redoc | ReDoc (API docs) |

**Tài khoản admin mặc định:** `admin@example.com` / `adminpass`

---

## ⚙️ Cấu hình chi tiết

### 6.1 Backend — `Backend/.env`

```env
# ─── BẮT BUỘC ───────────────────────────────────────
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ShoppingWeb
SECRET_KEY=your-very-long-random-secret-key-here

# ─── JWT (có giá trị mặc định) ──────────────────────
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256
MFA_CHALLENGE_EXPIRE_SECONDS=300

# ─── AI / Chatbot (tuỳ chọn) ────────────────────────
# Chatbot vẫn hoạt động rule-based nếu không có key này.
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=google/gemini-2.0-flash-001
OPENROUTER_MAX_TOKENS=1024

# ─── Thanh toán MoMo (tuỳ chọn) ─────────────────────
# Chỉ cần nếu test flow thanh toán MoMo.
# Khi test local, dùng ngrok để expose port 8000 cho IPN.
MOMO_PARTNER_CODE=
MOMO_ACCESS_KEY=
MOMO_SECRET_KEY=
MOMO_ENDPOINT=https://test-payment.momo.vn/v2/gateway/api/create
MOMO_REDIRECT_URL=http://localhost:5173/payment/result
MOMO_IPN_URL=https://your-ngrok-url.ngrok.io/payment/momo/ipn

# ─── Email SMTP (tuỳ chọn) ──────────────────────────
# Cần nếu dùng forgot password / đổi email.
# Dùng Gmail App Password (không phải password thường).
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_NAME=Electronics Store

# ─── Frontend URL (dùng để tạo link trong email) ────
FRONTEND_URL=http://localhost:5173

# ─── CORS ────────────────────────────────────────────
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

# ─── Site info (dùng trong QR MFA và email) ─────────
SITE_NAME=Your Electronics Store
SITE_URL=http://localhost:5173
```

### 6.2 Frontend — `Frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```


### 6.3 Hướng dẫn lấy Gmail App Password (cho SMTP)

1. Vào https://myaccount.google.com/security
2. Bật **2-Step Verification** (xác thực 2 bước)
3. Vào Security → **App Passwords**
4. Chọn **Mail** + **Windows Computer** → Generate
5. Copy mật khẩu 16 ký tự → dán vào `SMTP_PASSWORD`

### 6.4 Hướng dẫn cấu hình ngrok cho MoMo IPN (khi test local)

```bash
# Cài ngrok: https://ngrok.com/download
ngrok http 8000
# Copy URL https://xxx.ngrok.io → dán vào MOMO_IPN_URL trong .env
# Restart backend
```

---

## 🗄️ Database

- **Engine:** MySQL 8.x
- **Database name:** `ShoppingWeb`
- **Charset:** `utf8mb4`
- **Không cần chạy migration** — SQLAlchemy tự động tạo schema khi backend khởi động (`Base.metadata.create_all()`). Một số cột bổ sung được thêm qua `ensure_schema()`.
- Database cũng được **tự động tạo** nếu chưa tồn tại (nhờ `ensure_mysql_database_exists`).

Nếu cần tạo thủ công:

```sql
CREATE DATABASE IF NOT EXISTS ShoppingWeb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### Seed data tự động

Khi backend khởi động lần đầu, hệ thống tự động seed:
- 👤 **Admin user:** `admin@example.com` / `adminpass`
- 📂 **Danh mục sản phẩm:** Điện thoại, Laptop, Tablet, Phụ kiện, Gaming Gear, v.v.
- 🏷️ **Thương hiệu:** Apple, Samsung, Dell, ASUS, Sony, v.v.
- 🖥️ **GPU/CPU benchmark data** (cho recommendation engine)
- 🎮 **Game requirements** (cho chatbot tư vấn cấu hình)

---

## 📁 Cấu trúc thư mục

```
├── Backend/                        # FastAPI backend
│   ├── app/
│   │   ├── core/                   # Config, database, security, rate limit
│   │   │   ├── config.py           # pydantic-settings
│   │   │   ├── database.py         # SQLAlchemy engine + ensure_mysql_database_exists
│   │   │   ├── security.py         # JWT, password hashing, TOTP secret
│   │   │   ├── admin_security.py   # Account lockout, audit logging
│   │   │   ├── rate_limit.py       # slowapi limiter
│   │   │   └── email.py            # SMTP email builder
│   │   ├── routes/                 # 15+ API routers
│   │   │   ├── auth.py             # Auth + MFA endpoints
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   ├── cart.py
│   │   │   ├── admin.py            # Admin dashboard + management
│   │   │   ├── payment.py          # MoMo integration
│   │   │   ├── chatbot.py
│   │   │   └── ...
│   │   ├── services/               # Business logic layer
│   │   ├── repositories.py         # Data access layer
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── main.py                 # App entry point, startup seed
│   │   └── chatbot/                # AI chatbot engines
│   ├── requirements.txt
│   └── .env                        # Backend cấu hình
│
├── Frontend/                       # React + Vite frontend
│   ├── src/
│   │   ├── pages/                  # 30+ React pages
│   │   │   ├── Login.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── EditProfile.jsx     # Avatar, password, email, MFA settings
│   │   │   ├── OrderTracking.jsx
│   │   │   ├── Cart.jsx
│   │   │   ├── Checkout.jsx
│   │   │   ├── Wishlist.jsx
│   │   │   └── admin/              # Admin pages
│   │   ├── components/             # Reusable UI components
│   │   │   ├── auth/               # AuthLayout, AuthCard, AuthInput, AuthButton...
│   │   │   ├── Navbar.jsx
│   │   │   └── ...
│   │   ├── services/               # API service layer (Axios)
│   │   ├── store/                  # Redux slices (auth, cart, wishlist)
│   │   ├── hooks/                  # Custom hooks (useAuth, useCart, useWishlist)
│   │   ├── locales/                # i18n translations (en, vi)
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.ts
│   └── .env                        # Frontend cấu hình
│
├── package.json                    # Root package (scripts: dev, build)
└── README.md
```

---

## 🔐 Tài khoản mặc định

| Role | Email | Password | Ghi chú |
|---|---|---|---|
| Admin | `admin@example.com` | `adminpass` | Tự động tạo khi backend startup lần đầu |
| User | (đăng ký qua `/register`) | — | — |

> ⚠️ **Lưu ý bảo mật:** Đổi password admin ngay sau lần đầu đăng nhập trên môi trường production.

---

## 📡 API Documentation

| Loại | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Nhóm API endpoints chính

| Nhóm | Router | Ví dụ endpoint |
|---|---|---|
| Auth | `/auth/*` | `POST /auth/login`, `POST /auth/register` |
| MFA | `/auth/mfa/*` | `POST /auth/mfa/setup`, `POST /auth/mfa/verify` |
| Sản phẩm | `/products/*` | `GET /products`, `GET /products/{id}` |
| Danh mục | `/categories/*` | `GET /categories` |
| Giỏ hàng | `/cart/*` | `GET /cart`, `POST /cart/add` |
| Đơn hàng | `/orders/*` | `POST /orders`, `GET /orders/{id}/tracking` |
| Thanh toán | `/payment/*` | `POST /payment/momo/create`, `POST /payment/momo/ipn` |
| Wishlist | `/wishlist/*` | `GET /wishlist`, `POST /wishlist/add` |
| Admin | `/admin/*` | `GET /admin/stats`, `GET /admin/orders` |
| Chatbot | `/api/chat` | `POST /api/chat` |
| Recommendations | `/recommendations/*` | `GET /recommendations/personalized` |
| Users | `/users/*` | `PUT /users/me` |
| Addresses | `/addresses/*` | `GET /addresses`, `POST /addresses` |
| Uploads | `/upload-avatar` | `POST /upload-avatar` |

---

## 🧪 Kiểm thử hệ thống

Sau khi chạy cả backend và frontend, test nhanh các luồng chính:

### 1. Health check

```bash
curl http://localhost:8000/health
# → {"status": "ok", "message": "Server is running"}
```

### 2. Đăng nhập admin (qua Swagger)

1. Mở http://localhost:8000/docs
2. `POST /auth/login` → `{ "email": "admin@example.com", "password": "adminpass" }`
3. Copy `access_token` → Authorize (nút bên phải) → `Bearer {token}`
4. Gọi `GET /auth/me` → thấy thông tin admin

### 3. Test chatbot

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tư vấn laptop gaming dưới 20 triệu"}'
```

### 4. Test MFA flow

1. Đăng nhập → vào Edit Profile
2. Bấm "Bật xác thực hai lớp" → nhập mật khẩu
3. Quét QR bằng Google Authenticator
4. Nhập mã 6 số → Kích hoạt
5. Đăng xuất → đăng nhập lại → nhập mã TOTP

---

## 🌐 Đa ngôn ngữ (i18n)

- **Hỗ trợ:** Tiếng Việt (`vi`) và Tiếng Anh (`en`)
- **Cơ chế:** `react-i18next` + `i18next-browser-languagedetector`
- **Tự động:** Phát hiện ngôn ngữ trình duyệt khi lần đầu truy cập
- **Thủ công:** Toggle qua Settings icon (⚙️) trên Navbar

---

## ❓ Troubleshooting

| Lỗi | Nguyên nhân | Cách fix |
|---|---|---|
| `Can't connect to MySQL server` | MySQL chưa chạy hoặc sai credentials | Kiểm tra MySQL service, kiểm tra `DATABASE_URL` |
| `ModuleNotFoundError` | Chưa cài dependencies | Chạy `pip install -r requirements.txt` |
| CORS error trên browser | `ALLOWED_ORIGINS` thiếu địa chỉ frontend | Thêm URL vào `ALLOWED_ORIGINS` trong `Backend/.env` |
| `400 MFA not set up` | Gọi `/mfa/verify` trước `/mfa/setup` | Làm đúng thứ tự: setup → verify |
| `400 Invalid verification code` | Mã TOTP sai hoặc lệch đồng hồ | Đảm bảo đồng hồ điện thoại đúng giờ, thử lại |
| MoMo IPN không nhận được | `MOMO_IPN_URL` trỏ localhost | Dùng ngrok: `ngrok http 8000`, copy URL vào `.env` |
| Email không gửi được | Sai App Password hoặc chưa bật 2FA | Tạo Gmail App Password đúng (xem mục 6.3) |
| `npm install` lỗi | Node.js version quá cũ | Cập nhật Node.js lên 18+ |

---

## 📝 License

MIT License — xem file [LICENSE](LICENSE).
