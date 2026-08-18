from django.contrib import admin

from .models import Comment, Task


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'project', 'status', 'priority', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'company')
    search_fields = ('title',)
    inlines = (CommentInline,)
