# Generated by Django 2.0.1 on 2021-09-19 03:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_answer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_org', to='organisations.Tenant'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
