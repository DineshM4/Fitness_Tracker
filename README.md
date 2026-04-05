# Fitness Tracker

A full-stack fitness tracking application for logging workouts — track exercises, sets, reps, weight, and date with a browser-based UI backed by a REST API.

## Overview

The app is split into two components:

- **Backend** (`app.py`) — A Flask REST API that stores workout data in a local SQLite database
- **Frontend** (`streamlit_app.py`) — A Streamlit UI that communicates with the API to display and manage workout logs

## Features

- Log workouts with exercise name, sets, reps, weight, and date
- View all workout logs in a sortable table
- Visualize weight progress over time per exercise with a line chart
- Add new workout entries via a form (date defaults to today)
- Update existing workout entries by ID
- Delete a single workout entry by ID
- Delete all workout logs at once (with confirmation prompt)
- Graceful error handling if the backend is unreachable

## Tech Stack

- **Python** — core language
- **Flask** — REST API backend
- **SQLite** — local database (`workout_logs.db`)
- **Streamlit** — interactive frontend UI
- **Pandas** — data display and chart preparation
- **Requests** — HTTP client used by the frontend to call the API

## Getting Started

### Prerequisites

```bash
pip install flask
```

### Running the App

Start both servers in separate terminals:

**1. Start the Flask backend:**
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000`.

**2. Start the Streamlit frontend:**
```bash
streamlit run streamlit_app.py
```
The UI will open automatically in your browser.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/workouts` | Retrieve all workout logs |
| `POST` | `/workouts` | Add a new workout |
| `PUT` | `/workouts/<id>` | Update a workout by ID |
| `DELETE` | `/workouts/<id>` | Delete a workout by ID |
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

`date` is optional on POST — defaults to today's date if omitted.

## Project Structure

```
Fitness_Tracker/
├── app.py             # Flask REST API
├── streamlit_app.py   # Streamlit frontend
├── workout_logs.db    # SQLite database (auto-created on first run)
└── README.md
```
