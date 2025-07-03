from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    # HTML-интерфейс
    dashboard_view,
    UserRegisterView,

    create_project_view,
    project_detail_view,
    edit_project_view,
    delete_project_view,
    project_tasks_view,

    project_participants_view,
    remove_participant_view,

    create_task_view,
    edit_task_view,
    delete_task_view,
    task_detail_view,
    update_task_status_view,

    # API
    ProjectListCreateView, ProjectDetailView,
    TaskListCreateView, TaskDetailView,
    CommentCreateView,
    FileUploadView,
    ProjectParticipantListCreateView, ProjectParticipantUpdateDeleteView,
    LeaveProjectView,
    RegisterView, ChangePasswordView,
)

from api.forms import BootstrapAuthenticationForm

urlpatterns = [
    # Аутентификация HTML
    path(
        'login/',
        LoginView.as_view(template_name='registration/login.html', authentication_form=BootstrapAuthenticationForm),
        name='login'
    ),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', UserRegisterView.as_view(template_name='registration/register.html'), name='register'),

    # Главная страница (после входа)
    path('', dashboard_view, name='dashboard'),

    # API авторизация
    path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
    path('api/auth/register/', RegisterView.as_view(), name='api-register'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='api-change-password'),

    # Проекты
    path('api/projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('api/projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    path('projects/create/', create_project_view, name='create-project'),
    path('projects/<int:pk>/view/', project_detail_view, name='project-view'),
    path('projects/<int:pk>/edit/', edit_project_view, name='edit-project'),
    path('projects/<int:pk>/delete/', delete_project_view, name='delete-project'),
    path('projects/<int:project_id>/tasks/all/', project_tasks_view, name='project-tasks'),

    path('projects/<int:project_id>/tasks/create/', create_task_view, name='create-task'),
    path('projects/<int:project_id>/participants/', project_participants_view, name='project-participants'),
    path('participants/<int:pk>/remove/', remove_participant_view, name='remove-participant'),

    # Участники проектов
    path('api/projects/<int:project_id>/participants/', ProjectParticipantListCreateView.as_view(), name='api-project-participants'),
    path('api/participants/<int:pk>/', ProjectParticipantUpdateDeleteView.as_view(), name='api-participant-detail'),
    path('api/projects/<int:project_id>/leave/', LeaveProjectView.as_view(), name='api-leave-project'),

    # Задачи
    path('api/tasks/', TaskListCreateView.as_view(), name='api-task-list'),
    path('api/tasks/<int:pk>/', TaskDetailView.as_view(), name='api-task-detail'),

    path('tasks/<int:task_id>/edit/', edit_task_view, name='edit-task'),
    path('tasks/<int:task_id>/delete/', delete_task_view, name='delete-task'),
    path('tasks/<int:task_id>/', task_detail_view, name='task-detail-view'),
    path('tasks/<int:task_id>/status/', update_task_status_view, name='update-task-status'),

    # Комментарии
    path('api/comments/', CommentCreateView.as_view(), name='api-comment-create'),

    # Файлы
    path('api/files/', FileUploadView.as_view(), name='api-file-upload'),
]
