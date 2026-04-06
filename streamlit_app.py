"""
Modern Fitness Tracker - Streamlit Frontend
A polished, feature-rich UI for the FastAPI backend.
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# Configuration
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Theme management - initialize session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


def apply_theme_classes():
    """Apply dark/light theme by adding class to body via JavaScript."""
    theme_class = "dark" if st.session_state.get("dark_mode", False) else "light"
    st.markdown(
        f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const body = document.querySelector('body');
            if (body) {{
                body.className = '{theme_class}';
            }}
        }});
        // Also re-apply on every rerun
        document.addEventListener('st:load', function() {{
            const body = document.querySelector('body');
            if (body) {{
                body.className = '{theme_class}';
            }}
        }});
        </script>
        """,
        unsafe_allow_html=True,
    )


# Apply theme at startup
apply_theme_classes()

# Custom CSS for modern look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #4CAF50;
        --primary-dark: #45a049;
        --secondary: #2196F3;
        --accent: #FF9800;
        --danger: #f44336;
        --bg: #f5f5f5;
        --card: #ffffff;
        --text: #333333;
    }

    .dark {
        --primary: #4CAF50;
        --primary-dark: #45a049;
        --secondary: #2196F3;
        --accent: #FF9800;
        --danger: #f44336;
        --bg: #1e1e2e;
        --card: #2d2d44;
        --text: #e0e0e0;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }

    .main { padding: 2rem; }

    .card {
        background: var(--card);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }

    .card h2 { margin-top: 0; font-weight: 600; }

    .metric {
        text-align: center;
        padding: 1rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
    }

    .metric-label {
        font-size: 0.875rem;
        color: var(--text);
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

    .pr-badge {
        display: inline-block;
        background: linear-gradient(45deg, #FF9800, #FF5722);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .workout-row { display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; }
    .workout-exercise { flex: 1; font-weight: 500; }
    .workout-stats { display: flex; gap: 1rem; font-size: 0.875rem; }

    .success { color: var(--primary); }
    .error { color: var(--danger); }

    .tabs { display: flex; gap: 1rem; border-bottom: 2px solid var(--card); margin-bottom: 1rem; }
    .tab { padding: 0.75rem 1.5rem; cursor: pointer; border: none; background: none; font-size: 1rem; color: var(--text); }
    .tab.active { border-bottom: 3px solid var(--primary); font-weight: 600; }

    .sidebar .sidebar-content { background-color: var(--card); }
    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_workouts(**filters):
    """Fetch workouts from API with optional filters."""
    try:
        url = f"{API_BASE}/workouts"
        params = []
        for k, v in filters.items():
            if v:
                params.append(f"{k}={v}")
        if params:
            url += "?" + "&".join(params)

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        st.error(
            "Cannot connect to the backend. Make sure `uvicorn app:app --reload` is running."
        )
        st.stop()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
        st.stop()


def delete_workout(workout_id):
    """Delete a specific workout."""
    try:
        response = requests.delete(f"{API_BASE}/workouts/{workout_id}", timeout=10)
        response.raise_for_status()
        return True
    except requests.ConnectionError:
        st.error("Lost connection to the backend.")
    except requests.HTTPError as e:
        st.error(f"Failed to delete workout: {e}")
    return False


def delete_all_workouts():
    """Delete all workouts."""
    try:
        response = requests.delete(f"{API_BASE}/workouts", timeout=10)
        response.raise_for_status()
        return True
    except requests.ConnectionError:
        st.error("Lost connection to the backend.")
    except requests.HTTPError as e:
        st.error(f"Failed to delete workouts: {e}")
    return False


def create_workout(data):
    """Create a new workout."""
    try:
        response = requests.post(f"{API_BASE}/workouts", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        st.error("Lost connection to the backend.")
    except requests.HTTPError as e:
        st.error(f"Failed to create workout: {e}")
    return None


def update_workout(workout_id, data):
    """Update a workout."""
    try:
        response = requests.put(f"{API_BASE}/workouts/{workout_id}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        st.error("Lost connection to the backend.")
    except requests.HTTPError as e:
        st.error(f"Failed to update workout: {e}")
    return None


# Initialize session state
if "workouts" not in st.session_state:
    st.session_state.workouts = None


def load_workouts():
    """Load workouts from API and cache them."""
    data = fetch_workouts()
    if data:
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df["volume"] = df["sets"] * df["reps"] * df["weight"]
        return df
    return pd.DataFrame()


def get_stats(workouts_df):
    """Calculate statistics from workout data."""
    if workouts_df.empty:
        return {
            "total_workouts": 0,
            "total_sets": 0,
            "total_volume": 0,
            "unique_exercises": 0,
            "pr_count": 0,
            "current_streak": 0,
            "last_workout": None,
        }

    # PRs by exercise
    prs = workouts_df.loc[workouts_df.groupby("exercise")["weight"].idxmax()]

    # Streak calculation
    dates = pd.to_datetime(workouts_df["date"]).dt.date.unique()
    dates = sorted(dates, reverse=True)
    today = datetime.now().date()
    streak = 0
    for i, d in enumerate(dates):
        if i == 0:
            expected = today
        else:
            expected = dates[i - 1] - timedelta(days=1)
        if d == expected:
            streak += 1
        else:
            break

    return {
        "total_workouts": len(workouts_df),
        "total_sets": int(workouts_df["sets"].sum()),
        "total_volume": round(workouts_df["volume"].sum(), 2),
        "unique_exercises": len(workouts_df["exercise"].unique()),
        "pr_count": len(prs),
        "current_streak": streak,
        "last_workout": dates[0] if dates else None,
    }


# Sidebar navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1249/1249063.png", width=48)
st.sidebar.title("Fitness Tracker")

# Sidebar navigation - check if active_page is set by Quick Actions
if "active_page" in st.session_state and st.session_state.active_page != page:
    page = st.session_state.active_page
    del st.session_state.active_page

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Workouts", "Analytics", "Settings"],
    index=0,
    key="main_navigation",
)

st.sidebar.divider()
st.sidebar.subheader("Quick Stats")

# Dark mode toggle - use st.session_state.dark_mode as the source of truth
st.sidebar.toggle(
    "Dark Mode",
    value=st.session_state.get("dark_mode", False),
    key="dark_mode_toggle",
)
# Sync the session state with the toggle
st.session_state.dark_mode = st.session_state.get("dark_mode_toggle", False)

# Main content
if page == "Dashboard":
    st.title("🏠 Dashboard")

    # Load data
    workouts_df = load_workouts()
    stats = get_stats(workouts_df)

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Workouts", stats["total_workouts"], delta=None)
    with col2:
        st.metric("Volume Lifted", f"{stats['total_volume']:,} kg", delta=None)
    with col3:
        st.metric("Personal Records", stats["pr_count"], delta=None)
    with col4:
        st.metric("Active Streak", f"{stats['current_streak']} days", delta=None)

    # PR Highlights
    st.divider()
    st.subheader("🏆 Recent Personal Records")

    if not workouts_df.empty:
        # Get max weights per exercise
        prs = workouts_df.loc[workouts_df.groupby("exercise")["weight"].idxmax()]
        prs = prs.sort_values("date", ascending=False).head(10)

        for _, pr in prs.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <div class="workout-row">
                        <span class="workout-exercise">{pr['exercise']}</span>
                        <div class="workout-stats">
                            <span>🥇 {pr['weight']} kg</span>
                            <span>🔥 {pr['sets']} sets</span>
                            <span>💪 {pr['reps']} reps</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No workouts logged yet. Start logging to see your stats!")

    # Quick Actions - use sidebar.radio to navigate instead of session_state
    st.divider()
    st.subheader("🚀 Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Log Workout", use_container_width=True):
            st.session_state["main_navigation"] = "Workouts"
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state["main_navigation"] = "Analytics"
            st.rerun()

elif page == "Workouts":
    st.title("📋 Workout Logs")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search Exercise", "")
    with col2:
        date_from = st.date_input("From", datetime.now() - timedelta(days=30))
    with col3:
        date_to = st.date_input("To", datetime.now())

    # Load data with filters
    workouts_df = load_workouts()
    if search:
        workouts_df = workouts_df[workouts_df["exercise"].str.contains(search, case=False)]
    if not workouts_df.empty:
        workouts_df = workouts_df[
            (workouts_df["date"].dt.date >= date_from)
            & (workouts_df["date"].dt.date <= date_to)
        ]

    # Stats on workouts page
    st.subheader(f"Summary ({len(workouts_df)} workouts)")
    if not workouts_df.empty:
        st.markdown(
            f"""
            <div style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                <div><strong>Total Sets:</strong> {int(workouts_df['sets'].sum())}</div>
                <div><strong>Total Volume:</strong> {round(workouts_df['volume'].sum(), 0)} kg</div>
                <div><strong>Unique Exercises:</strong> {workouts_df['exercise'].nunique()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Workouts table
    if not workouts_df.empty:
        st.dataframe(
            workouts_df[["date", "exercise", "sets", "reps", "weight", "volume"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": "Date",
                "exercise": "Exercise",
                "sets": "Sets",
                "reps": "Reps",
                "weight": "Weight (kg)",
                "volume": "Volume (kg)",
            },
        )

        # Bulk actions
        st.divider()
        st.subheader("Bulk Actions")
        selected_ids = st.multiselect(
            "Select workouts to delete",
            options=workouts_df["id"].tolist(),
            format_func=lambda x: f"#{x}",
        )

        if selected_ids:
            if st.button(f"🗑️ Delete {len(selected_ids)} workouts", type="primary"):
                for workout_id in selected_ids:
                    delete_workout(workout_id)
                st.rerun()
    else:
        st.info("No workouts found matching your filters.")

    # Create workout form
    st.divider()
    st.subheader("➕ Log New Workout")

    with st.form("new_workout", clear_on_submit=True):
        exercise = st.text_input("Exercise")
        col1, col2, col3 = st.columns(3)
        with col1:
            sets = st.number_input("Sets", min_value=1, value=3)
        with col2:
            reps = st.number_input("Reps", min_value=1, value=10)
        with col3:
            weight = st.number_input("Weight (kg)", min_value=0.0, value=50.0)

        col4, col5 = st.columns(2)
        with col4:
            unit = st.selectbox("Unit", ["kg", "lbs"], index=0)
        with col5:
            rpe = st.number_input("RPE (1-10)", min_value=1, max_value=10, value=None)

        notes = st.text_area("Notes", height=60)
        workout_date = st.date_input("Date", value=datetime.now().date())

        submitted = st.form_submit_button("Log Workout", type="primary")

        if submitted:
            if exercise.strip():
                data = {
                    "exercise": exercise.strip(),
                    "sets": int(sets),
                    "reps": int(reps),
                    "weight": float(weight),
                    "unit": unit,
                    "date": workout_date.isoformat(),
                }
                if rpe:
                    data["rpe"] = float(rpe)
                if notes:
                    data["notes"] = notes

                result = create_workout(data)
                if result:
                    st.success("Workout logged successfully!")
                    st.rerun()
            else:
                st.error("Please enter an exercise name.")

elif page == "Analytics":
    st.title("📈 Analytics")

    workouts_df = load_workouts()
    if workouts_df.empty:
        st.info("No workout data available for analytics. Log some workouts first!")
        st.stop()

    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Progress Charts", "Volume Analysis", "Workout Frequency", "Exercise Breakdown"]
    )

    with tab1:
        st.subheader("Progress Over Time")

        exercises = sorted(workouts_df["exercise"].unique())
        selected_ex = st.selectbox("Select Exercise", exercises, index=0)

        # Create interactive chart
        fig = go.Figure()

        # Filter data for selected exercise
        ex_data = workouts_df[workouts_df["exercise"] == selected_ex].sort_values("date")

        if len(ex_data) >= 2:
            # Add weight trend
            fig.add_trace(
                go.Scatter(
                    x=ex_data["date"],
                    y=ex_data["weight"],
                    mode="lines+markers",
                    name="Weight (kg)",
                    line=dict(color="#4CAF50", width=2),
                    marker=dict(size=6),
                )
            )

            # Add trend line
            if len(ex_data) >= 3:
                z = np.polyfit(
                    pd.to_datetime(ex_data["date"]).astype(int) / 1e9, ex_data["weight"], 1
                )
                trend = np.poly1d(z)
                fig.add_trace(
                    go.Scatter(
                        x=ex_data["date"],
                        y=trend(pd.to_datetime(ex_data["date"]).astype(int) / 1e9),
                        mode="lines",
                        name="Trend",
                        line=dict(color="#FF9800", dash="dash"),
                    )
                )

            fig.update_layout(
                title=f"{selected_ex} Progress",
                xaxis_title="Date",
                yaxis_title="Weight (kg)",
                hovermode="x unified",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Stats
            max_weight = ex_data["weight"].max()
            max_date = ex_data[ex_data["weight"] == max_weight]["date"].iloc[0]
            st.info(f"🔥 PR: {max_weight} kg on {max_date.date()}")
        else:
            st.info("Need at least 2 entries for this exercise to show a chart.")

    with tab2:
        st.subheader("Volume Analysis")

        # Volume by date
        daily_volume = (
            workouts_df.groupby("date")["volume"]
            .sum()
            .reset_index()
            .sort_values("date")
        )

        fig = px.bar(
            daily_volume,
            x="date",
            y="volume",
            title="Daily Total Volume",
            color="volume",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # Volume heat map (by day of week)
        workouts_df["day_of_week"] = workouts_df["date"].dt.day_name()
        pivot_data = (
            workouts_df.groupby(["day_of_week", "exercise"])["volume"]
            .sum()
            .reset_index()
        )

        if not pivot_data.empty:
            heatmap = pivot_data.pivot_table(
                index="day_of_week", columns="exercise", values="volume", fill_value=0
            )
            fig = px.imshow(
                heatmap,
                labels=dict(x="Exercise", y="Day", color="Volume"),
                title="Volume by Day of Week",
                color_continuous_scale="RdYlGn",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Workout Frequency")

        # Day of week distribution
        dow_counts = workouts_df["day_of_week"].value_counts().reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            fill_value=0,
        )

        fig = px.pie(
            values=dow_counts.values,
            names=dow_counts.index,
            title="Workouts by Day of Week",
            hole=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Exercise distribution
        exercise_counts = workouts_df["exercise"].value_counts()
        fig = px.bar(
            x=exercise_counts.index,
            y=exercise_counts.values,
            title="Workouts per Exercise",
            labels={"x": "Exercise", "y": "Count"},
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Exercise Breakdown")

        # Select exercise
        selected_ex = st.selectbox(
            "Select Exercise for Detailed Stats", exercises, index=0
        )

        ex_data = workouts_df[workouts_df["exercise"] == selected_ex].sort_values("date")

        if not ex_data.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Workouts", len(ex_data))
                st.metric("PR Weight", f"{ex_data['weight'].max()} kg")
            with col2:
                st.metric("Total Sets", int(ex_data["sets"].sum()))
                st.metric("Avg Reps", round(ex_data["reps"].mean(), 1))
            with col3:
                st.metric("Total Volume", round(ex_data["volume"].sum(), 0))
                st.metric("Last Workout", ex_data["date"].max().date())

            # Workout history table
            st.subheader("Workout History")
            st.dataframe(
                ex_data[["date", "sets", "reps", "weight", "volume"]],
                hide_index=True,
                use_container_width=True,
            )

elif page == "Settings":
    st.title("⚙️ Settings")

    st.subheader("Export Data")
    st.write("Export all your workout data for backup or analysis.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download JSON"):
            try:
                response = requests.post(
                    f"{API_BASE}/export", json={"format": "json"}, timeout=10
                )
                response.raise_for_status()
                st.download_button(
                    "Download JSON File",
                    response.content,
                    "workouts.json",
                    "application/json",
                )
            except Exception as e:
                st.error(f"Export failed: {e}")

    with col2:
        if st.button("Download CSV"):
            try:
                response = requests.post(
                    f"{API_BASE}/export", json={"format": "csv"}, timeout=10
                )
                response.raise_for_status()
                st.download_button(
                    "Download CSV File",
                    response.content,
                    "workouts.csv",
                    "text/csv",
                )
            except Exception as e:
                st.error(f"Export failed: {e}")

    st.divider()
    st.subheader("Danger Zone")
    st.warning("⚠️ These actions cannot be undone!")

    if st.button("Delete All Workouts"):
        if st.checkbox("I understand this will delete all my workout data"):
            if delete_all_workouts():
                st.success("All workouts deleted!")
                st.rerun()

    st.divider()
    st.subheader("About")
    st.info(
        """
        **Fitness Tracker v2.0**
        - Modern FastAPI backend with JWT authentication
        - Extended schema (units, RPE, notes)
        - Advanced analytics with Plotly charts
        - Export to JSON/CSV
        - Exercise presets and PR tracking
        """
    )

# Update session state
if "active_page" in st.session_state:
    page = st.session_state.active_page
    del st.session_state.active_page
