# Generated by Django 5.1.2 on 2024-11-12 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0016_entries_equibase_horse_entries_scraped_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workouts',
            name='course',
        ),
        migrations.AddField(
            model_name='workouts',
            name='surface',
            field=models.CharField(choices=[('D', 'Dirt'), ('T', 'Turf')], default='D', max_length=1),
        ),
    ]
