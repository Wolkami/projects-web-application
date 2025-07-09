from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Project, Task, Comment, FileAttachment, ProjectParticipant

class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'group')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['start_date'].input_formats = ['%Y-%m-%d']
        self.fields['end_date'].input_formats = ['%Y-%m-%d']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date', 'assignee']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['due_date'].input_formats = ['%Y-%m-%d']

        # Удаляем поле assignee, если не создатель проекта
        if user and project and user != project.creator:
            self.fields.pop('assignee')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите комментарий...',
                'class': 'form-control',
            }),
        }
        labels = {
            'content': '',
        }

class TaskFileForm(forms.ModelForm):
    class Meta:
        model = FileAttachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'file': 'Выберите файл',
        }

class AddParticipantForm(forms.ModelForm):
    class Meta:
        model = ProjectParticipant
        fields = ['user', 'role']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # получаем проект из представления
        super().__init__(*args, **kwargs)

        if project:
            # Исключаем уже добавленных участников
            existing_ids = project.participants.values_list('user_id', flat=True)
            self.fields['user'].queryset = CustomUser.objects.exclude(id__in=existing_ids)

        # Красота для Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
