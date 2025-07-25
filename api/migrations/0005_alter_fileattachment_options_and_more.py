# Generated by Django 5.2.3 on 2025-07-02 11:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_comment_options_rename_user_comment_author_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fileattachment',
            options={'ordering': ['-uploaded_at'], 'verbose_name': 'Файл задачи', 'verbose_name_plural': 'Файлы задачи'},
        ),
        migrations.RemoveField(
            model_name='fileattachment',
            name='project',
        ),
        migrations.RemoveField(
            model_name='fileattachment',
            name='user',
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='uploaded_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Загрузил'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fileattachment',
            name='task',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='api.task', verbose_name='Задача'),
            preserve_default=False,
        ),
    ]
