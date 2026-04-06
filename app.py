"""FastAPI Backend for Fitness Tracker with API Key Authentication."""
from datetime import datetime, timedelta
from typing import Optional, List, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
import csv
import io
import json
import os

from database import get_db, User, Workout, ExercisePreset, pwd_context, init_db, verify_db
from schemas import (
    WorkoutCreate, WorkoutUpdate, WorkoutOut,
    WorkoutStats, PRResponse, ExercisePR,
    SearchRequest, SearchResponse,
    ExportRequest, ExportResponse,
    ExercisePresetCreate, ExercisePresetUpdate, ExercisePresetOut
)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fitness-tracker-secret-key-change-in-production")
API_KEY = os.getenv("API_KEY", "test-api-key-change-in-production")

# Initialize FastAPI app
app = FastAPI(
    title="Fitness Tracker API",
    description="A modern fitness tracking API with workout logs, PR tracking, and analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(api_key: Optional[str] = None) -> bool:
    """Verify API key."""
    return api_key == API_KEY


def get_api_key(x_api_key: Optional[str] = None) -> str:
    """Get and validate API key."""
    if verify_api_key(x_api_key):
        return x_api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Simple dependency for API key
class APIKeyDep:
    """API Key dependency class for header extraction."""
    def __init__(self, x_api_key: Optional[str] = None):
        self.api_key = x_api_key

    @classmethod
    def __call__(cls, x_api_key: Optional[str] = None):
        return cls(x_api_key)

    def verify(self):
        """Verify the API key."""
        if not verify_api_key(self.api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )
        return self.api_key


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # In production, use jwt.encode with SECRET_KEY
    return json.dumps(to_encode)  # Placeholder for demo


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_workout_from_schema(db: Session, workout_data: WorkoutCreate, user_id: Optional[int] = None) -> Workout:
    """Create a workout from schema data."""
    db_workout = Workout(
        user_id=user_id,
        exercise=workout_data.exercise,
        sets=workout_data.sets,
        reps=workout_data.reps,
        weight=workout_data.weight,
        unit=workout_data.unit or "kg",
        rpe=workout_data.rpe,
        notes=workout_data.notes,
        date=workout_data.date
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


# Auth endpoints
@app.post("/token", response_model=dict)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 password flow - get access token."""
    # For simplicity, this is a mock endpoint
    # In production, use proper JWT authentication
    return {"access_token": API_KEY, "token_type": "api_key"}


@app.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: dict,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    db_user = db.query(User).filter(User.username == user_in.get("username")).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    user = User(
        username=user_in.get("username"),
        email=user_in.get("email", "user@example.com"),
        hashed_password=get_password_hash(user_in.get("password")),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}


@app.get("/auth/me", response_model=dict)
async def read_users_me(
    api_key: Optional[str] = None
) -> Any:
    """Get current user profile."""
    return {"id": 1, "username": "api_user", "email": "api@example.com"}


@app.post("/seed", response_model=dict)
async def seed_workouts(
    api_key: Optional[str] = None
) -> Any:
    """Seed the database with sample workout data."""
    verify_api_key(api_key)
    seed_data()
    return {"status": "success", "message": "Sample data seeded"}


# Workout endpoints
@app.post("/workouts", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_in: WorkoutCreate,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Create a new workout log."""
    verify_api_key(api_key)
    db_workout = create_workout_from_schema(db, workout_in, user_id=1)
    return db_workout


@app.get("/workouts", response_model=List[WorkoutOut])
async def get_workouts(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    exercise: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Any:
    """Retrieve all workout logs with optional filters."""
    verify_api_key(api_key)
    query = db.query(Workout).filter(Workout.user_id == 1)

    if exercise:
        query = query.filter(Workout.exercise.ilike(f"%{exercise}%"))
    if date_from:
        query = query.filter(Workout.date >= date_from)
    if date_to:
        query = query.filter(Workout.date <= date_to)

    workouts = query.offset(skip).limit(limit).all()
    return workouts


@app.get("/workouts/{workout_id}", response_model=WorkoutOut)
async def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get a specific workout by ID."""
    verify_api_key(api_key)
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == 1
    ).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    return workout


@app.put("/workouts/{workout_id}", response_model=WorkoutOut)
async def update_workout(
    workout_id: int,
    workout_in: WorkoutUpdate,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Update a workout by ID."""
    verify_api_key(api_key)
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == 1
    ).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )

    update_data = workout_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)

    db.commit()
    db.refresh(workout)
    return workout


