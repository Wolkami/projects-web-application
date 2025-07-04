import os
import django
import random
from datetime import timedelta, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_project_manager.settings')
django.setup()

from api.models import CustomUser, Project, ProjectParticipant, Task

def run():
    # Удалим старые данные
    print("🧹 Очистка старых данных...")
    Task.objects.all().delete()
    ProjectParticipant.objects.all().delete()
    Project.objects.all().delete()
    CustomUser.objects.exclude(is_superuser=True).delete()

    print("👤 Создание пользователей...")
    users = []
    for i in range(1, 6):
        user = CustomUser.objects.create_user(
            username=f'student{i}',
            email=f'student{i}@test.com',
            password='password123',
            role='student'
        )
        users.append(user)

    teacher = CustomUser.objects.create_user(
        username='teacher1',
        email='teacher1@test.com',
        password='password123',
        role='teacher'
    )

    print("📁 Создание проектов...")
    for i in range(3):
        project = Project.objects.create(
            title=f'Проект {i + 1}',
            description='Описание учебного проекта',
            creator=teacher,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

        # Участники
        participants = random.sample(users, k=2)
        for u in participants:
            ProjectParticipant.objects.create(
                project=project,
                user=u,
                role='student'
            )

        # Создателя тоже добавим
        ProjectParticipant.objects.create(
            project=project,
            user=teacher,
            role='manager'
        )

        print(f"📝 Добавление задач в {project.title}...")
        for j in range(5):
            Task.objects.create(
                project=project,
                title=f'Задача {j + 1} проекта {i + 1}',
                description='Описание задачи',
                assignee=random.choice(participants + [teacher]),
                status=random.choice(['todo', 'in_progress', 'done']),
                due_date=date.today() + timedelta(days=random.randint(3, 15))
            )

    print("✅ Готово: проекты, пользователи и задачи созданы.")

if __name__ == '__main__':
    run()
