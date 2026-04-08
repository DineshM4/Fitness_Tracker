from datetime import date

import pandas as pd
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:5001"


def fetch_all():
    response = requests.get(f"{API_BASE}/workouts")
    response.raise_for_status()
    data = response.json()
    return [
        (w["id"], w["exercise"], w["sets"], w["reps"], w["weight"], w.get("date", ""))
        for w in data
    ]


def create_workout(exercise, sets, reps, weight, workout_date):
    response = requests.post(
        f"{API_BASE}/workouts",
        json={
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "date": workout_date,
        },
    )
    response.raise_for_status()


def update_workout(workout_id, exercise, sets, reps, weight, workout_date):
    response = requests.put(
        f"{API_BASE}/workouts/{workout_id}",
        json={
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "date": workout_date,
        },
    )
    response.raise_for_status()


def delete_workout(workout_id):
    response = requests.delete(f"{API_BASE}/workouts/{workout_id}")
    response.raise_for_status()


def delete_all_workouts():
    response = requests.delete(f"{API_BASE}/workouts")
    response.raise_for_status()


st.title("Fitness Tracker")

# --- Fetch data (with connection error handling) ---
try:
    rows = fetch_all()
except requests.ConnectionError:
    st.error(
        "Cannot connect to the Flask backend. Make sure `python app.py` is running on port 5000."
    )
    st.stop()
except requests.HTTPError as e:
    st.error(f"API error: {e}")
    st.stop()

# --- Build DataFrame once ---
df = (
    pd.DataFrame(
        rows, columns=["ID", "Exercise", "Sets", "Reps", "Weight (kg)", "Date"]
    )
    if rows
    else pd.DataFrame(columns=["ID", "Exercise", "Sets", "Reps", "Weight (kg)", "Date"])
)

# --- Database Table ---
st.header("Workout Logs")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No workout logs found.")

st.divider()

# --- Progress Chart ---
st.header("Progress Over Time")
if not df.empty:
    df_chart = df[df["Date"].notna() & (df["Date"] != "")]

    exercises = sorted(df_chart["Exercise"].unique())
    if exercises:
        selected = st.selectbox("Select exercise", exercises)
        df_filtered = (
            df_chart[df_chart["Exercise"] == selected]
            .copy()
            .assign(Date=lambda d: pd.to_datetime(d["Date"]))
            .sort_values("Date")
        )
        if len(df_filtered) >= 2:
            st.line_chart(df_filtered.set_index("Date")["Weight (kg)"])
        elif len(df_filtered) == 1:
            st.info(
                "Only one entry for this exercise — log more sessions to see a trend."
            )
        else:
            st.info("No dated entries for this exercise.")
    else:
        st.info("No dated entries available for charting.")
else:
    st.info("No workout data yet to chart.")

st.divider()

# --- Action Buttons ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Create Workout", use_container_width=True):
        st.session_state.active_form = "create"

with col2:
    if st.button("Update Workout", use_container_width=True):
        st.session_state.active_form = "update"

with col3:
    if st.button("Delete Workout", use_container_width=True):
        st.session_state.active_form = "delete"

with col4:
    if st.button("Delete All", use_container_width=True, type="primary"):
        st.session_state.active_form = "delete_all"

# --- Forms ---
active = st.session_state.get("active_form")

if active == "create":
    st.subheader("Create Workout")
    with st.form("create_form"):
        exercise = st.text_input("Exercise")
        sets = st.number_input("Sets", min_value=1, step=1)
        reps = st.number_input("Reps", min_value=1, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
        workout_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Add")
        if submitted:
            if exercise.strip():
                try:
                    create_workout(
                        exercise.strip(),
                        int(sets),
                        int(reps),
                        float(weight),
                        workout_date.isoformat(),
                    )
                    st.success("Workout added!")
                    st.session_state.active_form = None
                    st.rerun()
                except requests.ConnectionError:
                    st.error("Lost connection to the backend.")
            else:
                st.error("Exercise name cannot be empty.")

elif active == "update":
    st.subheader("Update Workout")
    with st.form("update_form"):
        workout_id = st.number_input("Workout ID to update", min_value=1, step=1)
        exercise = st.text_input("New Exercise")
        sets = st.number_input("New Sets", min_value=1, step=1)
        reps = st.number_input("New Reps", min_value=1, step=1)
        weight = st.number_input("New Weight (kg)", min_value=0.0, step=0.5)
        workout_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Update")
        if submitted:
            if exercise.strip():
                try:
                    update_workout(
                        int(workout_id),
                        exercise.strip(),
                        int(sets),
                        int(reps),
                        float(weight),
                        workout_date.isoformat(),
                    )
                    st.success(f"Workout {workout_id} updated!")
                    st.session_state.active_form = None
                    st.rerun()
                except requests.ConnectionError:
                    st.error("Lost connection to the backend.")
                except requests.HTTPError:
                    st.error(f"No workout found with ID {workout_id}.")
            else:
                st.error("Exercise name cannot be empty.")

elif active == "delete":
    st.subheader("Delete Workout")
    with st.form("delete_form"):
        workout_id = st.number_input("Workout ID to delete", min_value=1, step=1)
        submitted = st.form_submit_button("Delete")
        if submitted:
            try:
                delete_workout(int(workout_id))
                st.success(f"Workout {workout_id} deleted!")
                st.session_state.active_form = None
                st.rerun()
            except requests.ConnectionError:
                st.error("Lost connection to the backend.")
            except requests.HTTPError:
                st.error(f"No workout found with ID {workout_id}.")

elif active == "delete_all":
    st.subheader("Delete All Workouts")
    st.warning("This will permanently delete every workout log. This cannot be undone.")
    with st.form("delete_all_form"):
        submitted = st.form_submit_button("Yes, delete everything", type="primary")
        if submitted:
            try:
                delete_all_workouts()
                st.success("All workouts deleted.")
                st.session_state.active_form = None
                st.rerun()
            except requests.ConnectionError:
                st.error("Lost connection to the backend.")
