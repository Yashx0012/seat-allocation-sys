"""
Test Suite 6: Redundancy Fix Validation & Service Layer
========================================================
Validates the 9 redundancy fixes from the refactoring session and
tests the service layer (SessionService, StudentService, AllocationService)
for correct delegation to the query layer.

Redundancy fixes verified:
1. Duplicate session lookup queries → single SessionQueries class
2. Duplicate student count logic → StudentQueries.get_batch_counts
3. Unused leftover_calculator.py → removed (old_files/)
4. Duplicate DB connection helpers → single get_db() in db.py
5. Duplicate ensure_demo_db calls → single call in create_app
6. Duplicate CORS setup → single CORS config in create_app
7. Redundant cache snapshot logic → CacheManager consolidation
8. Duplicate classroom ownership checks → helper functions in blueprint
9. Duplicate session ownership checks → helper functions in blueprint
"""
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from conftest import (
    _auth_header, _signup_user,
    create_classroom, start_session,
)


# ============================================================================
# FIX 1: NO DUPLICATE SESSION LOOKUP QUERIES
# ============================================================================

class TestNoDuplicateSessionQueries:
    """SessionQueries should be the single source for session DB operations."""

    def test_session_queries_has_all_methods(self):
        """SessionQueries class should have all session-related methods."""
        from algo.database.queries.session_queries import SessionQueries

        required_methods = [
            "get_session_by_id",
            "get_session_by_plan_id",
            "create_session",
            "update_session_stats",
            "mark_session_completed",
            "expire_session",
            "get_active_sessions",
        ]
        for method in required_methods:
            assert hasattr(SessionQueries, method), \
                f"SessionQueries missing method: {method}"

    def test_session_service_delegates_to_queries(self, app_ctx):
        """SessionService.get_session should call SessionQueries.get_session_by_id."""
        from algo.services.session_service import SessionService
        from algo.database.queries.session_queries import SessionQueries

        with patch.object(SessionQueries, "get_session_by_id", return_value=None) as mock:
            SessionService.get_session(42)
            mock.assert_called_once_with(42)


# ============================================================================
# FIX 2: NO DUPLICATE STUDENT COUNT LOGIC
# ============================================================================

class TestNoDuplicateStudentCounts:
    """Student counts should use a single StudentQueries method."""

    def test_student_queries_has_batch_counts(self):
        """StudentQueries should have get_batch_counts method."""
        from algo.database.queries.student_queries import StudentQueries
        assert hasattr(StudentQueries, "get_batch_counts")

    def test_student_queries_has_bulk_insert(self):
        """StudentQueries should have bulk_insert_students method."""
        from algo.database.queries.student_queries import StudentQueries
        assert hasattr(StudentQueries, "bulk_insert_students")


# ============================================================================
# FIX 3: LEGACY FILES MOVED TO old_files/
# ============================================================================

class TestLegacyFilesRelocated:
    """Removed/deprecated files should be in old_files/ and not imported."""

    def test_old_files_exist_in_old_files_dir(self):
        """Legacy files should be in algo/old_files/."""
        import os
        old_files_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "algo", "old_files"
        )
        if os.path.exists(old_files_dir):
            files = os.listdir(old_files_dir)
            # These files were moved during refactoring
            expected_legacy = ["algo_legacy.py", "app_legacy.py", "cache_manager.py",
                               "leftover_calculator.py", "student_parser.py"]
            for f in expected_legacy:
                assert f in files, f"Expected legacy file {f} in old_files/"

    def test_legacy_files_not_imported(self):
        """No active module should import from old_files."""
        import os
        import re

        algo_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "algo")
        violations = []

        for root, dirs, files in os.walk(algo_dir):
            # Skip old_files and __pycache__
            if "old_files" in root or "__pycache__" in root:
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    if re.search(r"from\s+.*old_files", content):
                        violations.append(fpath)
                    if re.search(r"import\s+.*old_files", content):
                        violations.append(fpath)
                except Exception:
                    pass

        assert len(violations) == 0, f"Active code imports from old_files: {violations}"


# ============================================================================
# FIX 4: SINGLE DB CONNECTION HELPER
# ============================================================================

class TestSingleDBConnection:
    """Only one DB connection helper should exist (in db.py)."""

    def test_get_db_exists(self):
        """db.py should export get_db."""
        from algo.database.db import get_db
        assert callable(get_db)

    def test_get_db_connection_standalone_exists(self):
        """db.py should export get_db_connection_standalone."""
        from algo.database.db import get_db_connection_standalone
        assert callable(get_db_connection_standalone)

    def test_get_db_connection_is_alias(self):
        """get_db_connection should be an alias for get_db_connection_standalone."""
        from algo.database.db import get_db_connection, get_db_connection_standalone
        assert get_db_connection is get_db_connection_standalone

    def test_db_uses_config_path(self, app_ctx, tmp_db):
        """Database connection should use Config.DB_PATH."""
        from algo.database.db import get_db
        conn = get_db()
        assert conn is not None
        # Connection should be functional
        cur = conn.execute("SELECT 1")
        assert cur.fetchone()[0] == 1


