import pytest


@pytest.mark.anyio
async def test_get_activities(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = await client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    first = data["Chess Club"]
    assert expected_keys.issubset(set(first.keys()))
    assert isinstance(first["participants"], list)


@pytest.mark.anyio
async def test_signup_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    refresh = await client.get("/activities")
    assert email in refresh.json()[activity_name]["participants"]


@pytest.mark.anyio
async def test_signup_activity_duplicate(client):
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # Act
    first = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    duplicate = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert first.status_code == 200
    assert duplicate.status_code == 400
    assert "already signed up" in duplicate.json()["detail"].lower()


@pytest.mark.anyio
async def test_signup_activity_full(client):
    # Arrange
    activity_name = "Gym Class"

    # Fill activity to capacity (30 total participants, 2 prefilled)
    for i in range(28):
        resp = await client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"fill{i}@mergington.edu"}
        )
        assert resp.status_code == 200

    # Act
    overflow = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"}
    )

    # Assert
    assert overflow.status_code == 400
    assert "full" in overflow.json()["detail"].lower()


@pytest.mark.anyio
async def test_unregister_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = await client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    result = await client.get("/activities")
    assert email not in result.json()[activity_name]["participants"]


@pytest.mark.anyio
async def test_unregister_missing(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notfound@mergington.edu"

    # Act
    response = await client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()
