# Generated by Django 5.0.3 on 2024-03-24 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0029_rename_transaction_title_income_income_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='income',
            old_name='source',
            new_name='category',
        ),
    ]