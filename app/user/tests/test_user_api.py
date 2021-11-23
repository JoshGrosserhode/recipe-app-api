from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users api (Public)"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with valid payload is successful"""
        payload = {
            "email": "test@test.com",
            "password": "testpass",
            "name": "Test Name",
        }

        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))

        # check to make sure that the raw password is not returned in the res data
        self.assertNotIn("password", res.data)

    def test_user_exsits(self):
        """Test creating a user that already exsists"""
        payload = {
            "email": "test@test.com",
            "password": "testpass",
            "name": "User Name",
        }
        create_user(**payload)

        res = self.client.post(path=CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 chars"""
        payload = {
            "email": "test@test.com",
            "password": "pw",
            "name": "User Name",
        }

        res = self.client.post(path=CREATE_USER_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check to make sure that the user was never created
        user_exists = (
            get_user_model()
            .objects.filter(
                email=payload["email"],
            )
            .exists()
        )
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@test.com",
            "password": "pw",
            "name": "User Name",
        }
        create_user(**payload)

        res = self.client.post(path=TOKEN_URL, data=payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(
            email="test@test.com", password="test123", name="Test Name"
        )
        payload = {
            "email": "test@test.com",
            "password": "wrong",
            "name": "Test Name",
        }

        res = self.client.post(path=TOKEN_URL, data=payload)

        # should not include token because a user with that email already exists
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = {
            "email": "test@test.com",
            "password": "testpass",
            "name": "Test Name",
        }
        res = self.client.post(path=TOKEN_URL, data=payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_token(self):
        """Test that email and password are required"""
        payload = {
            "email": "test@test.com",
            "password": "",
        }
        res = self.client.post(path=TOKEN_URL, data=payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
