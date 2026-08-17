from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.users.models import User


class UserTenantIsolationTests(APITestCase):
    """Cahier des charges §26: cross-tenant user data must never leak,
    even when a user of Company A guesses another company's user IDs."""

    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', email='a@company.test')
        self.company_b = Company.objects.create(name='Company B', email='b@company.test')

        self.admin_a = User.objects.create_user(
            email='admin@a.test', password='pass1234', role=User.Role.ADMIN, company=self.company_a,
        )
        self.employee_a = User.objects.create_user(
            email='employee@a.test', password='pass1234', role=User.Role.EMPLOYEE, company=self.company_a,
        )
        self.manager_a = User.objects.create_user(
            email='manager@a.test', password='pass1234', role=User.Role.MANAGER, company=self.company_a,
        )
        self.admin_b = User.objects.create_user(
            email='admin@b.test', password='pass1234', role=User.Role.ADMIN, company=self.company_b,
        )

    def test_admin_lists_only_own_company_users(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = {u['email'] for u in response.data['results']}
        self.assertEqual(emails, {'admin@a.test', 'employee@a.test', 'manager@a.test'})

    def test_admin_cannot_retrieve_other_companys_user(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get(f'/api/users/{self.admin_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_other_companys_user(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.patch(f'/api/users/{self.admin_b.id}/', {'first_name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.admin_b.refresh_from_db()
        self.assertNotEqual(self.admin_b.first_name, 'Hacked')

    def test_admin_can_create_user_in_own_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/users/', {
            'email': 'new@a.test', 'password': 'BrandNew123!', 'role': User.Role.EMPLOYEE,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(email='new@a.test')
        self.assertEqual(created.company_id, self.company_a.id)

    def test_employee_cannot_create_user(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.post('/api/users/', {
            'email': 'sneaky@a.test', 'password': 'BrandNew123!', 'role': User.Role.EMPLOYEE,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_cannot_delete_user(self):
        self.client.force_authenticate(self.manager_a)
        response = self.client.delete(f'/api/users/{self.employee_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_users(self):
        # Per the cahier des charges, only Admins/Managers/Super Admins can
        # browse the user directory — employees only see their own profile
        # via /api/auth/me/.
        self.client.force_authenticate(self.employee_a)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_list_users(self):
        self.client.force_authenticate(self.manager_a)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_sees_every_user(self):
        super_admin = User.objects.create_user(
            email='root@bizflow.test', password='pass1234', role=User.Role.SUPER_ADMIN, is_staff=True, is_superuser=True,
        )
        self.client.force_authenticate(super_admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)  # 4 from setUp + this super admin
