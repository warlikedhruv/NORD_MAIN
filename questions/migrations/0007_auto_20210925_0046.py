# Generated by Django 3.2.7 on 2021-09-25 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_answer_set_goal'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='goal_answer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='goal_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
