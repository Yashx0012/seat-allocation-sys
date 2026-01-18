import sys
import os
import unittest
import json

# Ensure we can import the algo package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algo.main import app

class APIIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Verify the health endpoint is alive."""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_recent_plans(self):
        """Verify the recent plans endpoint (requires auth usually, checking if at least reachable)."""
        # Note: Since auth is enabled, this might return 401, which is fine for visibility check
        response = self.app.get('/api/plans/recent')
        # We expect 401 if token_required is working properly
        self.assertIn(response.status_code, [200, 401])

    def test_classrooms(self):
        """Verify classrooms endpoint is reachable."""
        response = self.app.get('/api/classrooms')
        self.assertIn(response.status_code, [200, 401])

if __name__ == "__main__":
    print("🔍 Running API Integrity Tests...")
    unittest.main()
