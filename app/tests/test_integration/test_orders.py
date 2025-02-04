def test_deny_access_unauthorized(client):
    response = client.get("/orders/")

    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    expected_detail = {"detail": "Not authenticated"}
    assert (
        response.json() == expected_detail
    ), f"Expected {expected_detail}, got {response.json()}"
