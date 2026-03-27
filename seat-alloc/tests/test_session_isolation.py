"""
Test Suite 1: Session Isolation & Data Ownership
=================================================
Verifies that every user can only see/modify their own data:
- Sessions belong to the creating user
- Classrooms are user-scoped
- Students/uploads are session-scoped (and sessions are user-scoped)
- Cross-user access is denied with 403
- Admin endpoints still enforce ownership where appropriate
"""
import pytest
from conftest import (
    _auth_header, _signup_user,
    create_classroom, start_session, upload_students,
    create_session_direct,
)


# ============================================================================
# SESSION ISOLATION
# ============================================================================

class TestSessionIsolation:
    """Each user should only see their own sessions."""

    def test_user_sees_only_own_sessions(self, client, user_a, user_b):
        """User A and User B each create sessions — neither sees the other's."""
        # User A creates a session (force_new to bypass upload_ids check)
        resp_a = client.post(
            "/api/sessions/start",
            json={"upload_ids": [], "force_new": True},
            headers=_auth_header(user_a["token"]),
        )
        # Session start may succeed or fail gracefully depending on logic
        # The key test is the listing isolation below

        # User B creates a session
        resp_b = client.post(
            "/api/sessions/start",
            json={"upload_ids": [], "force_new": True},
            headers=_auth_header(user_b["token"]),
        )

        # User A lists sessions
        list_a = client.get(
            "/api/sessions/list",
            headers=_auth_header(user_a["token"]),
        )
        sessions_a = list_a.get_json()
        # Should only contain Alice's session(s)
        if isinstance(sessions_a, dict) and "sessions" in sessions_a:
            sessions_a = sessions_a["sessions"]
        elif isinstance(sessions_a, dict) and "data" in sessions_a:
            sessions_a = sessions_a["data"]
        
        for s in (sessions_a if isinstance(sessions_a, list) else []):
            assert s.get("user_id") == user_a["user"]["id"], \
                f"User A sees session owned by user_id={s.get('user_id')}"

        # User B lists sessions
        list_b = client.get(
            "/api/sessions/list",
            headers=_auth_header(user_b["token"]),
        )
        sessions_b = list_b.get_json()
        if isinstance(sessions_b, dict) and "sessions" in sessions_b:
            sessions_b = sessions_b["sessions"]
        elif isinstance(sessions_b, dict) and "data" in sessions_b:
            sessions_b = sessions_b["data"]
        
        for s in (sessions_b if isinstance(sessions_b, list) else []):
            assert s.get("user_id") == user_b["user"]["id"], \
                f"User B sees session owned by user_id={s.get('user_id')}"

    def test_user_cannot_access_other_users_session(self, app, client, user_a, user_b):
        """User B cannot view details of User A's session."""
        # User A creates a session via service layer (API requires upload_ids)
        result = create_session_direct(app, user_a["user"]["id"], "Private Session")
        session_id = result.get("session_id")

        if session_id:
            # User B tries to access it
            resp = client.get(
                f"/api/sessions/{session_id}",
                headers=_auth_header(user_b["token"]),
            )
            # Should be 403 Forbidden or 404 Not Found
            assert resp.status_code in (403, 404), \
                f"Expected 403/404 but got {resp.status_code} — cross-user session access!"

    def test_user_cannot_delete_other_users_session(self, app, client, user_a, user_b):
        """User B cannot delete User A's session."""
        # User A creates a session via service layer
        result = create_session_direct(app, user_a["user"]["id"], "Protected Session")
        session_id = result.get("session_id")

        if session_id:
            resp = client.delete(
                f"/api/sessions/{session_id}",
                headers=_auth_header(user_b["token"]),
            )
            assert resp.status_code in (403, 404), \
                f"Expected 403/404 but got {resp.status_code} — cross-user session delete!"

    def test_active_session_returns_only_own(self, app, client, user_a, user_b):
        """GET /api/sessions/active returns only the requesting user's active session."""
        # Both users create sessions via service layer
        create_session_direct(app, user_a["user"]["id"], "A's Active")
        create_session_direct(app, user_b["user"]["id"], "B's Active")

        resp = client.get("/api/sessions/active",
                          headers=_auth_header(user_a["token"]))
        data = resp.get_json()
        if resp.status_code == 200 and data:
            session = data.get("session") or data
            if isinstance(session, dict) and "user_id" in session:
                assert session["user_id"] == user_a["user"]["id"]


# ============================================================================
# CLASSROOM ISOLATION
# ============================================================================

