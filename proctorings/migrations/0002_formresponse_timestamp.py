# Generated by Django 5.1.1 on 2024-09-20 04:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proctorings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='formresponse',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]