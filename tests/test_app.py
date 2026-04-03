import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activity_data():
    """Restore activity state after each test so tests stay isolated."""
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_success():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity in data
    assert "participants" in data[expected_activity]
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "Activity not found"


def test_signup_already_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test_student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "not_signed_up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Student not signed up for this activity"
