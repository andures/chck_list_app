# Generated by Django 5.1.7 on 2025-04-03 16:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0015_gquestion_allow_attachments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='gquestion',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_questions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gquestion',
            name='in_question_bank',
            field=models.BooleanField(default=False, help_text='Guardar esta pregunta en el banco de preguntas para reutilizarla'),
        ),
        migrations.AddField(
            model_name='gquestion',
            name='usage_count',
            field=models.PositiveIntegerField(default=0, help_text='Número de veces que se ha usado esta pregunta'),
        ),
    ]
