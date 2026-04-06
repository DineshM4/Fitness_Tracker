# Fitness Tracker - Modern Version

A full-stack fitness tracking application with workout logging, analytics, and PR tracking.

## Overview

This application features:

- **FastAPI Backend**: Modern REST API with async support, JWT auth (configurable), and comprehensive endpoints
- **SQLite Database**: Local storage with Alembic migrations
- **Streamlit UI**: Polished dashboard with Plotly charts, PR tracking, and stats

## Features

### Workout Logging
- Log workouts with exercise name, sets, reps, weight, and date
- Track RPE (Rate of Perceived Exertion) 1-10
- Add notes per workout
- Support for kg/lbs units

### Analytics & Insights
- Personal Records (PRs) by exercise
- Volume tracking over time
- Workout frequency heatmap by day of week
- Progress charts with trend lines
- Daily/weekly volume breakdown

### Data Management
- Export workouts to JSON/CSV
- Search workouts by exercise name
- Bulk delete workouts
- Exercise presets (save favorite workouts)

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, Alembic, Passlib
- **Frontend**: Python, Streamlit, Pandas, Plotly, Numpy
- **Authentication**: API Key (configurable) or JWT

## Getting Started

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (runs migrations)
python3 -c "from database import init_db; init_db()"
```

### Running the App

**1. Start the FastAPI backend:**
```bash
uvicorn app:app --reload
```
The API will be available at `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

**2. Start the Streamlit frontend:**
```bash
streamlit run streamlit_app.py
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/workouts` | Create a workout (X-API-Key header) |
| `GET` | `/workouts` | List all workouts |
| `GET` | `/workouts/{id}` | Get a specific workout |
| `PUT` | `/workouts/{id}` | Update a workout |
| `DELETE` | `/workouts/{id}` | Delete a workout |
| `GET` | `/stats` | Aggregate statistics |
| `GET` | `/stats/prs` | Personal records by exercise |
| `GET` | `/stats/volume-history` | Volume over time |
| `POST` | `/search` | Search workouts |
| `POST` | `/export` | Export to JSON/CSV |

### Authentication

The API uses an API key for authentication. Add `X-API-Key: test-api-key-change-in-production` to your headers.

For production, set `API_KEY` environment variable and update the `api_key` dependency in `app.py`.

## Project Structure

```
Fitness_Tracker/
├── app.py                 # FastAPI backend
├── database.py           # SQLAlchemy models and DB setup
├── schemas.py            # Pydantic models
├── streamlit_app.py      # Streamlit frontend
├── requirements.txt      # Python dependencies
├── alembic/              # Database migrations
│   └── versions/
├── workout_logs.db       # SQLite database (auto-created)
└── README.md
```

## Migration from v1

The original Flask app (`app.py`) has been replaced with a FastAPI backend. Old data is preserved:

1. The `workout_logs` table is preserved
2. New tables (`workouts`, `users`, `exercise_presets`) are created
3. Migrations apply schema changes

## License

MIT License
