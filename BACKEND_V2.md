# FastAPI Backend (v2)

## Overview
This is the new FastAPI backend with JWT authentication, extended schema, and comprehensive API endpoints.

## Features
- JWT-based authentication with bcrypt password hashing
- Extended workout schema (units, RPE, notes)
- User management (register, login, profile)
- Workout CRUD operations
- Stats and analytics endpoints
- Search functionality
- Export to CSV/JSON
- Exercise presets

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app:app --reload

# Server will be available at http://127.0.0.1:8000
```

## API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Authentication
- `POST /token` - Get access token (OAuth2 password flow)
- `POST /auth/register` - Register a new user
- `GET /auth/me` - Get current user profile

### Workouts
- `POST /workouts` - Create a new workout
- `GET /workouts` - List all workouts (with filters)
- `GET /workouts/{id}` - Get a specific workout
- `PUT /workouts/{id}` - Update a workout
- `DELETE /workouts/{id}` - Delete a workout
- `DELETE /workouts` - Delete all workouts
- `GET /workouts/{id}/history` - Get exercise history

### Stats & Analytics
- `GET /stats` - Aggregate statistics
- `GET /stats/prs` - Personal records by exercise
- `GET /stats/volume-history` - Volume over time
- `GET /stats/frequency` - Workout frequency by day

### Search & Export
- `POST /search` - Search workouts
- `POST /export` - Export workouts (CSV/JSON)
- `GET /export/download/{filename}` - Download exported file

### Exercise Presets
- `POST /presets` - Create a preset
- `GET /presets` - List all presets
- `PUT /presets/{id}` - Update a preset
- `DELETE /presets/{id}` - Delete a preset

### Utility
- `GET /health` - Health check

## Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision -m "description"

# Auto-generate a migration
alembic revision --autogenerate -m "description"
```

## Project Structure
```
Fitness_Tracker/
├── app.py              # FastAPI application
├── database.py         # SQLAlchemy models and DB setup
├── schemas.py          # Pydantic models
├── alembic/            # Database migrations
│   └── versions/
├── workout_logs.db     # SQLite database
└── requirements.txt    # Python dependencies
```
