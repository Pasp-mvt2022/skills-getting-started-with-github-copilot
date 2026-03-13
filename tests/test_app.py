import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly games",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce school plays and performances",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "elijah@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["benjamin@mergington.edu", "grace@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities dictionary before each test."""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)


def test_get_activities(client):
    """Test retrieving all activities."""
    # Arrange: No special setup needed as activities are reset by fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and data
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
    assert len(data) == 9  # All activities present


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange: Choose an activity and email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check response and that participant was added
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Verify participant was added
    response_check = client.get("/activities")
    data = response_check.json()
    assert email in data[activity_name]["participants"]


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # Arrange: Use an email already in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: Attempt to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 error
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity."""
    # Arrange: Use invalid activity name
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"

    # Act: Attempt to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity."""
    # Arrange: Choose an activity and existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check response and that participant was removed
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    # Verify participant was removed
    response_check = client.get("/activities")
    data = response_check.json()
    assert email not in data[activity_name]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistration when student is not signed up."""
    # Arrange: Use an email not in the activity
    activity_name = "Chess Club"
    email = "notsigned@mergington.edu"

    # Act: Attempt to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 error
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_activity_not_found(client):
    """Test unregistration from non-existent activity."""
    # Arrange: Use invalid activity name
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"

    # Act: Attempt to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_root_redirect(client):
    """Test that root path redirects to static index."""
    # Arrange: No special setup

    # Act: Make GET request to root without following redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to static page
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"