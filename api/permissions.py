from rest_framework import permissions
from .models import ProjectParticipant

class IsProjectParticipantOrCreator(permissions.BasePermission):
    """
    Разрешает доступ к проекту только его участникам или создателю.
    """

    def has_object_permission(self, request, view, obj):
        if request.user == obj.creator:
            return True

        return ProjectParticipant.objects.filter(project=obj, user=request.user).exists()

class IsTaskProjectParticipant(permissions.BasePermission):
    """
    Доступ к задаче — только если пользователь участвует в проекте задачи.
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project
        if request.user == project.creator:
            return True

        return ProjectParticipant.objects.filter(project=project, user=request.user).exists()
