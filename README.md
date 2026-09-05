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

Set `VITE_API_BASE_URL` when the API is not running at `http://localhost:8000`.

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

## Usage

Use the sidebar to switch between all contacts, favorites, recently viewed contacts, labels, and settings. Select a table row to open its detail drawer. Labels are entered as comma-separated values in the contact forms and are stored as relational records.
