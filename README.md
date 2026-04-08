# Fitness Tracker

A full-stack fitness tracking application for logging workouts — track exercises, sets, reps, weight, and date with a browser-based UI backed by a REST API.

## Overview

The app is split into two components:

| Component | File | Role |
|-----------|------|------|
| **Backend** | `app.py` | FastAPI REST API that stores workout data in a local SQLite database |
| **Frontend** | `streamlit_app.py` | Streamlit UI that communicates with the API to display and manage workout logs |

The backend auto-seeds demo data on first launch so you can explore the UI right away.

## Features

- **Dashboard** — at-a-glance stats: total workouts, current streak, heaviest lift, total volume
- **Workout Log** — view all entries in a sortable table, filter by exercise, delete individual rows
- **Personal Records** — automatically tracked per exercise with weight, sets, reps, and date
- **Progress Charts** — line chart of weight progression over time for any exercise
- **Quick Add** — sidebar form to log a new workout (date defaults to today)
- **Danger Zone** — delete all workout data with one click (with confirmation)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Frontend | Streamlit |
| Database | SQLite (`workout_logs.db`) |
| Data Handling | Pandas |
| HTTP Client | Requests |
| Validation | Pydantic |

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd Fitness_Tracker
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, Streamlit, Requests, Pandas, and Pydantic.

### 4. Launch the backend

```bash
python app.py
```

The API starts at **http://127.0.0.1:8000**. Interactive docs are available at `http://127.0.0.1:8000/docs` (Swagger UI).

### 5. Launch the frontend

Open a **second terminal** (activate the virtual environment again if using one), then run:

```bash
streamlit run streamlit_app.py
```

The UI opens automatically in your browser. If it doesn't, navigate to **http://localhost:8501**.

> **Tip:** Both servers need to be running simultaneously. The frontend expects the backend at `http://127.0.0.1:8000`.

## API Reference

All endpoints are prefixed with the base URL `http://127.0.0.1:8000`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/workouts` | Add a new workout |
| `GET` | `/workouts` | Retrieve all workout logs (optional `?exercise=` filter) |
| `GET` | `/workouts/exercises` | List distinct exercise names |
| `GET` | `/workouts/stats` | Dashboard stats (total workouts, streak, heaviest lift, volume) |
| `GET` | `/workouts/prs` | Personal records per exercise |
| `PUT` | `/workouts/{id}` | Update a workout by ID |
| `DELETE` | `/workouts/{id}` | Delete a workout by ID |
| `DELETE` | `/workouts` | Delete all workout logs |

### Request Body (POST / PUT)

```json
{
  "exercise": "Bench Press",
  "sets": 3,
  "reps": 10,
  "weight": 80.0,
  "date": "2026-04-05"
}
```

`date` is optional on `POST` — defaults to today's date if omitted.

### Response Example (GET /workouts/stats)

```json
{
  "total_workouts": 11,
  "current_streak": 3,
  "heaviest_lift": { "exercise": "Deadlift", "weight": 125.0 },
  "total_volume": 31250.0
}
```

## Project Structure

```
Fitness_Tracker/
├── app.py                 # FastAPI REST API + Uvicorn entry point
├── streamlit_app.py       # Streamlit frontend
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit theme & server config
├── workout_logs.db        # SQLite database (auto-created on first run)
├── .gitignore
└── README.md
```

## Configuration

### Streamlit Theme

Custom styling lives in `.streamlit/config.toml`:

- **Primary color:** `#ea580c` (orange accent)
- **Background:** `#fafafa`
- **Headless mode:** enabled (no browser auto-open on remote servers)

### Database

The SQLite database file (`workout_logs.db`) is created automatically on first run. It is ignored by Git via `.gitignore`. Demo data is seeded on first launch when the database is empty.
