# Generated by Django 5.1.2 on 2024-11-13 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0017_remove_workouts_course_workouts_surface'),
    ]

    operations = [
        migrations.AddField(
            model_name='races',
            name='eqb_chart_import',
            field=models.BooleanField(default=False),
        ),
    ]
