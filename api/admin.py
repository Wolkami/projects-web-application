from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, ProjectParticipant

# Register your models here.

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