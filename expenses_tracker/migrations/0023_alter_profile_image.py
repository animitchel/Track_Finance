# Generated by Django 5.0.2 on 2024-03-06 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_tracker', '0022_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='images/c0749b7cc401421662ae901ec8f9f660.jpg', null=True, upload_to='images'),
        ),
    ]
