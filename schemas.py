"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., email=True, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, email=True, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Workout schemas
class WorkoutBase(BaseModel):
    exercise: str = Field(..., min_length=1, max_length=100)
    sets: int = Field(..., gt=0)
    reps: int = Field(..., gt=0)
    weight: float = Field(..., ge=0)
    unit: Optional[str] = "kg"
    rpe: Optional[float] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    exercise: Optional[str] = Field(None, min_length=1, max_length=100)
    sets: Optional[int] = Field(None, gt=0)
    reps: Optional[int] = Field(None, gt=0)
    weight: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    rpe: Optional[float] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class WorkoutOut(BaseModel):
    id: int
    user_id: Optional[int]
    exercise: str
    sets: int
    reps: int
    weight: float
    unit: str
    rpe: Optional[float]
    notes: Optional[str]
    date: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stats schemas
class WorkoutStats(BaseModel):
    total_workouts: int
    total_sets: int
    total_reps: int
    total_volume: float  # weight * sets * reps
    unique_exercises: int
    first_workout_date: Optional[str]
    last_workout_date: Optional[str]


class ExercisePR(BaseModel):
    exercise: str
    max_weight: float
    reps: int
    date: str
    sets: int


class PRResponse(BaseModel):
    prs: List[ExercisePR]
    total_prs: int


class VolumeHistory(BaseModel):
    date: str
    total_volume: float


class WorkoutFrequency(BaseModel):
    day_of_week: str
    count: int


# Search schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=50, le=100)


class SearchResponse(BaseModel):
    results: List[WorkoutOut]
    count: int


# Export schemas
class ExportRequest(BaseModel):
    format: str = Field(default="csv", pattern="^(csv|json)$")
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    exercises: Optional[List[str]] = None


class ExportResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None


# Exercise preset schemas
class ExercisePresetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sets: int = Field(default=3, gt=0)
    reps: str = Field(default="8-12", max_length=50)
    weight: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=200)


class ExercisePresetCreate(ExercisePresetBase):
    pass


class ExercisePresetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sets: Optional[int] = Field(None, gt=0)
    reps: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class ExercisePresetOut(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    sets: int
    reps: str
    weight: Optional[float]
    notes: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
