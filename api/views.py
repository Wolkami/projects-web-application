from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Project, Task, Comment, FileAttachment
from .permissions import IsProjectParticipantOrCreator, IsTaskProjectParticipant
from .serializers import (
    ProjectSerializer, TaskSerializer,
    CommentSerializer, FileAttachmentSerializer
)

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
        serializer.save(creator=self.request.user)

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
