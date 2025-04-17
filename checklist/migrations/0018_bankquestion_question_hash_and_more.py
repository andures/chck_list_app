# Generated by Django 5.1.7 on 2025-04-04 02:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0017_remove_gquestion_in_question_bank_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='bankquestion',
            name='question_hash',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='bankquestion',
            unique_together={('created_by', 'question_hash')},
        ),
    ]
