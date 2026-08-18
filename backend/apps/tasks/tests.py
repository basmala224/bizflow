from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Comment, Task
from apps.users.models import User


class TaskTests(APITestCase):
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

        self.task_a = Task.objects.create(
            title='Build homepage', company=self.company_a, project=self.project_a, assigned_to=self.employee_a,
        )
        self.task_b = Task.objects.create(title='Secret task', company=self.company_b, project=self.project_b)

    def test_manager_can_create_task(self):
        self.client.force_authenticate(self.manager_a)
        response = self.client.post('/api/tasks/', {
            'title': 'New task', 'project': self.project_a.id, 'assigned_to': self.employee_a.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title='New task')
        self.assertEqual(task.company_id, self.company_a.id)

    def test_employee_cannot_create_task(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.post('/api/tasks/', {'title': 'Nope', 'project': self.project_a.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_sees_only_own_or_member_project_tasks(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {t['title'] for t in response.data['results']}
        self.assertEqual(titles, {'Build homepage'})

    def test_other_employee_not_on_project_does_not_see_task(self):
        self.client.force_authenticate(self.other_employee_a)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_company_b_cannot_see_company_a_task(self):
        self.client.force_authenticate(self.admin_b)
        response = self.client.get(f'/api/tasks/{self.task_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_task_on_other_company_project(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/tasks/', {'title': 'Cross co', 'project': self.project_b.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_task_to_non_project_member(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post('/api/tasks/', {
            'title': 'Bad assignment', 'project': self.project_a.id, 'assigned_to': self.other_employee_a.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_can_update_status_of_own_task(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.patch(f'/api/tasks/{self.task_a.id}/status/', {'status': Task.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.status, Task.Status.IN_PROGRESS)

    def test_status_endpoint_rejects_invalid_value(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.patch(f'/api/tasks/{self.task_a.id}/status/', {'status': 'NOT_A_STATUS'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_and_list_comments(self):
        self.client.force_authenticate(self.employee_a)
        response = self.client.post(f'/api/tasks/{self.task_a.id}/comments/add/', {'content': 'Looks good'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(task=self.task_a, author=self.employee_a).exists())

        response = self.client.get(f'/api/tasks/{self.task_a.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author_detail']['email'], 'employee@a.test')

    def test_other_employee_not_on_project_cannot_comment(self):
        self.client.force_authenticate(self.other_employee_a)
        response = self.client.post(f'/api/tasks/{self.task_a.id}/comments/add/', {'content': 'Hi'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_tasks_by_status(self):
        Task.objects.create(title='Done task', company=self.company_a, project=self.project_a, status=Task.Status.DONE)
        self.client.force_authenticate(self.admin_a)
        response = self.client.get('/api/tasks/', {'status': Task.Status.DONE})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Done task')
