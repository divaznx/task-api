# Task API

REST API for creating, listing, updating, and deleting tasks. Built with FastAPI and backed by a Supabase `tasks` table.

## Features

- List all tasks and fetch a single task by ID
- Create tasks with a required title and optional description
- Partial updates via `PATCH` (`title`, `description`, `completed`)
- Delete tasks
- `404` when a task ID is missing; `400` when a patch body has no fields

## Tech stack

| Layer | Library |
| --- | --- |
| HTTP | FastAPI |
| Validation | Pydantic |
| Database | Supabase |
| Config | python-dotenv |

## Prerequisites

- Python 3.10 or later (models use `str | None` union syntax)
- A [Supabase](https://supabase.com) project with a `tasks` table

### Expected table

The API reads and writes these columns:

| Column | Used for |
| --- | --- |
| `id` | Lookups, updates, and deletes |
| `title` | Create and update |
| `description` | Create and update |
| `completed` | Update (`PATCH` only; create currently inserts `title` and `description`) |

## Setup

Clone the repo and create a virtual environment:

```bash
git clone <repo-url>
cd task-api
python -m venv venv
```

Activate it:

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install fastapi uvicorn python-dotenv supabase
```

Create a `.env` file in the project root (this file is gitignored):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
```

## Run

From the project root:

```bash
uvicorn main:app --reload
```

- Health check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

`GET /` returns:

```json
{"message": "Task API v1.0.0 is running."}
```

## Frontend

A vanilla HTML/CSS/JS UI lives in `frontend/`. The API does not send CORS headers, so the UI is served by a small stdlib proxy that forwards `/tasks` to Uvicorn.

With the API already running on port 8000, in another terminal:

```bash
python frontend/server.py
```

Open [http://127.0.0.1:5500](http://127.0.0.1:5500). You can add a task, toggle completed, and delete.

Do not open `index.html` as a file or from another static server; those origins cannot call the API.

## API reference

| Method | Path | Body | Success |
| --- | --- | --- | --- |
| `GET` | `/` | — | `{ "message": "Task API v1.0.0 is running." }` |
| `GET` | `/tasks` | — | `{ "tasks": [ ... ] }` |
| `GET` | `/tasks/{task_id}` | — | `{ "task": [ ... ] }` |
| `POST` | `/tasks` | `{ "title": "...", "description": "..." }` | `{ "task": [ ... ] }` |
| `PATCH` | `/tasks/{task_id}` | Any subset of `title`, `description`, `completed` | `{ "task": [ ... ] }` |
| `DELETE` | `/tasks/{task_id}` | — | `{ "message": "Task deleted successfully." }` |

### Create body

```json
{
  "title": "Ship the README",
  "description": "Optional",
  "completed": false
}
```

`title` is required. `description` and `completed` are optional; `completed` defaults to `false` on the request model, but the create handler inserts only `title` and `description`.

### Patch body

Send only the fields you want to change. An empty object returns `400`.

```json
{
  "completed": true
}
```

### Errors

| Status | When |
| --- | --- |
| `400` | `PATCH` with no fields set |
| `404` | Task ID not found on get, update, or delete |

Unexpected database errors are returned as `{ "error": "<message>" }`.

## Project structure

```text
task-api/
├── main.py            # FastAPI app and GET /
├── database.py        # Supabase client from .env
├── models/
│   └── task.py        # Task and TaskUpdate models
├── routes/
│   └── tasks.py       # CRUD routes
└── frontend/
    ├── index.html     # Task UI
    ├── styles.css
    ├── app.js
    └── server.py      # Static files + /tasks proxy
```

## Note

Importing [`database.py`](database.py) creates the Supabase client and **inserts a sample row** into `tasks` (`title`: `Sample Task 3`). That runs whenever the app starts, so each reload can add another sample task.
