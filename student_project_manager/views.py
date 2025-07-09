from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from api.models import Project, ProjectParticipant

class LeaveProjectView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        try:
            participant = project.participants.get(user=request.user)
            participant.delete()
            messages.success(request, 'Вы вышли из проекта.')
        except ProjectParticipant.DoesNotExist:
            messages.warning(request, 'Вы не участвуете в этом проекте.')
        return redirect('dashboard')
