from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    # HTML-интерфейс
    dashboard_view,
    create_project_view,
    project_detail_view,
    edit_project_view,
    delete_project_view,
    UserRegisterView,

    # API
    ProjectListCreateView, ProjectDetailView,
    TaskListCreateView, TaskDetailView,
    CommentCreateView,
    FileUploadView,
    ProjectParticipantListCreateView, ProjectParticipantUpdateDeleteView,
    LeaveProjectView,
    RegisterView, ChangePasswordView,
)

urlpatterns = [
    # Аутентификация HTML
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),

    # Главная страница (после входа)
    path('', dashboard_view, name='dashboard'),

    # API авторизация
    path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
    path('api/auth/register/', RegisterView.as_view(), name='api-register'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='api-change-password'),

    # Проекты
    path('api/projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('api/projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/view/', project_detail_view, name='project-view'),
    path('projects/<int:pk>/edit/', edit_project_view, name='edit-project'),
    path('projects/<int:pk>/delete/', delete_project_view, name='delete-project'),


    path('projects/create/', create_project_view, name='create-project'),

    # Участники проектов
    path('api/projects/<int:project_id>/participants/', ProjectParticipantListCreateView.as_view(), name='project-participants'),
    path('api/participants/<int:pk>/', ProjectParticipantUpdateDeleteView.as_view(), name='participant-detail'),
    path('api/projects/<int:project_id>/leave/', LeaveProjectView.as_view(), name='leave-project'),

    # Задачи
    path('api/tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('api/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Комментарии
    path('api/comments/', CommentCreateView.as_view(), name='comment-create'),

    # Файлы
    path('api/files/', FileUploadView.as_view(), name='file-upload'),
]
