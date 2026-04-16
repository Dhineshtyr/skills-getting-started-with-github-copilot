"""
Tests for Mergington High School Activities API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Save and restore activities state before/after each test
    to prevent test cross-contamination
    """
    # Arrange: Save original state
    original = deepcopy(activities)
    
    yield  # Test runs here
    
    # Cleanup: Restore original state
    activities.clear()
    activities.update(original)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Verify GET /activities returns the activity list with proper structure"""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)


class TestSignupForActivity:
    def test_signup_for_activity_success(self, client, reset_activities):
        """Verify a new student can successfully sign up for an activity"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_returns_400(self, client, reset_activities):
        """Verify duplicate signup attempt returns HTTP 400"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Verify signup for non-existent activity returns HTTP 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    def test_unregister_participant_success(self, client, reset_activities):
        """Verify a participant can be successfully removed from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        assert email_to_remove in activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
        assert email_to_remove not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """Verify removing a non-existent participant returns HTTP 404"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Verify unregistering from non-existent activity returns HTTP 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
