# Generated by Django 5.0.3 on 2024-03-21 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0026_income'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='notes',
            field=models.TextField(max_length=50),
        ),
    ]
