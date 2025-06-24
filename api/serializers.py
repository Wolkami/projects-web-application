from rest_framework import serializers

# Пользователь
from .models import CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'group']

# Проект
from .models import Project
class ProjectSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'creator', 'start_date', 'end_date', 'status', 'created_at']

# Участник проекта
from .models import ProjectParticipant
class ProjectParticipantSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = ProjectParticipant
        fields = ['id', 'project', 'user', 'role']

# Задача
from .models import Task
class TaskSerializer(serializers.ModelSerializer):
    assignee = CustomUserSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assignee', 'status', 'due_date', 'created_at']

# Комментарий
from .models import Comment
class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'content', 'created_at']

# Прикрепленный файл
from .models import FileAttachment
class FileAttachmentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = FileAttachment
        fields = ['id', 'file', 'user', 'uploaded_at', 'project', 'task']