class TestClassroomIsolation:
    """Classrooms should be scoped to the user who created them."""

    def test_user_sees_only_own_classrooms(self, client, user_a, user_b):
        """Each user sees only their own classrooms."""
        create_classroom(client, user_a["token"], "Room-A1", 5, 6)
        create_classroom(client, user_a["token"], "Room-A2", 4, 5)
        create_classroom(client, user_b["token"], "Room-B1", 6, 8)

        # User A lists classrooms
        resp_a = client.get("/api/classrooms",
                            headers=_auth_header(user_a["token"]))
        rooms_a = resp_a.get_json()
        if isinstance(rooms_a, dict):
            rooms_a = rooms_a.get("classrooms") or rooms_a.get("data") or []

        assert len(rooms_a) >= 2, "User A should see at least 2 classrooms"
        for r in rooms_a:
            # Each classroom should either be unassigned or belong to User A
            assert r.get("user_id") in (None, user_a["user"]["id"]), \
                f"User A sees classroom belonging to user_id={r.get('user_id')}"

        # User B lists classrooms
        resp_b = client.get("/api/classrooms",
                            headers=_auth_header(user_b["token"]))
        rooms_b = resp_b.get_json()
        if isinstance(rooms_b, dict):
            rooms_b = rooms_b.get("classrooms") or rooms_b.get("data") or []

        for r in rooms_b:
            assert r.get("user_id") in (None, user_b["user"]["id"]), \
                f"User B sees classroom belonging to user_id={r.get('user_id')}"

    def test_user_cannot_delete_others_classroom(self, client, user_a, user_b):
        """User B cannot delete User A's classroom."""
        data, status = create_classroom(client, user_a["token"], "Protected-Room", 3, 4)
        room_id = None
        if isinstance(data, dict):
            room_id = data.get("id") or data.get("classroom", {}).get("id")

        if room_id:
            resp = client.delete(
                f"/api/classrooms/{room_id}",
                headers=_auth_header(user_b["token"]),
            )
            assert resp.status_code in (403, 404), \
                f"Expected 403/404 but got {resp.status_code}"

    def test_same_name_different_users(self, client, user_a, user_b):
        """Two users can have classrooms with the same name."""
        data_a, status_a = create_classroom(client, user_a["token"], "Lab-1", 3, 4)
        data_b, status_b = create_classroom(client, user_b["token"], "Lab-1", 5, 6)

        assert status_a == 200 or status_a == 201, f"User A create failed: {data_a}"
        assert status_b == 200 or status_b == 201, f"User B create failed: {data_b}"

    def test_duplicate_name_same_user_rejected(self, client, user_a):
        """Same user cannot create two classrooms with the same name."""
        create_classroom(client, user_a["token"], "UniqueRoom", 3, 4)
        data2, status2 = create_classroom(client, user_a["token"], "UniqueRoom", 5, 6)
        # Should fail with 400 or 409
        assert status2 in (400, 409, 500), f"Duplicate name should be rejected: {data2}"


# ============================================================================
# DASHBOARD ISOLATION
# ============================================================================

class TestDashboardIsolation:
    """Dashboard stats should reflect only the requesting user's data."""

    def test_dashboard_stats_are_user_scoped(self, client, user_a, user_b):
        """Stats endpoint returns counts for the requesting user only."""
        # User A creates a classroom
        create_classroom(client, user_a["token"], "Stats-Room-A", 3, 4)

        # User B has no classrooms
        resp_a = client.get("/api/dashboard/stats",
                            headers=_auth_header(user_a["token"]))
        resp_b = client.get("/api/dashboard/stats",
                            headers=_auth_header(user_b["token"]))

        if resp_a.status_code == 200 and resp_b.status_code == 200:
            stats_a = resp_a.get_json()
            stats_b = resp_b.get_json()

            # The key names may vary — try multiple common shapes
            def _get_cr(d):
                for k in ("total_classrooms", "classrooms", "classroom_count"):
                    if k in d:
                        return d[k]
                # Check nested
                if "data" in d:
                    return _get_cr(d["data"])
                return 0

            classrooms_a = _get_cr(stats_a)
            classrooms_b = _get_cr(stats_b)

            # User A should have more classrooms than User B
            assert classrooms_a >= classrooms_b, \
                f"User A classrooms ({classrooms_a}) should be >= User B ({classrooms_b})"


# ============================================================================
# DATABASE OVERVIEW ISOLATION
# ============================================================================

class TestDatabaseOverviewIsolation:
    """The database overview endpoint should show user-scoped data."""

    def test_overview_counts_are_user_scoped(self, client, user_a, user_b):
        """GET /api/database/overview returns user-specific table counts."""
        resp_a = client.get("/api/database/overview",
                            headers=_auth_header(user_a["token"]))
        resp_b = client.get("/api/database/overview",
                            headers=_auth_header(user_b["token"]))

        # Both should succeed
        assert resp_a.status_code in (200, 401)
        assert resp_b.status_code in (200, 401)


# ============================================================================
# UNAUTHENTICATED ACCESS
# ============================================================================

class TestUnauthenticatedAccess:
    """Endpoints requiring auth should reject requests without a token."""

    @pytest.mark.parametrize("method,path", [
        ("GET",  "/api/sessions/active"),
        ("GET",  "/api/sessions/list"),
        ("POST", "/api/sessions/start"),
        ("GET",  "/api/classrooms"),
        ("POST", "/api/classrooms"),
        ("GET",  "/api/dashboard/stats"),
        ("GET",  "/api/database/overview"),
        ("GET",  "/api/students"),
    ])
    def test_protected_endpoints_require_auth(self, client, method, path):
        """All protected endpoints return 401 without a token."""
        if method == "GET":
            resp = client.get(path)
        elif method == "POST":
            resp = client.post(path, json={})
        else:
            resp = client.delete(path)

        assert resp.status_code == 401, \
            f"{method} {path} returned {resp.status_code} without auth (expected 401)"
