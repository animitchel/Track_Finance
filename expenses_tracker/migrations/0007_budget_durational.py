# Generated by Django 5.0 on 2024-01-29 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0006_budget_duration_alter_budget_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='durational',
            field=models.BooleanField(default=False),
        ),
    ]