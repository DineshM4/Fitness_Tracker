"""Database configuration and models for Fitness Tracker."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.context import CryptContext

# Database setup
DATABASE_URL = "sqlite:///workout_logs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Models
class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("ExercisePreset", back_populates="user", cascade="all, delete-orphan")


class Workout(Base):
    """Workout log model with extended schema."""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for backwards compat
    exercise = Column(String(100), nullable=False, index=True)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    unit = Column(String(10), default="kg")  # kg or lbs
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion
    notes = Column(Text, nullable=True)
    date = Column(String(10), nullable=False, index=True)  # ISO format date
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="workouts")


class ExercisePreset(Base):
    """Saved exercise presets for users."""
    __tablename__ = "exercise_presets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    sets = Column(Integer, default=3)
    reps = Column(String(50), default="8-12")  # e.g., "8-12" or "10"
    weight = Column(Float, nullable=True)
    notes = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


# Verify database connection
def verify_db():
    """Verify database connection and schema."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False
