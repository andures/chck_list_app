# Generated by Django 5.1.7 on 2025-03-21 02:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('todo', 'Por Hacer'), ('progress', 'En Progreso'), ('done', 'Completado')], default='todo', max_length=20)),
                ('position', models.IntegerField(default=0)),
                ('todo_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='checklist.todolist')),
            ],
            options={
                'ordering': ['status', 'position'],
            },
        ),
    ]
