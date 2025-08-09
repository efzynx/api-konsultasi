"""
Comprehensive API Testing Script for Flask-RESTX Implementation
Tests all endpoints, authentication, CRUD operations, and edge cases
"""

import requests
import json
import time
from datetime import datetime


class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []

    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        self.test_results.append(result)
        print(f"{result['timestamp']} - {result['status']} {test_name}")
        if details:
            print(f"    Details: {details}")

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.api_base}/auth/health")
            success = response.status_code == 200
            data = response.json() if success else None
            self.log_test(
                "Health Check", success, f"Status: {response.status_code}, Data: {data}"
            )
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration endpoint"""
        test_user = {
            "username": f"testuser_{int(time.time())}",
            "password": "testpassword123",
            "nama": "Test User",
            "nim": "123456789",
            "role": "mahasiswa",
        }

        try:
            response = self.session.post(
                f"{self.api_base}/auth/register", json=test_user
            )
            success = response.status_code in [200, 201]
            data = response.json() if response.content else None
            self.log_test(
                "User Registration",
                success,
                f"Status: {response.status_code}, Data: {data}",
            )
            return success, test_user
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False, None

    def test_dosen_registration_and_login(self):
        """Test dosen registration and login for testing restricted endpoints"""
        # First create a regular user
        test_dosen_user = {
            "username": f"testdosen_{int(time.time())}",
            "password": "dosenpassword123",
            "nama": "Test Dosen User",
            "nim": None,
            "role": "dosen",
        }

        try:
            # Register dosen user
            response = self.session.post(
                f"{self.api_base}/auth/register", json=test_dosen_user
            )
            if response.status_code in [200, 201]:
                # Manually update user role to dosen (since registration defaults to mahasiswa)
                # This would normally be done by admin

                # Login as dosen
                login_data = {
                    "username": test_dosen_user["username"],
                    "password": test_dosen_user["password"],
                }

                login_response = self.session.post(
                    f"{self.api_base}/auth/login", json=login_data
                )
                if login_response.status_code == 200:
                    login_data_response = login_response.json()
                    if (
                        "data" in login_data_response
                        and "access_token" in login_data_response["data"]
                    ):
                        dosen_token = login_data_response["data"]["access_token"]
                        self.log_test(
                            "Dosen Registration & Login", True, "Dosen token obtained"
                        )
                        return True, dosen_token

            self.log_test(
                "Dosen Registration & Login", False, "Failed to create dosen user"
            )
            return False, None
        except Exception as e:
            self.log_test("Dosen Registration & Login", False, f"Exception: {str(e)}")
            return False, None

    def test_user_login(self, user_data):
        """Test user login endpoint"""
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }

        try:
            response = self.session.post(f"{self.api_base}/auth/login", json=login_data)
            success = response.status_code == 200
            data = response.json() if success else None

            if success and data and "data" in data and "access_token" in data["data"]:
                self.auth_token = data["data"]["access_token"]
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )

            self.log_test(
                "User Login",
                success,
                f"Status: {response.status_code}, Token received: {bool(self.auth_token)}",
            )
            return success
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False

    def test_protected_endpoint(self, endpoint, method="GET", data=None):
        """Test a protected endpoint with authentication"""
        try:
            # Ensure endpoint ends with / for Flask-RESTX
            if not endpoint.endswith("/"):
                endpoint += "/"

            if method == "GET":
                response = self.session.get(f"{self.api_base}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{self.api_base}{endpoint}", json=data)
            elif method == "PUT":
                response = self.session.put(f"{self.api_base}{endpoint}", json=data)
            elif method == "DELETE":
                response = self.session.delete(f"{self.api_base}{endpoint}")

            success = response.status_code in [200, 201, 204]
            response_data = response.json() if response.content else None
            self.log_test(
                f"{method} {endpoint}", success, f"Status: {response.status_code}"
            )
            return success, response_data
        except Exception as e:
            self.log_test(f"{method} {endpoint}", False, f"Exception: {str(e)}")
            return False, None

    def test_dosen_endpoints(self):
        """Test all dosen endpoints"""
        print("\n🧑‍🏫 Testing Dosen Endpoints...")

        # Test GET /dosen (list all)
        self.test_protected_endpoint("/dosen")

        # Test POST /dosen (create)
        dosen_data = {
            "nama_dosen": "Dr. Test Dosen",
            "mata_kuliah": "Test Subject",
            "username": f"dosen_{int(time.time())}",
            "password": "dosenpassword123",
        }
        success, response_data = self.test_protected_endpoint(
            "/dosen", "POST", dosen_data
        )

        # If creation successful, test update and delete
        if success and response_data and "data" in response_data:
            dosen_id = response_data["data"].get("id")
            if dosen_id:
                # Test PUT /dosen/<id> (update)
                update_data = {"mata_kuliah": "Updated Subject"}
                self.test_protected_endpoint(f"/dosen/{dosen_id}", "PUT", update_data)

                # Test DELETE /dosen/<id>
                self.test_protected_endpoint(f"/dosen/{dosen_id}", "DELETE")

    def test_booking_endpoints(self):
        """Test all booking endpoints"""
        print("\n📅 Testing Booking Endpoints...")

        # Test GET /booking (list)
        self.test_protected_endpoint("/booking")

        # Test POST /booking (create)
        booking_data = {
            "nama_mahasiswa": "Test Student",
            "nim": "987654321",
            "dosen_id": 1,
            "tanggal": "2024-12-31",
            "jam": "14:00:00",
            "topik_konsultasi": "Test consultation topic",
        }
        success, response_data = self.test_protected_endpoint(
            "/booking", "POST", booking_data
        )

        # If creation successful, test update and delete
        if success and response_data and "data" in response_data:
            booking_id = response_data["data"].get("id")
            if booking_id:
                # Test PUT /booking/<id> (update)
                update_data = {"topik_konsultasi": "Updated consultation topic"}
                self.test_protected_endpoint(
                    f"/booking/{booking_id}", "PUT", update_data
                )

                # Test DELETE /booking/<id>
                self.test_protected_endpoint(f"/booking/{booking_id}", "DELETE")

    def test_user_endpoints(self):
        """Test all user endpoints"""
        print("\n👤 Testing User Endpoints...")

        # Test GET /user/me (should work for any authenticated user)
        self.test_protected_endpoint("/user/me")

        # Test dosen-only endpoints with mahasiswa token (should fail)
        self.test_protected_endpoint("/user/all")
        self.test_protected_endpoint("/user/mahasiswa")

        # Test dosen-only endpoints with dosen token
        print("\n👨‍🏫 Testing Dosen-Only User Endpoints...")
        dosen_success, dosen_token = self.test_dosen_registration_and_login()
        if dosen_success and dosen_token:
            # Temporarily switch to dosen token
            original_auth = self.session.headers.get("Authorization")
            self.session.headers.update({"Authorization": f"Bearer {dosen_token}"})

            # Test dosen endpoints
            success1, _ = self.test_protected_endpoint("/user/all")
            success2, _ = self.test_protected_endpoint("/user/mahasiswa")

            if success1:
                self.log_test("GET /user/all (as dosen)", True, "Status: 200")
            if success2:
                self.log_test("GET /user/mahasiswa (as dosen)", True, "Status: 200")

            # Restore original token
            if original_auth:
                self.session.headers.update({"Authorization": original_auth})

    def test_profile_endpoints(self):
        """Test all profile endpoints"""
        print("\n👤 Testing Profile Endpoints...")

        # Test GET /profile
        self.test_protected_endpoint("/profile")

        # Test PUT /profile (update)
        profile_data = {"nama": "Updated Test User"}
        self.test_protected_endpoint("/profile", "PUT", profile_data)

        # Test PUT /profile/change-password
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newtestpassword123",
        }
        self.test_protected_endpoint("/profile/change-password", "PUT", password_data)

    def test_error_scenarios(self):
        """Test error scenarios and edge cases"""
        print("\n🚨 Testing Error Scenarios...")

        # Test unauthorized access (without token)
        temp_headers = self.session.headers.copy()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            response = self.session.get(f"{self.api_base}/user/me/")
            success = response.status_code == 401
            self.log_test(
                "Unauthorized Access", success, f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Exception: {str(e)}")

        # Restore headers
        self.session.headers.update(temp_headers)

        # Test invalid data
        invalid_user = {"username": "", "password": ""}
        try:
            response = self.session.post(
                f"{self.api_base}/auth/register", json=invalid_user
            )
            success = response.status_code in [400, 422]
            self.log_test(
                "Invalid Registration Data", success, f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Invalid Registration Data", False, f"Exception: {str(e)}")

    def test_swagger_documentation(self):
        """Test Swagger documentation endpoints"""
        print("\n📚 Testing Documentation Endpoints...")

        # Test Swagger UI
        try:
            response = self.session.get(f"{self.api_base}/docs/")
            success = response.status_code == 200
            self.log_test("Swagger UI", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Swagger UI", False, f"Exception: {str(e)}")

        # Test OpenAPI spec
        try:
            response = self.session.get(f"{self.api_base}/swagger.json")
            success = response.status_code == 200
            if success:
                spec = response.json()
                endpoints_count = sum(
                    len(methods) for methods in spec.get("paths", {}).values()
                )
                self.log_test(
                    "OpenAPI Specification",
                    success,
                    f"Status: {response.status_code}, Endpoints: {endpoints_count}",
                )
            else:
                self.log_test(
                    "OpenAPI Specification", success, f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("OpenAPI Specification", False, f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 60)

        # Test basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed. Server may not be running.")
            return False

        # Test authentication flow
        print("\n🔐 Testing Authentication Flow...")
        reg_success, user_data = self.test_user_registration()
        if reg_success and user_data:
            login_success = self.test_user_login(user_data)
            if not login_success:
                print("❌ Login failed. Cannot test protected endpoints.")
                return False
        else:
            print("❌ Registration failed. Cannot proceed with authentication tests.")
            return False

        # Test all endpoint categories
        self.test_dosen_endpoints()
        self.test_booking_endpoints()
        self.test_user_endpoints()
        self.test_profile_endpoints()

        # Test error scenarios
        self.test_error_scenarios()

        # Test documentation
        self.test_swagger_documentation()

        # Print summary
        self.print_test_summary()

        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")

        print("\n🎉 Testing Complete!")


if __name__ == "__main__":
    tester = APITester()
    tester.run_comprehensive_tests()
