# Phonebook Application

A responsive contact workspace built with FastAPI, PostgreSQL, SQLAlchemy, Vue 3, Pinia, Axios, Vue Router, and Nginx.

## Features

- Contact CRUD with name, phone, email, address, tags, and validation
- Phone number validation with optional `+`, spaces, hyphens, and parentheses, supporting 7–15 digits
- Search by name, phone number, or tag with server-side pagination
- Favorites and recently viewed contacts persisted in PostgreSQL
- Sorting by name, recently viewed, recently added, or recently updated
- Relational tags using `tags` and `contact_tags`
- Tag filtering from the Contacts page
- Responsive desktop table and mobile contact cards
- Bulk selection, favorite actions, delete confirmation, and undo
- Keyboard shortcuts: `/` search, `n` new contact, `Escape` close dialogs
- Settings for appearance, page size, delete confirmation, and shortcuts
- CSV export of the active contact view, including tags
- CSV/XLSX/XLS import with drag-and-drop, preview, validation, duplicate detection, tag support, and import summaries
- Unrelated columns in imported files are ignored
- Adaptive pagination with page navigation and direct page input
- Light and dark appearance modes

## Architecture

The application uses Nginx as a reverse proxy so that the Vue frontend and FastAPI backend are accessed through a single origin.

```text
Browser
    │
    │ http://localhost:8080
    ▼
Nginx
    ├── / ────────────────→ Vue :5173
    │
    └── /api/* ───────────→ FastAPI :8000
                                  │
                                  ▼
                             PostgreSQL :5432
The browser communicates only with http://localhost:8080.

API requests use the /api prefix externally:
http://localhost:8080/api/contacts/
Nginx removes the /api prefix before forwarding the request to FastAPI:

/api/contacts/
      ↓
/contacts/
      ↓
FastAPI

This allows the frontend and backend to be served from the same origin without requiring browser-side CORS configuration.

Project Structure
backend/app: FastAPI application, SQLAlchemy models, schemas, and routes
backend/tests: API tests
frontend/src: Vue application, router, Pinia store, components, and views
playwright/tests: Playwright end-to-end tests
playwright/test-data: Playwright test data
nginx/nginx.conf: Nginx reverse proxy configuration
docker-compose.yml: PostgreSQL, backend, frontend, and Nginx services
Docker Setup

Copy .env.example to .env, change the placeholder database password, then run:

docker compose up --build

Open the application at:

http://localhost:8080

The frontend and backend are accessed through Nginx.

The backend connects to PostgreSQL through the Docker service name db, not localhost.

The backend and frontend containers are internal Docker services and are not directly exposed to the host. Nginx provides the public application entry point on port 8080.

To stop the application:

docker compose down

To remove the PostgreSQL volume as well:

docker compose down -v
Local Setup
Backend

Create a virtual environment and install dependencies:

cd backend

python3 -m venv venv

. venv/bin/activate

pip install -r requirements.txt

Set DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, and DATABASE_NAME in backend/.env, then run:

uvicorn app.main:app --reload
Frontend
cd frontend

npm install

npm run dev

For the Docker deployment, the frontend is served through Nginx and the application is accessed at:

http://localhost:8080
Nginx Reverse Proxy

Nginx acts as the reverse proxy and provides a single public entry point for the application.

The routing is:

/          → frontend:5173
/api/*     → backend:8000

For example:

http://localhost:8080/

is routed to the Vue frontend.

An API request such as:

http://localhost:8080/api/contacts/

is routed by Nginx to:

http://backend:8000/contacts/

The frontend therefore does not need to communicate directly with the backend container.

Testing
Backend Tests

From the project root:

cd backend

pytest

The backend tests cover contact creation, retrieval, update, deletion, validation, duplicate phone prevention, tags, search, and recently viewed persistence.

Playwright End-to-End Tests

The project also includes Playwright UI tests covering the main application workflows.

The Playwright suite runs against the complete Docker-based application through Nginx rather than starting a separate frontend development server.

From the Playwright directory:

cd playwright

npx playwright test --reporter=list

If the Playwright browser has not been installed:

npx playwright install chromium

The Playwright suite covers:

Contact creation, editing, favorites, and deletion
Frontend validation
Search by name, phone number, and tag
Tag filtering and combined search/filter behavior
Pagination and page navigation
CSV import and validation
Import preview and drag-and-drop upload
CSV export including tags
Light and dark appearance settings
Recently viewed contacts
Responsive mobile layout
Creation/seeding of a dataset containing up to 1000 contacts
API Endpoints

The FastAPI backend provides the following endpoints:

GET    /
GET    /contacts/
POST   /contacts/
GET    /contacts/{id}
PUT    /contacts/{id}
DELETE /contacts/{id}
PATCH  /contacts/{id}/favorite
PATCH  /contacts/{id}/viewed
GET    /contacts/tags
GET    /contacts/metrics
POST   /contacts/import

The API is exposed to the browser through the Nginx /api prefix.

For example:

GET http://localhost:8080/api/contacts/

is forwarded by Nginx to:

GET /contacts/

The GET /contacts/ endpoint supports search, favorite, tag, unlabeled, recent, sort, page, and limit parameters.

POST /contacts/import supports validated name, phone_number, email, address, and optional tags data.

Usage

Use the sidebar to switch between all contacts, favorites, recently viewed contacts, and settings.

Use the main Contacts page to search by name, phone number, or tag, apply filters, sort contacts, and navigate through paginated results. Tags are available through the tag filter and can also be matched through the universal search.

Select a table row to open its detail drawer.

Use Import to upload a CSV, XLSX, or XLS file. Imported data is previewed and validated before submission. Unrelated columns are ignored, and tags can be imported from the tags column.

Use Export to download the current filtered contact view, including name, phone number, email, address, and tags.

Tags are selected or created through the tag selector and are stored as relational records.