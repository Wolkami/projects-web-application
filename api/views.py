from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .models import Project, ProjectParticipant, Task, Comment, FileAttachment, CustomUser
from .permissions import IsProjectParticipantOrCreator, IsTaskProjectParticipant
from .serializers import (
    ProjectSerializer, ProjectParticipantSerializer, TaskSerializer,
    CommentSerializer, FileAttachmentSerializer,
    RegisterSerializer, ChangePasswordSerializer,
)
from .forms import CustomUserCreationForm, ProjectForm, TaskForm, CommentForm, TaskFileForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

# Project
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        created = Project.objects.filter(creator=user)
        participating = Project.objects.filter(participants__user=user)
        return (created | participating).distinct()

    def perform_create(self, serializer):
        project = serializer.save(creator=self.request.user)

        # Добавляем автора как участника с ролью lead
        ProjectParticipant.objects.create(
            project=project,
            user=self.request.user,
            role='lead'
        )

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectParticipantOrCreator]

# Task
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            project__participants__user=user
        ).distinct() | Task.objects.filter(
            project__creator=user
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        serializer.save()

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskProjectParticipant]

# Comment
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# FileAttachment
class FileUploadView(generics.ListCreateAPIView):
    queryset = FileAttachment.objects.all()
    serializer_class = FileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ProjectParticipant
class ProjectParticipantListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(pk=project_id)

        # Проверка прав доступа
        user = self.request.user
        if not (user == project.creator or ProjectParticipant.objects.filter(project=project, user=user).exists()):
            raise PermissionDenied("Нет доступа к проекту.")

        return ProjectParticipant.objects.filter(project=project)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.kwargs['project_id']
        project = Project.objects.get(pk=project_id)
        context.update({'project': project})
        return context

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(pk=project_id)

        user = self.request.user
        if project.creator != user:
            raise PermissionDenied("Только автор проекта может добавлять участников.")

        serializer.save(project=project)

class ProjectParticipantUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectParticipant.objects.all()
    serializer_class = ProjectParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        project = serializer.instance.project
        if self.request.user != project.creator:
            raise PermissionDenied("Только автор проекта может менять роли.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.project.creator:
            raise PermissionDenied("Только автор проекта может удалять участников.")
        instance.delete()

class LeaveProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, project_id):
        user = request.user
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Проект не найден."}, status=status.HTTP_404_NOT_FOUND)

        if project.creator == user:
            return Response({"detail": "Создатель проекта не может выйти из проекта."}, status=status.HTTP_400_BAD_REQUEST)

        participant = ProjectParticipant.objects.filter(project=project, user=user).first()

        if participant:
            participant.delete()
            return Response({"detail": "Вы успешно вышли из проекта."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Вы не являетесь участником проекта."}, status=status.HTTP_400_BAD_REQUEST)

# Регистрация и смена пароля
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": "Неверный текущий пароль."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'api/register.html'
    success_url = reverse_lazy('login')

@login_required
def dashboard_view(request):
    user = request.user

    created_projects = Project.objects.filter(creator=user)
    joined_projects = Project.objects.filter(participants__user=user).exclude(creator=user)

    context = {
        'created_projects': created_projects,
        'joined_projects': joined_projects,
    }

    return render(request, 'api/dashboard.html', context)

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            messages.success(request, 'Проект успешно создан.')
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'api/create_project.html', {'form': form})

@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.creator != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект обновлён.')
            return redirect('project-view', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'api/edit_project.html', {'form': form, 'project': project})

@login_required
def delete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.creator != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Проект удалён.')
        return redirect('dashboard')

    return render(request, 'api/delete_project.html', {'project': project})

@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Только участники или создатель могут смотреть
    if project.creator != request.user and not project.participants.filter(user=request.user).exists():
        return redirect('dashboard')

    tasks = Task.objects.filter(project=project)

    context = {
        'project': project,
        'tasks_todo': tasks.filter(status=Task.Status.TODO),
        'tasks_in_progress': tasks.filter(status=Task.Status.IN_PROGRESS),
        'tasks_done': tasks.filter(status=Task.Status.DONE),
    }

    return render(request, 'api/project_detail.html', context)

@login_required
def project_participants_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Только автор проекта может управлять участниками
    if project.creator != request.user:
        return redirect('dashboard')

    participants = project.participants.select_related('user')

    # Добавление участника
    if request.method == 'POST':
        username = request.POST.get('username')
        user = CustomUser.objects.filter(username=username).first()

        if not user:
            messages.error(request, f'Пользователь "{username}" не найден.')
        elif user == project.creator:
            messages.warning(request, 'Создатель уже является участником.')
        elif project.participants.filter(user=user).exists():
            messages.warning(request, 'Пользователь уже в проекте.')
        else:
            ProjectParticipant.objects.create(project=project, user=user)
            messages.success(request, f'Пользователь {username} добавлен.')

        return redirect('project-participants', project_id=project.id)

    return render(request, 'api/project_participants.html', {
        'project': project,
        'participants': participants,
    })

@login_required
def remove_participant_view(request, pk):
    participant = get_object_or_404(ProjectParticipant, pk=pk)

    # Только автор проекта может удалять
    if participant.project.creator != request.user:
        return redirect('dashboard')

    participant.delete()
    messages.success(request, f'Участник {participant.user.username} удалён.')
    return redirect('project-participants', project_id=participant.project.pk)

@login_required
def create_task_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = TaskForm(request.POST or None, user=request.user, project=project)

    # Только участники или автор проекта могут создавать задачи
    if project.creator != request.user and not project.participants.filter(user=request.user).exists():
        return redirect('dashboard')

    if request.method == 'POST':
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.creator = request.user
            task.save()
            messages.success(request, 'Задача создана.')
            return redirect('project-view', pk=project.pk)

    return render(request, 'api/create_task.html', {'form': form, 'project': project})

@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    form = TaskForm(request.POST or None, instance=task, user=request.user, project=project)

    # Только автор проекта или исполнитель может редактировать
    if request.user != project.creator and request.user != task.assignee:
        return redirect('project-view', pk=project.pk)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача обновлена.')
            return redirect('project-view', pk=project.pk)

    return render(request, 'api/edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project

    # Только создатель проекта или исполнитель может удалить задачу
    if request.user != project.creator and request.user != task.assignee:
        return redirect('project-view', pk=project.pk)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача удалена.')
        return redirect('project-view', pk=project.pk)

    return render(request, 'api/delete_task.html', {'task': task})

@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project

    if request.user != project.creator and not project.participants.filter(user=request.user).exists():
        return redirect('dashboard')

    comment_form = CommentForm()
    file_form = TaskFileForm()

    if request.method == 'POST':
        if 'content' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен.')
                return redirect('task-detail-view', task_id=task.id)

        elif 'file' in request.FILES:
            file_form = TaskFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                uploaded_file = file_form.save(commit=False)
                uploaded_file.task = task
                uploaded_file.uploaded_by = request.user
                uploaded_file.save()
                messages.success(request, 'Файл успешно загружен.')
                return redirect('task-detail-view', task_id=task.id)

    comments = task.comments.select_related('author')
    files = task.files.select_related('uploaded_by')

    return render(request, 'api/task_detail.html', {
        'task': task,
        'comments': comments,
        'form': comment_form,
        'file_form': file_form,
        'files': files,
    })

@require_POST
@login_required
def update_task_status_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project

    # Только автор проекта или исполнитель может менять статус
    if request.user != project.creator and request.user != task.assignee:
        return redirect('task-detail-view', task_id=task.id)

    new_status = request.POST.get('status')
    if new_status in dict(Task.Status.choices).keys():
        task.status = new_status
        task.save()
        messages.success(request, 'Статус обновлён.')

    return redirect('task-detail-view', task_id=task.id)

@login_required
def project_tasks_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Только участники или создатель проекта
    if request.user != project.creator and not project.participants.filter(user=request.user).exists():
        return redirect('dashboard')

    tasks = project.tasks.select_related('assignee').all()

    # Фильтрация по статусу (через ?status=done и т.п.)
    status_filter = request.GET.get('status')
    if status_filter in [choice[0] for choice in Task.Status.choices]:
        tasks = tasks.filter(status=status_filter)

    return render(request, 'api/project_tasks.html', {
        'project': project,
        'tasks': tasks,
        'status_filter': status_filter,
        'Task': Task,
    })
