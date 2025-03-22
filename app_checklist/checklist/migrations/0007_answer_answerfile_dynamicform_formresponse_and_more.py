# Generated by Django 5.1.7 on 2025-03-22 03:03

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0006_remove_selectedoption_answer_remove_dynamicform_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_answer', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnswerFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='form_answers/')),
                ('file_name', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=100)),
                ('file_url', models.URLField(blank=True, null=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='checklist.answer')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_published', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FormResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='checklist.dynamicform')),
                ('respondent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='response',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='checklist.formresponse'),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('question_type', models.CharField(choices=[('short_text', 'Respuesta Corta'), ('paragraph', 'Párrafo'), ('multiple_choice', 'Opción Múltiple'), ('checkbox', 'Casillas de Verificación'), ('dropdown', 'Menú Desplegable'), ('file_upload', 'Carga de Archivos'), ('linear_scale', 'Escala Lineal'), ('multiple_choice_grid', 'Cuadrícula de Opción Múltiple'), ('checkbox_grid', 'Cuadrícula de Casillas de Verificación'), ('date', 'Fecha'), ('time', 'Hora'), ('datetime', 'Fecha y Hora')], max_length=30)),
                ('is_required', models.BooleanField(default=False)),
                ('position', models.IntegerField(default=0)),
                ('help_text', models.CharField(blank=True, max_length=255, null=True)),
                ('min_value', models.IntegerField(blank=True, null=True)),
                ('max_value', models.IntegerField(blank=True, null=True)),
                ('min_label', models.CharField(blank=True, max_length=50, null=True)),
                ('max_label', models.CharField(blank=True, max_length=50, null=True)),
                ('rows_text', models.TextField(blank=True, null=True)),
                ('columns_text', models.TextField(blank=True, null=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='checklist.dynamicform')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checklist.question'),
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('position', models.IntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='checklist.question')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='SelectedOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_options', to='checklist.answer')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checklist.questionoption')),
            ],
        ),
    ]
