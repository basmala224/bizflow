from django.contrib import admin

from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'status', 'priority', 'manager', 'progress')
    list_filter = ('status', 'priority', 'company')
    search_fields = ('name',)
    inlines = (ProjectMemberInline,)
