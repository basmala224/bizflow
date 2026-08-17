from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.projects.models import Project, ProjectMember
from apps.users.models import User


class ProjectTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', email='a@company.test')
        self.company_b = Company.objects.create(name='Company B', email='b@company.test')

        self.admin_a = User.objects.create_user(email='admin@a.test', password='pass1234', role=User.Role.ADMIN, company=self.company_a)
        self.manager_a = User.objects.create_user(email='manager@a.test', password='pass1234', role=User.Role.MANAGER, company=self.company_a)
        self.employee_a = User.objects.create_user(email='employee@a.test', password='pass1234', role=User.Role.EMPLOYEE, company=self.company_a)
        self.other_employee_a = User.objects.create_user(email='other@a.test', password='pass1234', role=User.Role.EMPLOYEE, company=self.company_a)
        self.admin_b = User.objects.create_user(email='admin@b.test', password='pass1234', role=User.Role.ADMIN, company=self.company_b)

        self.project_a = Project.objects.create(name='Website Revamp', company=self.company_a, manager=self.manager_a)
        self.project_b = Project.objects.create(name='Secret Project', company=self.company_b, manager=self.admin_b)
        ProjectMember.objects.create(project=self.project_a, user=self.employee_a, role=ProjectMember.Role.DEVELOPER)

    def test_admin_can_create_project(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/projects/', {
            'name': 'New Project', 'status': Project.Status.PLANNED, 'priority': Project.Priority.HIGH,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(name='New Project')
        self.assertEqual(project.company_id, self.company_a.id)

    def test_manager_cannot_create_project(self):
        self.client.force_authenticate(self.manager_a)
        response = self.client.post('/api/projects/', {'name': 'Nope'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_can_view_own_project_only(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {p['name'] for p in response.data['results']}
        self.assertEqual(names, {'Website Revamp'})

    def test_employee_not_on_project_does_not_see_it(self):
        self.client.force_authenticate(self.other_employee_a)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_manager_sees_all_company_projects(self):
        self.client.force_authenticate(self.manager_a)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_company_b_cannot_see_company_a_project(self):
        self.client.force_authenticate(self.admin_b)
        response = self.client.get(f'/api/projects/{self.project_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_cannot_assign_manager_from_other_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/projects/', {'name': 'Cross Co', 'manager': self.admin_b.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_add_member(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post(
            f'/api/projects/{self.project_a.id}/members/add/',
            {'user': self.other_employee_a.id, 'role': ProjectMember.Role.TESTER},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProjectMember.objects.filter(project=self.project_a, user=self.other_employee_a).exists())

    def test_admin_cannot_add_member_from_other_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post(
            f'/api/projects/{self.project_a.id}/members/add/',
            {'user': self.admin_b.id, 'role': ProjectMember.Role.TESTER},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_cannot_add_member(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.post(
            f'/api/projects/{self.project_a.id}/members/add/',
            {'user': self.other_employee_a.id, 'role': ProjectMember.Role.TESTER},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_remove_member(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.delete(f'/api/projects/{self.project_a.id}/members/{self.employee_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProjectMember.objects.filter(project=self.project_a, user=self.employee_a).exists())

    def test_list_members_endpoint(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get(f'/api/projects/{self.project_a.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_detail']['email'], 'employee@a.test')

    def test_filter_projects_by_status(self):
        Project.objects.create(name='Completed One', company=self.company_a, status=Project.Status.COMPLETED)
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/projects/', {'status': Project.Status.COMPLETED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Completed One')
