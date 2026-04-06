#!/usr/bin/env python3
"""Test script for the FastAPI Fitness Tracker backend."""
import requests
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "test-api-key-change-in-production"  # Should match the app


def wait_for_server(timeout=30):
    """Wait for the server to be ready."""
    print("Waiting for server to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    print("Server not ready after timeout")
    return False


def get_headers():
    """Get auth headers."""
    return {"X-API-Key": API_KEY}


def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health ===")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"Health: {data}")
    assert response.status_code == 200
    assert data["status"] == "healthy"
    print("✓ Health check passed")


def test_workouts():
    """Test workout CRUD operations."""
    print("\n=== Testing Workouts ===")

    # Create a workout
    print("Creating workout...")
    workout_data = {
        "exercise": "Bench Press",
        "sets": 3,
        "reps": 10,
        "weight": 80.0,
        "unit": "kg",
        "rpe": 7.5,
        "notes": "Good session",
        "date": "2026-04-05",
    }
    response = requests.post(
        f"{BASE_URL}/workouts", json=workout_data, headers=get_headers()
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"
    workout = response.json()
    print(f"Created workout: {workout}")
    workout_id = workout["id"]

    # Get all workouts
    print("Getting all workouts...")
    response = requests.get(f"{BASE_URL}/workouts", headers=get_headers())
    assert response.status_code == 200
    workouts = response.json()
    print(f"Found {len(workouts)} workouts")

    # Get specific workout
    print(f"Getting workout {workout_id}...")
    response = requests.get(f"{BASE_URL}/workouts/{workout_id}", headers=get_headers())
    assert response.status_code == 200
    print("✓ Workout retrieval passed")

    # Update workout
    print("Updating workout...")
    response = requests.put(
        f"{BASE_URL}/workouts/{workout_id}",
        json={"weight": 85.0, "notes": "Updated notes"},
        headers=get_headers(),
    )
    assert response.status_code == 200
    print("✓ Workout update passed")

    # Get history for exercise
    print("Getting exercise history...")
    response = requests.get(
        f"{BASE_URL}/workouts/{workout_id}/history", headers=get_headers()
    )
    assert response.status_code == 200
    print("✓ Exercise history passed")

    # Delete workout
    print(f"Deleting workout {workout_id}...")
    response = requests.delete(
        f"{BASE_URL}/workouts/{workout_id}", headers=get_headers()
    )
    assert response.status_code == 204
    print("✓ Workout deletion passed")


def test_stats():
    """Test stats endpoints."""
    print("\n=== Testing Stats ===")

    # Create a few workouts first
    for i in range(3):
        requests.post(
            f"{BASE_URL}/workouts",
            json={
                "exercise": f"Exercise {i+1}",
                "sets": 3,
                "reps": 10,
                "weight": 50.0 + i * 10,
                "unit": "kg",
                "date": "2026-04-05",
            },
            headers=get_headers(),
        )

    # Get stats
    print("Getting stats...")
    response = requests.get(f"{BASE_URL}/stats", headers=get_headers())
    assert response.status_code == 200
    stats = response.json()
    print(f"Stats: {stats}")
    assert "total_workouts" in stats
    assert "total_volume" in stats
    print("✓ Stats passed")

    # Get PRs
    print("Getting personal records...")
    response = requests.get(f"{BASE_URL}/stats/prs", headers=get_headers())
    assert response.status_code == 200
    prs = response.json()
    print(f"PRs: {prs}")
    assert "prs" in prs
    print("✓ PRs passed")

    # Get volume history
    print("Getting volume history...")
    response = requests.get(f"{BASE_URL}/stats/volume-history", headers=get_headers())
    assert response.status_code == 200
    volume = response.json()
    print(f"Volume history: {volume}")
    print("✓ Volume history passed")


def test_search():
    """Test search endpoint."""
    print("\n=== Testing Search ===")

    # Create workouts with distinct names
    requests.post(
        f"{BASE_URL}/workouts",
        json={
            "exercise": "Squat",
            "sets": 4,
            "reps": 8,
            "weight": 100.0,
            "unit": "kg",
            "date": "2026-04-05",
        },
        headers=get_headers(),
    )

    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "Squat", "limit": 10},
        headers=get_headers(),
    )
    assert response.status_code == 200
    results = response.json()
    print(f"Search results: {results}")
    assert results["count"] > 0
    print("✓ Search passed")


def test_export():
    """Test export endpoint."""
    print("\n=== Testing Export ===")

    response = requests.post(
        f"{BASE_URL}/export", json={"format": "json"}, headers=get_headers()
    )
    assert response.status_code == 200
    result = response.json()
    print(f"Export result: {result}")
    assert result["status"] == "success"
    print("✓ Export passed")


def test_presets():
    """Test exercise presets."""
    print("\n=== Testing Presets ===")

    # Create preset
    preset_data = {
        "name": "Chest Day",
        "sets": 4,
        "reps": "8-12",
        "weight": 80.0,
        "notes": "My favorite chest workout",
    }
    response = requests.post(
        f"{BASE_URL}/presets", json=preset_data, headers=get_headers()
    )
    assert response.status_code == 201
    preset = response.json()
    print(f"Created preset: {preset}")
    preset_id = preset["id"]

    # Get presets
    response = requests.get(f"{BASE_URL}/presets", headers=get_headers())
    assert response.status_code == 200
    presets = response.json()
    print(f"Found {len(presets)} presets")

    # Update preset
    response = requests.put(
        f"{BASE_URL}/presets/{preset_id}", json={"sets": 5}, headers=get_headers()
    )
    assert response.status_code == 200

    # Delete preset
    response = requests.delete(
        f"{BASE_URL}/presets/{preset_id}", headers=get_headers()
    )
    assert response.status_code == 204
    print("✓ Presets passed")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Fitness Tracker API Tests")
    print("=" * 50)

    if not wait_for_server():
        print("\n❌ Server not available. Start it with: uvicorn app:app --reload")
        sys.exit(1)

    tests = [
        test_health,
        test_workouts,
        test_stats,
        test_search,
        test_export,
        test_presets,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
