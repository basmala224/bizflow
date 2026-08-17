from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.users.models import User


class CompanyIsolationTests(APITestCase):
    """Cahier des charges §26: a user from Company A must never be able to
    read or write Company B's data, even by guessing IDs directly."""

    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', email='a@company.test')
        self.company_b = Company.objects.create(name='Company B', email='b@company.test')

        self.admin_a = User.objects.create_user(
            email='admin@a.test', password='pass1234', role=User.Role.ADMIN, company=self.company_a,
        )
        self.admin_b = User.objects.create_user(
            email='admin@b.test', password='pass1234', role=User.Role.ADMIN, company=self.company_b,
        )
        self.super_admin = User.objects.create_user(
            email='root@bizflow.test', password='pass1234', role=User.Role.SUPER_ADMIN, is_staff=True, is_superuser=True,
        )

    def test_super_admin_sees_all_companies(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_admin_cannot_list_companies(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_retrieve_own_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get(f'/api/companies/{self.company_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.company_a.id)

    def test_admin_cannot_retrieve_other_companys_data(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get(f'/api/companies/{self.company_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_create_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/companies/', {'name': 'New Co', 'email': 'new@co.test'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_update_other_companys_data(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.patch(f'/api/companies/{self.company_b.id}/', {'name': 'Hacked'})
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.company_b.refresh_from_db()
        self.assertEqual(self.company_b.name, 'Company B')

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
