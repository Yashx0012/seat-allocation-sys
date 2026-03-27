"""Quick test: verify auth works against consolidated database."""
import urllib.request
import json
import sys

BASE = "http://127.0.0.1:5000"

def test(label, method, path, body=None, expect_status=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    if body:
        req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        status = resp.status
    except urllib.error.HTTPError as e:
        result = json.loads(e.read())
        status = e.code
    
    ok = (status == expect_status) if expect_status else (200 <= status < 300)
    symbol = "PASS" if ok else "FAIL"
    print(f"  [{symbol}] {label}: HTTP {status} -> {result.get('status', result.get('message', ''))}")
    return ok, result

print("=" * 60)
print("Testing consolidated database...")
print("=" * 60)

all_ok = True

# 1) Health
ok, _ = test("Health check", "GET", "/api/health")
all_ok &= ok

# 2) Login with wrong password (should be 401)
ok, _ = test("Login wrong pass", "POST", "/api/auth/login", 
             {"email": "harshit@gmail.com", "password": "wrong"}, expect_status=401)
all_ok &= ok

# 3) Signup new user
import secrets
test_email = f"test_{secrets.token_hex(2)}@consolidation-test.com"
ok, r = test("Signup new user", "POST", "/api/auth/signup",
             {"username": "consolidation_test", "email": test_email, "password": "Test1234!", "role": "STUDENT"})
all_ok &= ok

if r.get('token'):
    token = r['token']
    
    # 4) Profile with token
    req = urllib.request.Request(BASE + "/api/auth/profile")
    req.add_header('Authorization', f'Bearer {token}')
    try:
        resp = urllib.request.urlopen(req)
        profile = json.loads(resp.read())
        user_email = profile.get('user', {}).get('email', '')
        match = user_email == test_email
        symbol = "PASS" if match else "FAIL"
        print(f"  [{symbol}] Profile fetch: email={user_email}")
        all_ok &= match
    except Exception as e:
        print(f"  [FAIL] Profile fetch: {e}")
        all_ok = False
    
    # 5) Active session (should be empty but not crash)
    req = urllib.request.Request(BASE + "/api/sessions/active")
    req.add_header('Authorization', f'Bearer {token}')
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        print(f"  [PASS] Sessions active: {data.get('success', False)}")
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
        # 404 = no active session, which is fine for a new user
        if e.code in (200, 404):
            print(f"  [PASS] Sessions active: HTTP {e.code} (no active session)")
        else:
            print(f"  [FAIL] Sessions active: HTTP {e.code}")
            all_ok = False
    except Exception as e:
        print(f"  [FAIL] Sessions active: {e}")
        all_ok = False

print("=" * 60)
print(f"Result: {'ALL PASSED' if all_ok else 'SOME FAILED'}")
print("=" * 60)
sys.exit(0 if all_ok else 1)
