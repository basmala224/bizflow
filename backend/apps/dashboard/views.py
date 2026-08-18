from datetime import date, datetime, time

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


def _last_n_months(n):
    """Returns the last n (year, month) tuples ending with the current month."""
    today = date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        company_scoped = user.role != User.Role.SUPER_ADMIN

        projects = Project.objects.all()
        tasks = Task.objects.all()
        employees = User.objects.exclude(role=User.Role.SUPER_ADMIN)
        if company_scoped:
            projects = projects.filter(company_id=user.company_id)
            tasks = tasks.filter(company_id=user.company_id)
            employees = employees.filter(company_id=user.company_id)

        kpis = {
            'projects_total': projects.count(),
            'projects_active': projects.filter(
                status__in=[Project.Status.PLANNED, Project.Status.IN_PROGRESS]
            ).count(),
            'tasks_total': tasks.count(),
            'tasks_completed': tasks.filter(status=Task.Status.DONE).count(),
            'employees_total': employees.count(),
        }

        projects_by_status = [
            {'status': choice, 'label': label, 'count': projects.filter(status=choice).count()}
            for choice, label in Project.Status.choices
        ]

        months = _last_n_months(6)
        start_year, start_month = months[0]
        range_start = make_aware(datetime.combine(date(start_year, start_month, 1), time.min))
        completed_by_month = {
            row['month'].strftime('%Y-%m'): row['count']
            for row in (
                tasks.filter(status=Task.Status.DONE, updated_at__gte=range_start)
                .annotate(month=TruncMonth('updated_at'))
                .values('month')
                .annotate(count=Count('id'))
            )
        }
        tasks_completed_by_month = [
            {'month': f'{year:04d}-{month:02d}', 'count': completed_by_month.get(f'{year:04d}-{month:02d}', 0)}
            for year, month in months
        ]

        employee_performance = list(
            tasks.filter(status=Task.Status.DONE, assigned_to__isnull=False)
            .values('assigned_to', 'assigned_to__first_name', 'assigned_to__last_name')
            .annotate(completed_tasks=Count('id'))
            .order_by('-completed_tasks')[:5]
        )
        employee_performance = [
            {
                'user_id': row['assigned_to'],
                'name': f"{row['assigned_to__first_name']} {row['assigned_to__last_name']}".strip(),
                'completed_tasks': row['completed_tasks'],
            }
            for row in employee_performance
        ]

        return Response({
            'kpis': kpis,
            'projects_by_status': projects_by_status,
            'tasks_completed_by_month': tasks_completed_by_month,
            'employee_performance': employee_performance,
        })
