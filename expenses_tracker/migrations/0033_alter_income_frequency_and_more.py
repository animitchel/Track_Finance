# Generated by Django 5.0.3 on 2024-03-24 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0032_rename_recurring_income_income_recurring_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='frequency',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='income',
            name='transaction_title',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
