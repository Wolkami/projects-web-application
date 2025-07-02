from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

# Пользователи и проекты
from .models import CustomUser, Project, ProjectParticipant

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'group', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'group')}),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date']
    search_fields = ['title', 'description']

@admin.register(ProjectParticipant)
class ProjectParticipantAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role']
    list_filter = ['role']

# Задачи и комментарии
from .models import Task, Comment, FileAttachment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assignee', 'status', 'due_date']
    list_filter = ['status', 'project']
    search_fields = ['title', 'description']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content', 'created_at']
    search_fields = ['content']

@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'task', 'uploaded_at']