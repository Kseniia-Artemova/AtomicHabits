# Generated by Django 4.2.6 on 2023-10-20 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0004_schedule_last_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='last_event',
        ),
    ]
