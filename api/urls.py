from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),

    path('tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

    path('comments/', views.CommentCreateView.as_view(), name='comment-create'),

    path('files/', views.FileUploadView.as_view(), name='file-upload'),
]

# Token
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns += [
    path('auth/token/', obtain_auth_token, name='api-token-auth'),
]