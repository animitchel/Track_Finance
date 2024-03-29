# Generated by Django 5.0.3 on 2024-03-24 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0027_alter_income_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='frequency',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='income',
            name='next_occurrence',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='income',
            name='recurring_income',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='income',
            name='transaction_title',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
