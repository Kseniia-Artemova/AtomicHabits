# Generated by Django 4.2.6 on 2023-10-21 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0007_remove_interval_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='last_event',
            field=models.DateField(blank=True, null=True, verbose_name='Дата последней отправки напоминания'),
        ),
    ]
