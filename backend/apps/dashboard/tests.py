from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


class DashboardTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', email='a@company.test')
        self.company_b = Company.objects.create(name='Company B', email='b@company.test')

        self.admin_a = User.objects.create_user(email='admin@a.test', password='pass1234', role=User.Role.ADMIN, company=self.company_a)
        self.employee_a = User.objects.create_user(email='employee@a.test', password='pass1234', role=User.Role.EMPLOYEE, company=self.company_a)
        self.admin_b = User.objects.create_user(email='admin@b.test', password='pass1234', role=User.Role.ADMIN, company=self.company_b)

        self.project_a = Project.objects.create(name='Website', company=self.company_a, status=Project.Status.IN_PROGRESS)
        self.project_b = Project.objects.create(name='Secret', company=self.company_b, status=Project.Status.PLANNED)

        Task.objects.create(title='Task 1', company=self.company_a, project=self.project_a, status=Task.Status.DONE, assigned_to=self.employee_a)
        Task.objects.create(title='Task 2', company=self.company_a, project=self.project_a, status=Task.Status.TODO)
        Task.objects.create(title='Task 3', company=self.company_b, project=self.project_b, status=Task.Status.DONE)

    def test_dashboard_requires_authentication(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_scoped_to_own_company(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['kpis']['projects_total'], 1)
        self.assertEqual(response.data['kpis']['tasks_total'], 2)
        self.assertEqual(response.data['kpis']['tasks_completed'], 1)
        self.assertEqual(response.data['kpis']['employees_total'], 2)

    def test_employee_can_view_own_company_dashboard(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['kpis']['projects_total'], 1)

    def test_projects_by_status_breakdown(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/dashboard/')
        breakdown = {row['status']: row['count'] for row in response.data['projects_by_status']}
        self.assertEqual(breakdown['IN_PROGRESS'], 1)
        self.assertEqual(breakdown['PLANNED'], 0)

    def test_tasks_completed_by_month_includes_current_month(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/dashboard/')
        months = response.data['tasks_completed_by_month']
        self.assertEqual(len(months), 6)
        current_month = date.today().strftime('%Y-%m')
        current_bucket = next(m for m in months if m['month'] == current_month)
        self.assertEqual(current_bucket['count'], 1)

    def test_employee_performance_lists_completer(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/dashboard/')
        performance = response.data['employee_performance']
        self.assertEqual(len(performance), 1)
        self.assertEqual(performance[0]['user_id'], self.employee_a.id)
        self.assertEqual(performance[0]['completed_tasks'], 1)

    def test_company_b_data_not_leaked(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.data['kpis']['tasks_total'], 2)
