"""FastAPI Backend for Fitness Tracker."""

import sqlite3
from datetime import date, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Fitness Tracker API",
    description="A clean REST API for tracking workouts, personal records, and streaks.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---


class WorkoutCreate(BaseModel):
    exercise: str
    sets: int
    reps: int
    weight: float
    date: Optional[str] = None


class WorkoutUpdate(BaseModel):
    exercise: str
    sets: int
    reps: int
    weight: float
    date: Optional[str] = None


class WorkoutOut(BaseModel):
    id: int
    exercise: str
    sets: int
    reps: int
    weight: float
    date: Optional[str] = None


class StatsOut(BaseModel):
    total_workouts: int
    current_streak: int
    heaviest_lift: Optional[dict] = None
    total_volume: float


# --- Database ---


def get_db():
    conn = sqlite3.connect("workout_logs.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            date TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


def seed_db():
    """Seed demo data if the database is empty."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM workout_logs").fetchone()[0]
    if count == 0:
        today = date.today()
        demo_data = [
            ("Bench Press", 4, 8, 80.0, (today - timedelta(days=13)).isoformat()),
            ("Squat", 4, 6, 100.0, (today - timedelta(days=12)).isoformat()),
            ("Deadlift", 3, 5, 120.0, (today - timedelta(days=11)).isoformat()),
            ("Bench Press", 4, 10, 82.5, (today - timedelta(days=9)).isoformat()),
            ("Overhead Press", 3, 8, 50.0, (today - timedelta(days=8)).isoformat()),
            ("Squat", 4, 8, 105.0, (today - timedelta(days=6)).isoformat()),
            ("Deadlift", 3, 5, 125.0, (today - timedelta(days=5)).isoformat()),
            ("Bench Press", 4, 8, 85.0, (today - timedelta(days=3)).isoformat()),
            ("Overhead Press", 4, 6, 55.0, (today - timedelta(days=2)).isoformat()),
            ("Squat", 4, 8, 110.0, (today - timedelta(days=1)).isoformat()),
            ("Bench Press", 5, 6, 90.0, today.isoformat()),
        ]
        conn.executemany(
            "INSERT INTO workout_logs (exercise, sets, reps, weight, date) VALUES (?, ?, ?, ?, ?)",
            demo_data,
        )
        conn.commit()
    conn.close()


seed_db()


# --- Endpoints ---


@app.post("/workouts", response_model=WorkoutOut, status_code=201)
def create_workout(workout: WorkoutCreate):
    workout_date = workout.date or date.today().isoformat()
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO workout_logs (exercise, sets, reps, weight, date) VALUES (?, ?, ?, ?, ?)",
        (workout.exercise, workout.sets, workout.reps, workout.weight, workout_date),
    )
    conn.commit()
    workout_id = cursor.lastrowid
    row = conn.execute(
        "SELECT * FROM workout_logs WHERE id = ?", (workout_id,)
    ).fetchone()
    conn.close()
    return dict(row)


@app.get("/workouts", response_model=List[WorkoutOut])
def get_workouts(exercise: Optional[str] = None):
    conn = get_db()
    if exercise:
        rows = conn.execute(
            "SELECT * FROM workout_logs WHERE exercise LIKE ? ORDER BY date DESC",
            (f"%{exercise}%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM workout_logs ORDER BY date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/workouts/exercises", response_model=List[str])
def get_exercises():
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT exercise FROM workout_logs ORDER BY exercise"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


@app.get("/workouts/stats", response_model=StatsOut)
def get_stats():
    conn = get_db()

    # Total workouts
    total = conn.execute("SELECT COUNT(*) FROM workout_logs").fetchone()[0]

    # Current streak
    dates = [
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT date FROM workout_logs WHERE date IS NOT NULL ORDER BY date DESC"
        ).fetchall()
    ]
    streak = 0
    if dates:
        date_set = set(date.fromisoformat(d) for d in dates)
        check = date.today()
        if check not in date_set:
            check -= timedelta(days=1)
        while check in date_set:
            streak += 1
            check -= timedelta(days=1)

    # Heaviest lift
    heaviest = conn.execute(
        "SELECT exercise, weight FROM workout_logs ORDER BY weight DESC LIMIT 1"
    ).fetchone()
    heaviest_lift = (
        {"exercise": heaviest[0], "weight": heaviest[1]} if heaviest else None
    )

    # Total volume
    volume = conn.execute(
        "SELECT COALESCE(SUM(sets * reps * weight), 0) FROM workout_logs"
    ).fetchone()[0]

    conn.close()
    return StatsOut(
        total_workouts=total,
        current_streak=streak,
        heaviest_lift=heaviest_lift,
        total_volume=round(volume, 1),
    )


@app.get("/workouts/prs")
def get_personal_records():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT w.exercise, w.weight, w.sets, w.reps, w.date
        FROM workout_logs w
        INNER JOIN (
            SELECT exercise, MAX(weight) as max_weight
            FROM workout_logs
            GROUP BY exercise
        ) m ON w.exercise = m.exercise AND w.weight = m.max_weight
        GROUP BY w.exercise
        ORDER BY w.exercise
    """
    ).fetchall()
    conn.close()
    return [
        {"exercise": r[0], "weight": r[1], "sets": r[2], "reps": r[3], "date": r[4]}
        for r in rows
    ]


@app.put("/workouts/{workout_id}")
def update_workout(workout_id: int, workout: WorkoutUpdate):
    workout_date = workout.date or date.today().isoformat()
    conn = get_db()
    cursor = conn.execute(
        "UPDATE workout_logs SET exercise=?, sets=?, reps=?, weight=?, date=? WHERE id=?",
        (
            workout.exercise,
            workout.sets,
            workout.reps,
            workout.weight,
            workout_date,
            workout_id,
        ),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Workout not found")
    conn.close()
    return {"message": "Workout updated"}


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int):
    conn = get_db()
    cursor = conn.execute("DELETE FROM workout_logs WHERE id=?", (workout_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Workout not found")
    conn.close()
    return {"message": "Workout deleted"}


@app.delete("/workouts")
def delete_all_workouts():
    conn = get_db()
    conn.execute("DELETE FROM workout_logs")
    conn.commit()
    conn.close()
    return {"message": "All workouts deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
