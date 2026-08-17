from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.users.models import User

from .tokens import password_reset_token


class AuthenticationFlowTests(APITestCase):
    def test_register_creates_company_and_admin_user(self):
        response = self.client.post('/api/auth/register/', {
            'company_name': 'Acme Corp',
            'email': 'admin@acme.test',
            'password': 'SuperSecret123!',
            'first_name': 'Ada',
            'last_name': 'Admin',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        user = User.objects.get(email='admin@acme.test')
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertEqual(user.company.name, 'Acme Corp')

    def test_register_rejects_duplicate_email(self):
        company = Company.objects.create(name='Existing Co', email='existing@co.test')
        User.objects.create_user(email='dup@co.test', password='pass1234', company=company)

        response = self.client.post('/api/auth/register/', {
            'company_name': 'New Co',
            'email': 'dup@co.test',
            'password': 'SuperSecret123!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens_and_user_payload(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        response = self.client.post('/api/auth/login/', {'email': 'user@acme.test', 'password': 'pass1234'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'user@acme.test')

    def test_login_rejects_wrong_password(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        response = self.client.post('/api/auth/login/', {'email': 'user@acme.test', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        self.client.force_authenticate(user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@acme.test')

    def test_change_password_rejects_wrong_current_password(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        self.client.force_authenticate(user)
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'wrong', 'new_password': 'BrandNewPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_succeeds_and_updates_login(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        self.client.force_authenticate(user)
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'pass1234', 'new_password': 'BrandNewPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(None)
        login = self.client.post('/api/auth/login/', {'email': 'user@acme.test', 'password': 'BrandNewPass123!'})
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_forgot_password_returns_generic_response_for_unknown_email(self):
        response = self.client.post('/api/auth/forgot-password/', {'email': 'nobody@nowhere.test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_with_valid_token(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)

        response = self.client.post('/api/auth/reset-password/', {
            'uid': uid, 'token': token, 'new_password': 'BrandNewPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        login = self.client.post('/api/auth/login/', {'email': 'user@acme.test', 'password': 'BrandNewPass123!'})
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_reset_password_with_invalid_token_is_rejected(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.post('/api/auth/reset-password/', {
            'uid': uid, 'token': 'not-a-real-token', 'new_password': 'BrandNewPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklists_refresh_token(self):
        company = Company.objects.create(name='Acme Corp', email='acme@co.test')
        user = User.objects.create_user(email='user@acme.test', password='pass1234', company=company)

        login = self.client.post('/api/auth/login/', {'email': 'user@acme.test', 'password': 'pass1234'})
        refresh = login.data['refresh']

        self.client.force_authenticate(user)
        logout_response = self.client.post('/api/auth/logout/', {'refresh': refresh})
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post('/api/auth/refresh/', {'refresh': refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
