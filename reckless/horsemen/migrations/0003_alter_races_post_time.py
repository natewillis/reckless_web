# Generated by Django 5.1.2 on 2024-11-08 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0002_alter_tracks_country_races'),
    ]

    operations = [
        migrations.AlterField(
            model_name='races',
            name='post_time',
            field=models.DateTimeField(null=True),
        ),
    ]
