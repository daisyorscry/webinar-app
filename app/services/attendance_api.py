from datetime import datetime
import requests


class AttendanceAPIError(Exception):
    pass


def _parse_payload(payload: dict) -> dict:
    data = payload.get("data") if isinstance(payload, dict) else None
    if data is None:
        data = payload
    if not isinstance(data, dict):
        raise AttendanceAPIError("Invalid JSON structure from attendance API")

    participant_id = data.get("participant_id") or data.get("id") or data.get("user_id")
    name = data.get("name") or data.get("full_name")
    email = data.get("email")
    status = data.get("status") or data.get("attendance_status") or "unknown"
    attended_at_raw = data.get("attended_at") or data.get("checked_in_at")

    attended_at = None
    if attended_at_raw:
        try:
            attended_at = datetime.fromisoformat(attended_at_raw.replace("Z", "+00:00"))
        except ValueError:
            attended_at = None

    if not participant_id or not name or not email:
        raise AttendanceAPIError("Missing required fields from attendance API")

    return {
        "participant_id": str(participant_id),
        "name": name,
        "email": email,
        "attendance_status": status,
        "attended_at": attended_at,
    }


def _mock_response(identifier_type: str, identifier_value: str) -> dict:
    now = datetime.utcnow()
    return {
        "participant_id": "WB-" + identifier_value.upper().replace("@", "-"),
        "name": "Mock Participant",
        "email": identifier_value if identifier_type == "email" else "mock@example.com",
        "attendance_status": "present",
        "attended_at": now,
    }


def fetch_attendance(api_url: str, api_key: str, identifier_type: str, identifier_value: str, use_mock: bool) -> dict:
    if use_mock:
        return _mock_response(identifier_type, identifier_value)

    if not api_url:
        raise AttendanceAPIError("ATTENDANCE_API_URL is not configured")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    params = {identifier_type: identifier_value}

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
    except requests.RequestException as exc:
        raise AttendanceAPIError(f"Attendance API request failed: {exc}") from exc

    if response.status_code != 200:
        raise AttendanceAPIError(f"Attendance API error: {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise AttendanceAPIError("Attendance API did not return JSON") from exc

    return _parse_payload(payload)
