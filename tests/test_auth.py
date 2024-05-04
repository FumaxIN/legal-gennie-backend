from rest_framework.test import APITestCase

from vendor.models import User


class RegisterTestCase(APITestCase):
    def test_register(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "name": "Test User1",
                "email": "testuser1@example.com",
                "password": "testpass",
                "password2": "testpass"
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="testuser1@example.com").exists())


class LoginTestCase(APITestCase):
    def setUp(self):
        User.objects.create_user(
            name="Test User2",
            email="testuser2@example.com",
            password="testpass",
        )

    def test_login(self):
        response = self.client.post(
            "/api/auth/login",
            {
                "email":    "testuser2@example.com",
                "password": "testpass"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.json())

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/login",
            {
                "email": "testuser2@example.com",
                "password": "wrongtestpass"
            }
        )
        self.assertEqual(response.status_code, 401)