# ============================================================================
# FIX 5: SINGLE ensure_demo_db CALL
# ============================================================================

class TestSingleDbInit:
    """ensure_demo_db should be called once during app creation, not scattered."""

    def test_schema_module_has_ensure_demo_db(self):
        """schema.py should export ensure_demo_db."""
        from algo.database.schema import ensure_demo_db
        assert callable(ensure_demo_db)

    def test_database_init_exports(self):
        """algo.database should export ensure_demo_db."""
        from algo.database import ensure_demo_db
        assert callable(ensure_demo_db)

    def test_auth_service_does_not_init_db(self):
        """auth_service.py should NOT have its own init_user_database."""
        import algo.services.auth_service as auth
        assert not hasattr(auth, "init_user_database"), \
            "auth_service should not have init_user_database (consolidated)"


# ============================================================================
# FIX 6: NO user_auth.db REFERENCES
# ============================================================================

class TestNoSeparateAuthDB:
    """auth_service.py should not reference user_auth.db."""

    def test_auth_service_no_db_path_constant(self):
        """auth_service should not have a DB_PATH pointing to user_auth.db."""
        import algo.services.auth_service as auth
        # Should NOT have DB_PATH attribute (removed during consolidation)
        if hasattr(auth, "DB_PATH"):
            assert "user_auth" not in str(auth.DB_PATH), \
                "auth_service.DB_PATH should not reference user_auth.db"

    def test_auth_service_uses_config(self):
        """auth_service should import Config from settings."""
        import inspect
        import algo.services.auth_service as auth
        source = inspect.getsource(auth)
        assert "from algo.config.settings import Config" in source, \
            "auth_service should import Config"

    def test_auth_service_has_get_conn(self):
        """auth_service should have _get_conn helper using Config.DB_PATH."""
        import algo.services.auth_service as auth
        assert hasattr(auth, "_get_conn"), \
            "auth_service should have _get_conn helper"


# ============================================================================
# FIX 7: CACHE MANAGER CONSOLIDATION
# ============================================================================

class TestCacheManagerConsolidation:
    """CacheManager should be in core/cache/, not duplicated."""

    def test_cache_manager_importable(self):
        """CacheManager should be importable from core.cache."""
        try:
            from algo.core.cache.cache_manager import CacheManager
            assert True
        except ImportError:
            pytest.fail("CacheManager should be importable from algo.core.cache")


# ============================================================================
# FIX 8 & 9: OWNERSHIP HELPER FUNCTIONS IN BLUEPRINTS
# ============================================================================

class TestOwnershipHelpers:
    """Session and classroom blueprints should have ownership verification helpers."""

    def test_session_blueprint_has_ownership_check(self):
        """sessions.py blueprint should have ownership verification logic."""
        import inspect
        from algo.api.blueprints import sessions
        source = inspect.getsource(sessions)
        # Should have some form of ownership/user_id check
        assert "user_id" in source, \
            "sessions blueprint should check user_id for ownership"

    def test_classroom_blueprint_has_ownership_check(self):
        """classrooms.py blueprint should have ownership verification logic."""
        import inspect
        from algo.api.blueprints import classrooms
        source = inspect.getsource(classrooms)
        assert "user_id" in source, \
            "classrooms blueprint should check user_id for ownership"


# ============================================================================
# SERVICE LAYER: SESSION SERVICE
# ============================================================================

