# Generated by Django 5.0.3 on 2024-03-25 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0033_alter_income_frequency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='notes',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(max_length=100, null=True),
        ),
    ]
