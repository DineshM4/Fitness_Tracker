# TODOs for Fitness Tracker

## UI Issues (Completed)

- [x] Quick Action buttons don't do anything when clicked on
  - Fixed by using `st.session_state["main_navigation"]` to update the sidebar radio state
  - Buttons now properly navigate to Workouts or Analytics pages

- [x] Dark mode toggle is not working
  - Added JavaScript to apply `.dark` class to body element on page load and Streamlit reload
  - CSS variables (`--bg`, `--card`, `--text`) already defined for `.dark` class
  - Uses `dark_mode_toggle` session state key to persist toggle state

- [x] There should be a source from where the pre-information is coming from, saved in a SQL database or something. Not just randomly mocked up.
  - Added `/seed` endpoint that pre-populates the database with sample workouts
  - Sample data includes: Bench Press, Squat, Deadlift, Overhead Press, Bent Over Row, Pull Ups, Dumbbell Curl
  - Database seeds automatically on startup if empty
  - Returns proper error messages when backend is unreachable

## Future Enhancements (Not Yet Planned)

## Future Enhancements (Not Yet Planned)

- [ ] User registration/login with full JWT authentication
- [ ] More advanced analytics (weekly/monthly comparisons, exercise groupings)
- [ ] Mobile-responsive UI improvements
- [ ] Workout templates with auto-complete for common exercises
- [ ] Integration with external APIs (Strava, MyFitnessPal, etc.)
- [ ] PDF report generation with charts
- [ ] Backup/restore functionality
- [ ] Multi-device sync
- [ ] Workout notifications/reminders
- [ ] Social features (share workouts, compare with friends)
