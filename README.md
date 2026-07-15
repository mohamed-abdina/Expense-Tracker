# Expense Tracker API

A Django + Django REST Framework backend for personal finance tracking: JWT
authentication, categories, transactions (income/expense), a dashboard, and
reporting endpoints (monthly, by category, income vs expense, highest
income/expense).

## Tech Stack

- **Backend:** Django 5
- **API:** Django REST Framework
- **Database:** SQLite by default (swap to MySQL/PostgreSQL by editing `DATABASES` in `config/settings.py`)
- **Auth:** JWT via `djangorestframework-simplejwt`

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # then edit .env and set a real DJANGO_SECRET_KEY

python manage.py migrate
python manage.py createsuperuser  # optional, for /admin/
python manage.py runserver
```

The API is served at `http://localhost:8000/`. The Django admin (if you
created a superuser) is at `http://localhost:8000/admin/`.

## Authentication

Every endpoint below requires this header, except register/login:
```
Authorization: Bearer <access_token>
```

### Register
`POST /api/register/`
```json
{
  "username": "jane",
  "email": "jane@example.com",
  "password": "supersecret123",
  "password2": "supersecret123"
}
```
Returns the created user plus `access` and `refresh` tokens.

### Login
`POST /api/login/`
```json
{ "username": "jane", "password": "supersecret123" }
```
Returns `access`, `refresh`, and `user`.

### Refresh token
`POST /api/login/refresh/`
```json
{ "refresh": "<refresh_token>" }
```

### Profile
`GET /api/profile/` — returns the logged-in user's `id`, `username`, `email`, `first_name`, `last_name`, `date_joined`.
`PUT`/`PATCH /api/profile/` — update `email`, `first_name`, `last_name`.

## Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories/` | list your categories (optional `?type=income\|expense`) |
| POST | `/api/categories/` | create — `{ "name": "Food", "type": "expense" }` |
| GET | `/api/categories/{id}/` | retrieve one |
| PUT/PATCH | `/api/categories/{id}/` | update |
| DELETE | `/api/categories/{id}/` | delete |

Categories are scoped per-user, and `(user, name, type)` is unique.

## Transactions

Each transaction has: `title`, `amount`, `type` (`income`/`expense`), `category`
(a category id, must match the transaction's type), `notes`, `date`
(`YYYY-MM-DD`).

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/transactions/` | list (filters below) |
| POST | `/api/transactions/` | create |
| GET | `/api/transactions/{id}/` | retrieve one |
| PUT/PATCH | `/api/transactions/{id}/` | update |
| DELETE | `/api/transactions/{id}/` | delete |

**Filters on list:** `?type=income|expense`, `?category=<id>`,
`?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`, `?search=<text>`

**Create example:**
```json
{
  "title": "Salary",
  "amount": 1200,
  "type": "income",
  "category": 1,
  "date": "2026-07-14",
  "notes": "July Salary"
}
```

## Dashboard

`GET /api/dashboard/`
```json
{
  "total_income": 3200.00,
  "total_expenses": 845.50,
  "current_balance": 2354.50,
  "number_of_transactions": 18,
  "recent_transactions": [ /* last 5, most recent first */ ]
}
```

## Reports

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/monthly/?month=YYYY-MM` | income/expenses/net + per-category breakdown for a month (defaults to current month) |
| GET | `/api/reports/category/?type=&date_from=&date_to=` | totals grouped by category |
| GET | `/api/reports/income-vs-expense/?date_from=&date_to=` | income vs expenses vs net for a period |
| GET | `/api/reports/highest-expense/?date_from=&date_to=` | single largest expense transaction |
| GET | `/api/reports/highest-income/?date_from=&date_to=` | single largest income transaction |

## Project Structure

```
expense-tracker-api/
├── backend/
│   ├── config/           # settings, root urls, wsgi/asgi
│   ├── accounts/         # register, login, profile (uses Django's built-in User model)
│   ├── categories/       # Category model + CRUD API
│   ├── transactions/     # Transaction model + CRUD API
│   ├── reports/          # dashboard + report endpoints (no models — aggregates the two apps above)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## Database Design

**User** (Django's built-in `auth.User`): `id`, `username`, `email`, `password`, `date_joined`

**Category**: `id`, `name`, `type` (`income`/`expense`), `user` (FK), `created_at`

**Transaction**: `id`, `title`, `amount`, `type` (`income`/`expense`), `category` (FK, nullable), `notes`, `date`, `created_at`, `user` (FK)

## Notes on this build

- Passwords are hashed by Django's default auth system (PBKDF2); never stored in plain text.
- A transaction's `category` must belong to the same user and have the same `type` (income category can't be attached to an expense transaction, etc.) — enforced in the serializer.
- This project was written and syntax-checked (`python -m py_compile`) in a sandboxed environment without network access, so `pip install` and `python manage.py migrate/runserver` could not be executed here. Migrations were hand-written to match the models so `migrate` should work immediately after `pip install -r requirements.txt`. Please run it locally and open an issue/fix if anything surfaces — the code follows standard, well-tested Django/DRF/SimpleJWT patterns throughout.
