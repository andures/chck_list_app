# Generated by Django 5.1.7 on 2025-03-24 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0008_answer_media_answer_media_type_question_media_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='file_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
