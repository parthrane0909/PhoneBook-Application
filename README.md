# Phonebook Application

A responsive contact workspace built with FastAPI, PostgreSQL, SQLAlchemy, Vue 3, Pinia, Axios, and Vue Router.

## Features

- Contact CRUD with name, phone, email, address, and validation
- Search by name or phone with server-side pagination
- Favorites and recently viewed contacts persisted in PostgreSQL
- Sorting by name, recently viewed, recently added, or recently updated
- Relational labels using `tags` and `contact_tags`
- Responsive desktop table and mobile contact cards
- Bulk selection, favorite actions, delete confirmation, and undo
- Keyboard shortcuts: `/` search, `n` new contact, `Escape` close dialogs
- Settings for appearance, page size, delete confirmation, and shortcuts
- CSV export of the active contact view
- CSV import with header validation, row validation, duplicate detection, and import summaries

## Project Structure

- `backend/app`: FastAPI application, SQLAlchemy models, schemas, and routes
- `backend/tests`: API tests
- `frontend/src`: Vue application, router, Pinia store, components, and views
- `docker-compose.yml`: PostgreSQL, backend, and frontend services

## Docker Setup

Copy `.env.example` to `.env`, change the placeholder database password, then run:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The API is available at `http://localhost:8000/docs`.

The backend connects to PostgreSQL through the Docker service name `db`, not `localhost`.

## Local Setup

### Backend

Create a virtual environment and install dependencies:

```bash
cd backend
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Set `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, and `DATABASE_NAME` in `backend/.env`, then run:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Local Vite development proxies `/api` to `http://localhost:8000`. Set `VITE_API_PROXY_TARGET` when the backend is running elsewhere. Docker sets this target to the `backend` service.

## Testing

From the project root:

```bash
cd backend
pytest
```

The tests cover contact creation, retrieval, update, deletion, validation, duplicate phone prevention, labels, search, and recently viewed persistence.

## API Endpoints

- `GET /contacts/` with `search`, `favorite`, `tag`, `sort`, `page`, and `limit`
- `POST /contacts/`
- `GET /contacts/{id}`
- `PUT /contacts/{id}`
- `DELETE /contacts/{id}`
- `PATCH /contacts/{id}/favorite`
- `PATCH /contacts/{id}/viewed`
- `GET /contacts/tags`
- `GET /contacts/metrics`
- `POST /contacts/import` with validated `name`, `phone_number`, `email`, `address`, and optional `tags`

## Usage

Use the sidebar to switch between all contacts, favorites, recently viewed contacts, labels, and settings. Select a table row to open its detail drawer. Use Import to validate and add a CSV, or Export to download the current filtered contact view using only name, phone number, email, and address fields. Labels are selected or created through the label selector and are stored as relational records.
