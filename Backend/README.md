# Shop Backend

This is the FastAPI backend for the Shop storefront.

## Run locally

1. Create a Python environment:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Install dependencies:

   pip install -r requirements.txt

3. Configure a supported SQL database by creating a `.env` file with a `DATABASE_URL` for MySQL or PostgreSQL, for example:

   # PostgreSQL example
   DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/shopdb

   # MySQL example
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/shopdb

   Then install dependencies and start the server.

4. Start the API server:

   uvicorn app.main:app --reload --

5. The frontend is configured to call the backend at `http://localhost:8000`.

## Default admin user

A default admin account is created on startup if it does not exist:

- Email: `admin@example.com`
- Password: `adminpass`

## API endpoints

The backend exposes endpoints for:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /users/me`
- `GET /products`
- `GET /products/{id}`
- `POST /products`
- `PUT /products/{id}`
- `DELETE /products/{id}`
- `GET /categories`
- `POST /categories`
- `GET /cart`
- `POST /cart/items`
- `PATCH /cart/items/{itemId}`
- `DELETE /cart/items/{itemId}`
- `DELETE /cart/clear`
- `POST /orders`
- `GET /orders`
- `GET /orders/{id}`
- `GET /admin/orders`
- `PUT /orders/{id}/status`
- `GET /admin/stats`
