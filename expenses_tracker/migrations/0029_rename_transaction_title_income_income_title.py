# Generated by Django 5.0.3 on 2024-03-24 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0028_income_frequency_income_next_occurrence_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='income',
            old_name='transaction_title',
            new_name='income_title',
        ),
    ]