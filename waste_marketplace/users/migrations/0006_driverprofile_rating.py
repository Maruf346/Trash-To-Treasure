# Generated by Django 5.1.5 on 2025-04-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_driverprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverprofile',
            name='rating',
            field=models.FloatField(default=0.0),
        ),
    ]
