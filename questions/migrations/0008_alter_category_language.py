# Generated by Django 3.2.5 on 2021-09-25 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0007_auto_20210925_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='language',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