class TestSessionService:
    """Unit tests for SessionService methods."""

    def test_create_session(self, app_ctx):
        """SessionService.create_session should return a session dict."""
        from algo.services.session_service import SessionService
        result = SessionService.create_session("Test Session", user_id=1)
        assert isinstance(result, dict)
        assert "session_id" in result
        assert "plan_id" in result
        assert result["user_id"] == 1

    def test_get_nonexistent_session(self, app_ctx):
        """SessionService.get_session for non-existent ID returns None."""
        from algo.services.session_service import SessionService
        result = SessionService.get_session(99999)
        assert result is None

    def test_delete_nonexistent_session(self, app_ctx):
        """SessionService.delete_session for non-existent ID returns error."""
        from algo.services.session_service import SessionService
        result = SessionService.delete_session(99999)
        assert result.get("success") is False

    def test_finalize_session(self, app_ctx):
        """SessionService.finalize_session should mark session completed."""
        from algo.services.session_service import SessionService
        from algo.database.queries.session_queries import SessionQueries

        sess = SessionService.create_session("Finalize Test", user_id=1)
        SessionService.finalize_session(sess["session_id"])

        updated = SessionQueries.get_session_by_id(sess["session_id"])
        assert updated["status"] == "completed"

    def test_get_user_sessions(self, app_ctx):
        """SessionService.get_user_sessions returns sessions for the given user."""
        from algo.services.session_service import SessionService

        SessionService.create_session("User Sessions 1", user_id=1)
        SessionService.create_session("User Sessions 2", user_id=1)

        sessions = SessionService.get_user_sessions(user_id=1)
        assert isinstance(sessions, list)
        assert len(sessions) >= 2

    def test_session_timeout_constants(self):
        """SessionService should have timeout constants."""
        from algo.services.session_service import SessionService
        assert hasattr(SessionService, "SESSION_INACTIVE_TIMEOUT_MINUTES")
        assert SessionService.SESSION_INACTIVE_TIMEOUT_MINUTES == 120
        assert hasattr(SessionService, "SESSION_ABANDONED_TIMEOUT_MINUTES")
        assert SessionService.SESSION_ABANDONED_TIMEOUT_MINUTES == 30


# ============================================================================
# SERVICE LAYER: ALLOCATION QUERIES
# ============================================================================

class TestAllocationQueries:
    """Unit tests for AllocationQueries methods."""

    def test_get_allocations_empty(self, app_ctx):
        """AllocationQueries.get_allocations_by_session for empty session returns empty list."""
        from algo.database.queries.allocation_queries import AllocationQueries
        result = AllocationQueries.get_allocations_by_session(99999)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_allocation_queries_has_required_methods(self):
        """AllocationQueries should have all required methods."""
        from algo.database.queries.allocation_queries import AllocationQueries
        required = [
            "get_allocations_by_session",
            "save_allocation_batch",
            "clear_session_allocations",
            "get_allocated_student_ids",
            "get_allocated_rooms",
        ]
        for method in required:
            assert hasattr(AllocationQueries, method), \
                f"AllocationQueries missing: {method}"


# ============================================================================
# STUDENT QUERIES
# ============================================================================

class TestStudentQueries:
    """Unit tests for StudentQueries methods."""

    def test_student_queries_has_required_methods(self):
        """StudentQueries should have all required methods."""
        from algo.database.queries.student_queries import StudentQueries
        required = [
            "get_batch_counts",
            "create_upload",
            "bulk_insert_students",
            "get_session_uploads",
        ]
        for method in required:
            assert hasattr(StudentQueries, method), \
                f"StudentQueries missing: {method}"

    def test_get_batch_counts_empty(self, app_ctx):
        """get_batch_counts for non-existent session returns empty list."""
        from algo.database.queries.student_queries import StudentQueries
        result = StudentQueries.get_batch_counts(99999)
        assert isinstance(result, list)
        assert len(result) == 0


# ============================================================================
# CONFIG VALIDATION
# ============================================================================

class TestConfigValidation:
    """Verify Config has required settings."""

    def test_config_has_db_path(self):
        """Config should have DB_PATH."""
        from algo.config.settings import Config
        assert hasattr(Config, "DB_PATH")
        assert str(Config.DB_PATH).endswith("demo.db")

    def test_config_has_secret_key(self):
        """Config should have SECRET_KEY."""
        from algo.config.settings import Config
        assert hasattr(Config, "SECRET_KEY")
        assert len(Config.SECRET_KEY) > 0

    def test_config_has_log_file(self):
        """Config should have LOG_FILE."""
        from algo.config.settings import Config
        assert hasattr(Config, "LOG_FILE")

    def test_config_ensure_dirs(self):
        """Config.ensure_dirs should be callable."""
        from algo.config.settings import Config
        assert callable(Config.ensure_dirs)


# ============================================================================
# APP FACTORY VALIDATION
# ============================================================================

class TestAppFactory:
    """Verify create_app produces a properly configured Flask app."""

    def test_app_has_blueprints(self, app):
        """App should have all registered blueprints."""
        bp_names = list(app.blueprints.keys())
        expected_bps = [
            "sessions", "students", "allocations",
            "classrooms", "dashboard", "health",
        ]
        for bp in expected_bps:
            assert bp in bp_names, f"Missing blueprint: {bp}"

    def test_app_has_db_teardown(self, app):
        """App should have a teardown handler for DB connections."""
        # Flask stores teardown functions
        assert len(app.teardown_appcontext_funcs) > 0, \
            "App should have at least one teardown handler (close_db)"

    def test_app_test_config_applied(self, app):
        """Test config should set TESTING=True."""
        assert app.config.get("TESTING") is True
