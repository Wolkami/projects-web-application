from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

# Пользователь
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', _('Студент')
        TEACHER = 'teacher', _('Преподаватель')
        ADMIN = 'admin', _('Администратор')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Роль')
    )

    group = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Группа')
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

# Проект
class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Черновик')
        ACTIVE = 'active', _('Активный')
        COMPLETED = 'completed', _('Завершённый')

    title = models.CharField(max_length=200, verbose_name=_('Название проекта'))
    description = models.TextField(verbose_name=_('Описание проекта'))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name=_('Руководитель проекта')
    )
    start_date = models.DateField(verbose_name=_('Дата начала'))
    end_date = models.DateField(verbose_name=_('Дата окончания'))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('Статус проекта')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')

# Участники проекта
class ProjectParticipant(models.Model):
    class Role(models.TextChoices):
        STUDENT = 'student', _('Студент')
        TEACHER = 'teacher', _('Преподаватель')
        LEAD = 'lead', _('Руководитель')

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='participants', verbose_name=_('Проект'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name=_('Роль в проекте'))

    def __str__(self):
        return f"{self.user} — {self.project} ({self.role})"

    class Meta:
        verbose_name = _('Участник проекта')
        verbose_name_plural = _('Участники проекта')
        unique_together = ('project', 'user')