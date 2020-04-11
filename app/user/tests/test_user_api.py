from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """test the users api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test creating with valid payload"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'password123',
            'name': 'Test Test',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test creating user already exists fails"""
        payload = {'email': 'test@gmail.com', 'password': 'password123'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test is pw is less than 5"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'Test Test',
            }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload[
            'email'
            ]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test that a token is created for user"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'test test'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """test token is not created if invalid credentials"""
        create_user(
            email='test@gmail.com',
            password='password123',
            name="test test"
        )
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrong',
            'name': 'test test'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test that token is not created"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'test test'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test email pw required"""
        res = self.client.post(TOKEN_URL, {'email': 'wrong', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
