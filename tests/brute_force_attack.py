import requests
import time
import json


def attempt_login(username, password, base_url="http://localhost:8000"):
    """
    Attempts to log in to the Django authentication API.
    
    :param username: The username to attempt to log in with
    :param password: The password to try
    :param base_url: Base URL of the Django application
    :return: Dictionary with 'success', 'message', and optional 'attempts_remaining'
    """
    login_url = f"{base_url}/api/auth/login/"
    
    try:
        response = requests.post(
            login_url,
            json={
                "username": username,
                "password": password
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            # Successful login
            data = response.json()
            return {
                'success': True,
                'message': 'Login successful',
                'access_token': data.get('access'),
                'refresh_token': data.get('refresh'),
                'user_data': {
                    'user_id': data.get('user_id'),
                    'username': data.get('username'),
                    'email': data.get('email')
                }
            }
        elif response.status_code == 401:
            # Invalid credentials
            return {
                'success': False,
                'message': 'Invalid credentials',
                'status_code': 401
            }
        elif response.status_code == 429:
            # Rate limited (Too Many Requests)
            return {
                'success': False,
                'message': 'Rate limit exceeded',
                'status_code': 429,
                'attempts_remaining': 0
            }
        else:
            # Other error
            return {
                'success': False,
                'message': f'Error: {response.status_code} - {response.text}',
                'status_code': response.status_code
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'Connection refused. Is the server running?',
            'error': 'ConnectionError'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Request timed out',
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'error': type(e).__name__
        }


def brute_force_attack(username, password_list, delay=0.5, base_url="http://localhost:8000"):
    """
    Attempts to brute-force a login using a list of passwords.

    :param username: The username to attempt to log in with
    :param password_list: A list of passwords to try
    :param delay: Delay in seconds between attempts (default: 0.5)
    :param base_url: Base URL of the Django application
    :return: The password if found, None otherwise
    """
    print(f"\n{'='*60}")
    print(f"Starting Brute Force Attack Test")
    print(f"Target: {base_url}/api/auth/login/")
    print(f"Username: {username}")
    print(f"Password list length: {len(password_list)}")
    print(f"Delay between attempts: {delay}s")
    print(f"{'='*60}\n")
    
    successful_password = None
    total_attempts = len(password_list)
    failed_attempts = 0
    rate_limited = False
    
    for i, password in enumerate(password_list, 1):
        print(f"[Attempt {i}/{total_attempts}] Trying password: '{password}'")
        
        result = attempt_login(username, password, base_url)

        if result['success']:
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS! Password found: '{password}'")
            print(f"{'='*60}")
            print(f"User Data:")
            print(json.dumps(result.get('user_data', {}), indent=2))
            successful_password = password
            break
        else:
            failed_attempts += 1
            print(f"  ✗ Login failed: {result['message']}")
            
            if result.get('attempts_remaining') is not None:
                print(f"  ⚠ Attempts remaining: {result['attempts_remaining']}")
            
            if result.get('status_code') == 429:
                rate_limited = True
                print(f"\n{'='*60}")
                print(f"⚠ RATE LIMITED - Server is protecting against brute force!")
                print(f"{'='*60}\n")
                break
            
            if result.get('error') == 'ConnectionError':
                print(f"\n{'='*60}")
                print(f"✗ Cannot connect to server at {base_url}")
                print(f"Please ensure the Django server is running:")
                print(f"  python manage.py runserver")
                print(f"{'='*60}\n")
                break
        
        # Wait before next attempt
        if i < total_attempts:
            time.sleep(delay)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Brute Force Attack Summary")
    print(f"{'='*60}")
    print(f"Total attempts: {i}/{total_attempts}")
    print(f"Failed attempts: {failed_attempts}")
    print(f"Success: {'Yes' if successful_password else 'No'}")
    if successful_password:
        print(f"Found password: {successful_password}")
    if rate_limited:
        print(f"Status: Rate limited (Good - server is protected)")
    print(f"{'='*60}\n")
    
    return successful_password


def test_authentication_api(base_url="http://localhost:8000"):
    """
    Test the authentication API with sample requests.
    
    :param base_url: Base URL of the Django application
    """
    print(f"\n{'='*60}")
    print(f"Testing Authentication API")
    print(f"{'='*60}\n")
    
    # Test 1: Register a new user
    print("Test 1: Registering a new test user...")
    register_url = f"{base_url}/api/auth/register/"
    
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(register_url, json=test_user, timeout=10)
        
        if response.status_code == 201:
            print(f"✓ Registration successful!")
            data = response.json()
            print(f"  Username: {data.get('username')}")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Email: {data.get('email')}")
            
            # Test 2: Login with correct credentials
            print(f"\nTest 2: Login with correct credentials...")
            result = attempt_login(test_user['username'], test_user['password'], base_url)
            
            if result['success']:
                print(f"✓ Login successful!")
                print(f"  Access Token: {result['access_token'][:50]}...")
                
                # Test 3: Try with wrong password (brute force simulation)
                print(f"\nTest 3: Simulating brute force with common passwords...")
                common_passwords = [
                    "password", "123456", "admin", "letmein", "welcome",
                    "qwerty", "abc123", "password1", "iloveyou",
                    "123123", "admin123", "login", "passw0rd",
                    "1234", "12345", "1234567", "12345678",
                    test_user['password']  # Include correct password at the end
                ]
                
                found_password = brute_force_attack(
                    test_user['username'],
                    common_passwords,
                    delay=0.5,
                    base_url=base_url
                )
                
                if found_password:
                    print(f"✓ Brute force test completed - password discovered")
                else:
                    print(f"✗ Brute force test failed or was rate limited")
            else:
                print(f"✗ Login failed: {result['message']}")
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {base_url}")
        print(f"  Please ensure the Django server is running:")
        print(f"    python manage.py runserver")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
    
    print(f"\n{'='*60}\n")


def test_authentication_with_lockout(base_url="http://127.0.0.1:8000", max_failures=5):
    """
    Test the authentication API with lockout after consecutive failures.
    
    :param base_url: Base URL of the Django application
    :param max_failures: Maximum number of consecutive failed attempts before stopping
    """
    print(f"\n{'='*60}")
    print(f"Testing Authentication API with Lockout Protection")
    print(f"Max consecutive failures allowed: {max_failures}")
    print(f"{'='*60}\n")
    
    # Test 1: Register a new user
    print("Test 1: Registering a new test user...")
    register_url = f"{base_url}/api/auth/register/"
    
    test_user = {
        "username": f"lockouttest_{int(time.time())}",
        "email": f"lockout_{int(time.time())}@example.com",
        "password": "SecurePassword456!"
    }
    
    try:
        response = requests.post(register_url, json=test_user, timeout=10)
        
        if response.status_code == 201:
            print(f"✓ Registration successful!")
            data = response.json()
            print(f"  Username: {data.get('username')}")
            print(f"  User ID: {data.get('user_id')}")
            
            # Test 2: Attempt logins with lockout protection
            print(f"\nTest 2: Attempting logins with incorrect passwords...")
            print(f"Will stop after {max_failures} consecutive failures\n")
            
            wrong_passwords = [
                "wrong1", "wrong2", "wrong3", "wrong4", "wrong5",
                "wrong6", "wrong7", "wrong8", "wrong9", "wrong10"
            ]
            
            consecutive_failures = 0
            
            for i, password in enumerate(wrong_passwords, 1):
                if consecutive_failures >= max_failures:
                    print(f"\n{'='*60}")
                    print(f"🛑 LOCKOUT TRIGGERED!")
                    print(f"Stopped after {consecutive_failures} consecutive failures")
                    print(f"{'='*60}\n")
                    break
                
                print(f"[Attempt {i}] Trying password: '{password}'")
                result = attempt_login(test_user['username'], password, base_url)
                
                if result['success']:
                    print(f"  ✓ Login successful (unexpected)")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    print(f"  ✗ Login failed: {result['message']}")
                    print(f"  Consecutive failures: {consecutive_failures}/{max_failures}")
                    
                    if result.get('status_code') == 429:
                        print(f"  ⚠ Rate limited by server")
                        break
                
                time.sleep(0.3)
            
            # Test 3: Verify correct password still works (if not rate limited)
            # if consecutive_failures >= max_failures:
            #     print(f"\nTest 3: Attempting login with correct password after lockout...")
            #     result = attempt_login(test_user['username'], test_user['password'], base_url)
                
            #     if result['success']:
            #         print(f"✓ Correct password accepted")
            #     elif result.get('status_code') == 429:
            #         print(f"⚠ Server rate limit still active (expected)")
            #     else:
            #         print(f"✗ Login failed: {result['message']}")
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {base_url}")
        print(f"  Please ensure the Django server is running:")
        print(f"    python manage.py runserver")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
    
    print(f"\n{'='*60}\n")



if __name__ == "__main__":
    # Run the authentication API test without lockout
    # test_authentication_api()

    # Run the authentication API test with lockout protection
    test_authentication_with_lockout(max_failures=5)
    
    # Or run a custom brute force attack:
    # brute_force_attack(
    #     username="known_username",
    #     password_list=["pass1", "pass2", "pass3", "pass4", "pass5", "pass6", "pass7", "pass8", "pass9", "pass10"],
    #     delay=1.0
    # )

