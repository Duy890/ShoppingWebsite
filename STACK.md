# STACK — Technology Stack (actual)

## Backend
| Thành phần | Công nghệ | Version | Ghi chú |
|---|---|---|---|
| **Runtime** | Python | 3.12.10 | |
| **Web framework** | FastAPI | 0.116.0 | |
| **ASGI server** | Uvicorn | 0.24.0 | |
| **ORM** | SQLAlchemy | 2.0.22 | Dạng sync (không dùng async session) |
| **DB driver** | PyMySQL | 1.1.0 | |
| **Database** | MySQL | (phụ thuộc máy chủ) | Dùng `mysql+pymysql` |
| **Validation** | Pydantic | 2.8.0 | |
| **Settings** | pydantic-settings | 2.8.0 | |
| **Auth** | python-jose (JWT) + passlib[bcrypt] | 3.3.0 + 1.7.4 | HS256, access token 1440p |
| **MFA** | pyotp | 2.9.0 | TOTP |
| **Rate limiter** | slowapi | 0.1.9 | |
| **Payment** | MoMo test gateway | — | Endpoint test, không dùng SDK |
| **OpenAI client** | openai | 2.37.0 | Chỉ dùng cho chatbot OpenRouter |
| **SMTP** | aiosmtplib | 5.1.0 | Gửi email (Gmail SMTP) |
| **HTTP client** | requests | 2.32.3 | Cho MoMo + OpenRouter proxy |

### Không có trong project
- **Alembic**: ❌ Không dùng — migration làm bằng tay SQL
- **Redis/Celery**: ❌ Không dùng
- **Docker**: ❌ Không có Dockerfile hay docker-compose
- **CI/CD**: ❌ Không có (không GitHub Actions, GitLab CI, Jenkins)
- **Async DB**: ❌ SQLAlchemy sync session, không async
- **pytest/mypy/ruff/black/flake8**: ❌ Không có trong dev dependencies

## Frontend
| Thành phần | Công nghệ | Version | Ghi chú |
|---|---|---|---|
| **Bundler** | Vite | ^5.4.2 | |
| **UI library** | React | ^18.3.1 | (classic, không có Server Components) |
| **State management** | Redux Toolkit (RTK) | ^2.11.2 | RTK (viết tắt của Redux Toolkit) |
| **React-Redux** | react-redux | ^9.2.0 | Kết nối component với store |
| **Routing** | react-router-dom | ^7.13.2 | |
| **Form** | react-hook-form | ^7.73.1 | |
| **CSS** | Tailwind CSS | ^3.4.1 | |
| **HTTP** | Axios | ^1.14.0 | Có interceptor gắn token |
| **i18n** | i18next | ^26.0.6 | react-i18next + browser detector |
| **Maps** | @react-google-maps/api | ^2.20.8 | |
| **Icons** | lucide-react | ^0.344.0 | |
| **TypeScript** | TypeScript | ^5.5.3 | |
| **Linter** | ESLint | ^9.9.1 | flat config (eslint.config.js) |

### Không có trong project
- **Next.js/Nuxt/SvelteKit**: ❌ Dùng Vite + React thuần
- **Redux classic (createStore)**: ❌ Đã dùng Redux Toolkit (configureStore)
- **Redux Thunk/Saga**: ❌ RTK đã built-in createAsyncThunk
- **React Query/SWR**: ❌ Không dùng

## Hosting & Deploy
| Yếu tố | Trạng thái |
|---|---|
| **Hosting** | Không xác định (chạy local: `localhost:5173` frontend, `localhost:8000` backend) |
| **Docker** | Không dùng |
| **CI/CD** | Không có |
| **Domain** | Không có (config `your-store.com`) |

## Database
| Yếu tố | Giá trị |
|---|---|
| **Engine** | MySQL (thông qua PyMySQL) |
| **Connection** | `mysql+pymysql://root:***@localhost:3306/ShoppingWeb` |
| **Migration tool** | Không có (Alembic chưa setup) |
| **Schema** | SQLAlchemy `declarative_base()` — tạo bảng bằng `Base.metadata.create_all()` |

## Dev Dependencies (Backend — KHÔNG CÓ)
Không có pytest, mypy, ruff, black, flake8, pre-commit.

## Dev Dependencies (Frontend)
| Package | Version | Mục đích |
|---|---|---|
| @vitejs/plugin-react | ^4.3.1 | Vite React plugin |
| typescript | ^5.5.3 | Type checking |
| eslint + plugins | ^9.9.1 | Linting |
| tailwindcss + postcss + autoprefixer | ^3.4.1 + ^8.4.35 + ^10.4.18 | CSS utility |
