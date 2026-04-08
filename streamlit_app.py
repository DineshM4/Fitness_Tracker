"""Fitness Tracker - Streamlit Frontend"""

from datetime import date

import pandas as pd
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Fitness Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- API Functions ---


def fetch_workouts(exercise=None):
    params = {"exercise": exercise} if exercise else {}
    response = requests.get(f"{API_BASE}/workouts", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_stats():
    response = requests.get(f"{API_BASE}/workouts/stats", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_prs():
    response = requests.get(f"{API_BASE}/workouts/prs", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_exercises():
    response = requests.get(f"{API_BASE}/workouts/exercises", timeout=10)
    response.raise_for_status()
    return response.json()


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
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def delete_workout(workout_id):
    response = requests.delete(f"{API_BASE}/workouts/{workout_id}", timeout=10)
    response.raise_for_status()


def delete_all_workouts():
    response = requests.delete(f"{API_BASE}/workouts", timeout=10)
    response.raise_for_status()


# --- Custom CSS ---

st.markdown(
    """
<style>
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        border: 1px solid #e7e5e4;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(234, 88, 12, 0.15);
    }
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #ea580c, #fb923c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 13px;
        color: #78716c;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-icon {
        font-size: 28px;
        margin-bottom: 4px;
    }
    .pr-row {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        border: 1px solid #e7e5e4;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Render Helpers ---


def render_card(icon, value, label):
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# --- Main App ---

# Connection check
try:
    stats = fetch_stats()
except requests.ConnectionError:
    st.error(
        "⚠️ Cannot connect to the FastAPI backend. Make sure `python app.py` is running on port 8000."
    )
    st.stop()
except requests.HTTPError as e:
    st.error(f"API error: {e}")
    st.stop()

# --- Header ---
st.title("Fitness Tracker")
st.caption("Track workouts. Crush PRs. Stay consistent.")

# --- Dashboard Cards ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_card("🏋️", str(stats["total_workouts"]), "Total Workouts")

with col2:
    streak_val = stats["current_streak"]
    render_card(
        "🔥",
        f"{streak_val} day{'s' if streak_val != 1 else ''}",
        "Current Streak",
    )

with col3:
    if stats.get("heaviest_lift"):
        h = stats["heaviest_lift"]
        render_card("🏆", f"{h['weight']}kg", f"Heaviest: {h['exercise']}")
    else:
        render_card("🏆", "—", "Heaviest Lift")

with col4:
    vol = stats["total_volume"]
    if vol >= 1000:
        vol_str = f"{vol / 1000:.1f}k"
    else:
        vol_str = str(int(vol))
    render_card("📊", f"{vol_str}kg", "Total Volume")

st.divider()

# --- Tabs ---
tab_log, tab_prs, tab_progress = st.tabs(
    ["📋 Workout Log", "🏆 Personal Records", "📈 Progress"]
)

with tab_log:
    # Filter
    exercises = fetch_exercises()
    selected_exercise = st.selectbox("Filter by exercise", ["All"] + exercises)

    # Fetch and display
    exercise_filter = None if selected_exercise == "All" else selected_exercise
    workouts = fetch_workouts(exercise=exercise_filter)

    if workouts:
        df = pd.DataFrame(workouts)
        df = df[["id", "exercise", "sets", "reps", "weight", "date"]]
        df.columns = ["ID", "Exercise", "Sets", "Reps", "Weight (kg)", "Date"]
        st.dataframe(df, width="stretch", hide_index=True, height=400)

        # Delete individual workout
        st.write("")
        del_col1, del_col2 = st.columns([3, 1])
        with del_col2:
            delete_id = st.number_input(
                "ID to delete", min_value=1, step=1, key="delete_id"
            )
            if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                try:
                    delete_workout(delete_id)
                    st.success(f"Workout {delete_id} deleted!")
                    st.rerun()
                except requests.HTTPError:
                    st.error(f"Workout {delete_id} not found.")
    else:
        st.info("No workouts found. Add one from the sidebar! 👈")

with tab_prs:
    prs = fetch_prs()
    if prs:
        for pr in prs:
            st.markdown(
                f"""
            <div class="pr-row">
                <div>
                    <span style="font-size: 18px; font-weight: 600; color: #1c1917;">{pr["exercise"]}</span><br>
                    <span style="font-size: 12px; color: #78716c;">{pr["sets"]}×{pr["reps"]} on {pr.get("date", "N/A")}</span>
                </div>
                <div style="font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #ea580c, #fb923c); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {pr["weight"]}kg
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No PRs yet. Start logging workouts! 💪")

with tab_progress:
    if exercises:
        selected = st.selectbox("Select exercise", exercises, key="progress_exercise")
        workouts = fetch_workouts(exercise=selected)
        if workouts:
            df = pd.DataFrame(workouts)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            if len(df) >= 2:
                st.line_chart(df.set_index("date")["weight"], height=400)
                st.caption(f"Weight progression for {selected}")
            elif len(df) == 1:
                st.info("Only one entry — log more sessions to see a trend!")
        else:
            st.info("No data for this exercise.")
    else:
        st.info("No exercises logged yet.")

# --- Sidebar: Quick Add ---
with st.sidebar:
    st.header("➕ Quick Add")
    with st.form("quick_add"):
        exercise = st.text_input("Exercise", placeholder="e.g. Bench Press")
        sets = st.number_input("Sets", min_value=1, step=1)
        reps = st.number_input("Reps", min_value=1, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
        workout_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Add Workout", use_container_width=True)
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
                    st.success("✅ Workout added!")
                    st.rerun()
                except requests.ConnectionError:
                    st.error("Lost connection to the backend.")
            else:
                st.error("Exercise name cannot be empty.")

    st.divider()

    # Danger zone
    with st.expander("⚠️ Danger Zone"):
        st.write("This will delete **all** workout data. This cannot be undone.")
        if st.button("🗑️ Delete All Workouts", type="primary", use_container_width=True):
            delete_all_workouts()
            st.success("All workouts deleted.")
            st.rerun()
