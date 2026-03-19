import requests

def test_post_api_rooms_delete_non_existent_room():
    base_url = "http://localhost:8001"
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    non_existent_room_id = "000000000000000000000000"
    url = f"{base_url}/api/rooms/{non_existent_room_id}"

    try:
        response = requests.delete(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request to delete non-existent room failed: {e}"

    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
    try:
        json_response = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    expected_error_message = "Not found."
    # Depending on API error response structure, check message presence
    if isinstance(json_response, dict):
        # Check typical error message keys: "detail", "message", or similar
        error_msg = None
        for key in ["detail", "message", "error"]:
            if key in json_response:
                error_msg = json_response[key]
                break
        assert error_msg == expected_error_message, f"Expected error message '{expected_error_message}', got '{error_msg}'"
    else:
        assert False, "Response JSON is not a dictionary"

test_post_api_rooms_delete_non_existent_room()