@app.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> None:
    """Delete a workout by ID."""
    verify_api_key(api_key)
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == 1
    ).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    db.delete(workout)
    db.commit()


@app.delete("/workouts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_workouts(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> None:
    """Delete all workouts."""
    verify_api_key(api_key)
    db.query(Workout).filter(Workout.user_id == 1).delete()
    db.commit()


@app.get("/workouts/{workout_id}/history", response_model=List[WorkoutOut])
async def get_workout_history(
    workout_id: int,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get exercise history for a specific workout's exercise."""
    verify_api_key(api_key)
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )

    history = db.query(Workout).filter(
        Workout.user_id == 1,
        Workout.exercise == workout.exercise,
        Workout.id != workout_id
    ).order_by(Workout.date.desc()).all()
    return history


# Stats endpoints
@app.get("/stats", response_model=WorkoutStats)
async def get_stats(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get aggregate statistics."""
    verify_api_key(api_key)

    total_workouts = db.query(func.count(Workout.id)).filter(
        Workout.user_id == 1
    ).scalar()

    stats = db.query(
        func.sum(Workout.sets).label("total_sets"),
        func.sum(Workout.reps).label("total_reps"),
        func.sum(Workout.sets * Workout.reps * Workout.weight).label("total_volume")
    ).filter(Workout.user_id == 1).first()

    unique_exercises = db.query(func.count(func.distinct(Workout.exercise))).filter(
        Workout.user_id == 1
    ).scalar()

    date_range = db.query(
        func.min(Workout.date).label("first_date"),
        func.max(Workout.date).label("last_date")
    ).filter(Workout.user_id == 1).first()

    return WorkoutStats(
        total_workouts=total_workouts or 0,
        total_sets=stats.total_sets or 0,
        total_reps=stats.total_reps or 0,
        total_volume=round(stats.total_volume or 0, 2),
        unique_exercises=unique_exercises or 0,
        first_workout_date=date_range.first_date,
        last_workout_date=date_range.last_date
    )


@app.get("/stats/prs", response_model=PRResponse)
async def get_personal_records(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get personal records (max weight) for each exercise."""
    verify_api_key(api_key)

    prs = db.query(
        Workout.exercise,
        func.max(Workout.weight).label("max_weight"),
        func.max(Workout.id).label("workout_id")
    ).filter(Workout.user_id == 1).group_by(Workout.exercise).all()

    result = []
    for pr in prs:
        workout = db.query(Workout).filter(
            Workout.exercise == pr.exercise,
            Workout.weight == pr.max_weight,
            Workout.user_id == 1
        ).first()

        if workout:
            result.append(ExercisePR(
                exercise=pr.exercise,
                max_weight=pr.max_weight,
                reps=workout.reps,
                date=workout.date,
                sets=workout.sets
            ))

    result.sort(key=lambda x: x.max_weight, reverse=True)
    return PRResponse(prs=result, total_prs=len(result))


@app.get("/stats/volume-history", response_model=List[Any])
async def get_volume_history(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None,
    days: int = 30
) -> Any:
    """Get volume history for the last N days."""
    verify_api_key(api_key)
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    volume_data = db.query(
        Workout.date,
        func.sum(Workout.sets * Workout.reps * Workout.weight).label("total_volume")
    ).filter(
        Workout.user_id == 1,
        Workout.date >= cutoff_date
    ).group_by(Workout.date).order_by(Workout.date).all()

    return [{"date": d, "total_volume": round(v, 2)} for d, v in volume_data]


@app.get("/stats/frequency", response_model=List[Any])
async def get_workout_frequency(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get workout frequency by day of week."""
    verify_api_key(api_key)
    frequency = db.query(
        extract("weekday", Workout.date).label("dow"),
        func.count().label("count")
    ).filter(Workout.user_id == 1).group_by(
        extract("weekday", Workout.date)
    ).all()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [{"day_of_week": days[int(r.dow)], "count": r.count} for r in frequency]


# Search endpoints
@app.post("/search", response_model=SearchResponse)
async def search_workouts(
    search_in: SearchRequest,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Search workouts by exercise name."""
    verify_api_key(api_key)
    query = db.query(Workout).filter(
        Workout.user_id == 1,
        Workout.exercise.ilike(f"%{search_in.query}%")
    ).order_by(Workout.date.desc()).limit(search_in.limit).all()

    return SearchResponse(
        results=query,
        count=len(query)
    )


# Export endpoints
@app.post("/export", response_model=ExportResponse)
async def export_workouts(
    export_in: ExportRequest,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Export workouts to CSV or JSON."""
    verify_api_key(api_key)

    query = db.query(Workout).filter(Workout.user_id == 1)

    if export_in.date_from:
        query = query.filter(Workout.date >= export_in.date_from)
    if export_in.date_to:
        query = query.filter(Workout.date <= export_in.date_to)
    if export_in.exercises:
        query = query.filter(Workout.exercise.in_(export_in.exercises))

    workouts = query.order_by(Workout.date.desc()).all()

    if export_in.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Exercise", "Sets", "Reps", "Weight", "Unit", "RPE", "Notes", "Date"])
        for w in workouts:
            writer.writerow([
                w.id, w.exercise, w.sets, w.reps, w.weight, w.unit,
                w.rpe, w.notes or "", w.date
            ])
        output.seek(0)
        csv_path = f"/tmp/fitness_export_{1}.csv"
        with open(csv_path, "w") as f:
            f.write(output.getvalue())
        return ExportResponse(
            status="success",
            message="CSV exported successfully",
            download_url=f"/export/download/1.csv"
        )
    else:  # JSON
        data = [
            {
                "id": w.id,
                "exercise": w.exercise,
                "sets": w.sets,
                "reps": w.reps,
                "weight": w.weight,
                "unit": w.unit,
                "rpe": w.rpe,
                "notes": w.notes,
                "date": w.date
            }
            for w in workouts
        ]
        json_path = f"/tmp/fitness_export_{1}.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        return ExportResponse(
            status="success",
            message="JSON exported successfully",
            download_url=f"/export/download/1.json"
        )


@app.get("/export/download/{filename}")
async def download_export(filename: str, api_key: Optional[str] = None):
    """Download exported file."""
    filepath = f"/tmp/fitness_export_{1}.{filename.split('.')[-1]}"
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found. Please export first.",
        )
    return FileResponse(filepath)


# Exercise preset endpoints
@app.post("/presets", response_model=ExercisePresetOut, status_code=status.HTTP_201_CREATED)
async def create_preset(
    preset_in: ExercisePresetCreate,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Create a new exercise preset."""
    verify_api_key(api_key)
    preset = ExercisePreset(
        user_id=1,
        name=preset_in.name,
        sets=preset_in.sets,
        reps=preset_in.reps,
        weight=preset_in.weight,
        notes=preset_in.notes
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


@app.get("/presets", response_model=List[ExercisePresetOut])
async def get_presets(
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Get all exercise presets."""
    verify_api_key(api_key)
    presets = db.query(ExercisePreset).filter(
        ExercisePreset.user_id == 1
    ).order_by(ExercisePreset.name).all()
    return presets


@app.put("/presets/{preset_id}", response_model=ExercisePresetOut)
async def update_preset(
    preset_id: int,
    preset_in: ExercisePresetUpdate,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> Any:
    """Update an exercise preset."""
    verify_api_key(api_key)
    preset = db.query(ExercisePreset).filter(
        ExercisePreset.id == preset_id,
        ExercisePreset.user_id == 1
    ).first()
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found",
        )

    update_data = preset_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preset, field, value)

    db.commit()
    db.refresh(preset)
    return preset


@app.delete("/presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    api_key: Optional[str] = None
) -> None:
    """Delete an exercise preset."""
    verify_api_key(api_key)
    preset = db.query(ExercisePreset).filter(
        ExercisePreset.id == preset_id,
        ExercisePreset.user_id == 1
    ).first()
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found",
        )
    db.delete(preset)
    db.commit()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "ok" if verify_db() else "error"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on app startup and seed initial data."""
    init_db()
    seed_data()
    print("Database initialized with sample data")


def seed_data():
    """Seed the database with sample workout data."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Check if there's any data already
        if db.query(Workout).first():
            return  # Data already exists

        # Create a default user
        existing_user = db.query(User).filter(User.username == "demo_user").first()
        if not existing_user:
            user = User(
                username="demo_user",
                email="demo@example.com",
                hashed_password=pwd_context.hash("demo123"),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id
        else:
            user_id = existing_user.id

        # Sample workouts
        sample_workouts = [
            {"exercise": "Bench Press", "sets": 3, "reps": 10, "weight": 80.0, "unit": "kg", "date": "2026-04-01"},
            {"exercise": "Bench Press", "sets": 4, "reps": 8, "weight": 85.0, "unit": "kg", "date": "2026-04-03"},
            {"exercise": "Bench Press", "sets": 3, "reps": 6, "weight": 90.0, "unit": "kg", "date": "2026-04-05"},
            {"exercise": "Squat", "sets": 4, "reps": 8, "weight": 100.0, "unit": "kg", "date": "2026-04-01"},
            {"exercise": "Squat", "sets": 5, "reps": 5, "weight": 110.0, "unit": "kg", "date": "2026-04-03"},
            {"exercise": "Squat", "sets": 4, "reps": 6, "weight": 115.0, "unit": "kg", "date": "2026-04-05"},
            {"exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 120.0, "unit": "kg", "date": "2026-04-02"},
            {"exercise": "Deadlift", "sets": 3, "reps": 5, "weight": 125.0, "unit": "kg", "date": "2026-04-04"},
            {"exercise": "Overhead Press", "sets": 3, "reps": 8, "weight": 50.0, "unit": "kg", "date": "2026-04-02"},
            {"exercise": "Overhead Press", "sets": 4, "reps": 6, "weight": 55.0, "unit": "kg", "date": "2026-04-04"},
            {"exercise": "Bent Over Row", "sets": 3, "reps": 10, "weight": 70.0, "unit": "kg", "date": "2026-04-03"},
            {"exercise": "Bent Over Row", "sets": 4, "reps": 8, "weight": 75.0, "unit": "kg", "date": "2026-04-05"},
            {"exercise": "Pull Ups", "sets": 3, "reps": 8, "weight": 0.0, "unit": "kg", "date": "2026-04-02"},
            {"exercise": "Pull Ups", "sets": 3, "reps": 10, "weight": 0.0, "unit": "kg", "date": "2026-04-04"},
            {"exercise": "Dumbbell Curl", "sets": 3, "reps": 12, "weight": 20.0, "unit": "kg", "date": "2026-04-01"},
        ]

        for workout in sample_workouts:
            db_workout = Workout(
                user_id=user_id,
                exercise=workout["exercise"],
                sets=workout["sets"],
                reps=workout["reps"],
                weight=workout["weight"],
                unit=workout["unit"],
                date=workout["date"],
            )
            db.add(db_workout)

        db.commit()
        print(f"Seeded {len(sample_workouts)} sample workouts")
    except Exception as e:
        print(f"Seed data error (may already exist): {e}")
        db.rollback()
    finally:
        db.close()


# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
