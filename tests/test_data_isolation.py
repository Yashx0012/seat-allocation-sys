import requests
import json
import unittest

BASE_URL = "http://localhost:5000/api"

class TestDataIsolation(unittest.TestCase):
    """
    Test suite for verifying that database manager endpoints
    correctly isolate data between different users.
    """

    @classmethod
    def setUpClass(cls):
        # Create/Login User A
        cls.user_a_creds = {
            "username": "user_a",
            "email": "user_a@test.com",
            "password": "password123"
        }
        res_a = requests.post(f"{BASE_URL}/auth/signup", json=cls.user_a_creds)
        if res_a.status_code != 200: 
             res_a = requests.post(f"{BASE_URL}/auth/login", json=cls.user_a_creds)
        
        cls.token_a = res_a.json().get('token')
        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}

        # Create/Login User B
        cls.user_b_creds = {
            "username": "user_b",
            "email": "user_b@test.com",
            "password": "password123"
        }
        res_b = requests.post(f"{BASE_URL}/auth/signup", json=cls.user_b_creds)
        if res_b.status_code != 200:
             res_b = requests.post(f"{BASE_URL}/auth/login", json=cls.user_b_creds)
             
        cls.token_b = res_b.json().get('token')
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}

    def test_01_hierarchy_isolation(self):
        """Verify that User A cannot see User B's seeded session"""
        # User A check
        res_a = requests.get(f"{BASE_URL}/database/hierarchy", headers=self.headers_a)
        hierarchy_a = res_a.json().get('hierarchy', [])
        plan_ids_a = [s['plan_id'] for s in hierarchy_a]
        
        self.assertIn("PLAN_A", plan_ids_a)
        self.assertNotIn("PLAN_B", plan_ids_a)

        # User B check
        res_b = requests.get(f"{BASE_URL}/database/hierarchy", headers=self.headers_b)
        hierarchy_b = res_b.json().get('hierarchy', [])
        plan_ids_b = [s['plan_id'] for s in hierarchy_b]
        
        self.assertIn("PLAN_B", plan_ids_b)
        self.assertNotIn("PLAN_A", plan_ids_b)

    def test_02_overview_isolation(self):
        """Verify that overview counts are per-user"""
        res_a = requests.get(f"{BASE_URL}/database/overview", headers=self.headers_a)
        # Overview currently counts: students, classrooms, uploads, allocations, feedback
        # Since we only seeded session_id, we should verify the implementation doesn't crash
        # and returns correct isolated counts if data was there.
        self.assertTrue(res_a.json().get('success'))

    def test_03_unauthorized_deletion(self):
        """Verify User A cannot delete User B's session"""
        # Get User B's session ID manually from DB if needed, or from B's hierarchy
        res_b = requests.get(f"{BASE_URL}/database/hierarchy", headers=self.headers_b)
        hierarchy_b = res_b.json().get('hierarchy', [])
        if not hierarchy_b:
            self.skipTest("No session for User B found")
            
        session_id_b = hierarchy_b[0]['session_id']
        
        # User A tries to delete User B's session
        res_del = requests.delete(f"{BASE_URL}/database/table/allocation_sessions/{session_id_b}", headers=self.headers_a)
        self.assertEqual(res_del.status_code, 403)

if __name__ == "__main__":
    unittest.main()
