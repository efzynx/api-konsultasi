#!/usr/bin/env python3
"""
Production API Test Script
Run this script to test your deployed API endpoints
"""
import json
import sys
from datetime import datetime

import requests


class APITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.session = requests.Session()

    def test_health_check(self):
        """Test health check endpoint"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_register(self):
        """Test user registration"""
        print("🔍 Testing user registration...")
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "password": "testpassword123",
            "nama": "Test User Production",
            "nim": "123456789",
            "role": "mahasiswa",
        }

        try:
            response = self.session.post(
                f"{self.base_url}/register",
                json=test_user,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 201:
                print("✅ User registration successful")
                self.test_user = test_user
                return True
            else:
                print(
                    f"❌ Registration failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

    def test_login(self):
        """Test user login"""
        print("🔍 Testing user login...")
        if not hasattr(self, "test_user"):
            print("❌ No test user available for login")
            return False

        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],
        }

        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "access_token" in data:
                    self.token = data["access_token"]
                    print("✅ Login successful")
                    return True
                else:
                    print(f"❌ Login failed: Invalid response format")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def test_protected_endpoint(self):
        """Test protected endpoint with JWT token"""
        print("🔍 Testing protected endpoint...")
        if not self.token:
            print("❌ No token available for protected endpoint test")
            return False

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            response = self.session.get(f"{self.base_url}/profile", headers=headers)

            if response.status_code == 200:
                print("✅ Protected endpoint access successful")
                return True
            else:
                print(
                    f"❌ Protected endpoint failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
            return False

    def test_dosen_list(self):
        """Test dosen list endpoint (public)"""
        print("🔍 Testing dosen list...")
        try:
            response = self.session.get(f"{self.base_url}/dosen")

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(
                        f"✅ Dosen list retrieved successfully ({len(data.get('data', []))} records)"
                    )
                    return True
                else:
                    print("❌ Dosen list failed: Invalid response format")
                    return False
            else:
                print(f"❌ Dosen list failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Dosen list error: {e}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting API tests for: {self.base_url}")
        print("=" * 50)

        tests = [
            self.test_health_check,
            self.test_dosen_list,
            self.test_register,
            self.test_login,
            self.test_protected_endpoint,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1
            print()

        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check your deployment.")
            return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_production.py <your-api-url>")
        print("Example: python test_production.py https://your-domain.com")
        sys.exit(1)

    api_url = sys.argv[1]
    tester = APITester(api_url)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
