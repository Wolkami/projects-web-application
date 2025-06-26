from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import CustomUser, Project, ProjectParticipant, Task, Comment, FileAttachment

# Пользователь
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'group']

# Проект
class ProjectSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'creator', 'start_date', 'end_date', 'status', 'created_at']

# Участник проекта
class ProjectParticipantSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = ProjectParticipant
        fields = ['id', 'project', 'user', 'role']
        extra_kwargs = {
            'project': {'required': False},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user = instance.user
        rep['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'group': user.group,
        }
        return rep

# Задача
class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assignee', 'status', 'due_date', 'created_at']

    def validate(self, data):
        request = self.context['request']
        user = request.user
        project = data.get('project')

        # 1. Проверяем, имеет ли право пользователь создавать задачи в этом проекте
        is_creator = (project.creator == user)
        is_participant = ProjectParticipant.objects.filter(project=project, user=user).exists()

        if not (is_creator or is_participant):
            raise serializers.ValidationError("Вы не являетесь участником проекта.")

        # 2. Проверяем, что assignee — участник того же проекта
        assignee = data.get('assignee')
        if assignee and not ProjectParticipant.objects.filter(project=project, user=assignee).exists():
            raise serializers.ValidationError("Назначенный пользователь не состоит в проекте.")

        return data

# Комментарий
class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'content', 'created_at']

# Прикрепленный файл
class FileAttachmentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = FileAttachment
        fields = ['id', 'file', 'user', 'uploaded_at', 'project', 'task']
