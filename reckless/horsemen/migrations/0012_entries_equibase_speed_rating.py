# Generated by Django 5.1.2 on 2024-11-11 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0011_horses_horse_results_scraped_for_race'),
    ]

    operations = [
        migrations.AddField(
            model_name='entries',
            name='equibase_speed_rating',
            field=models.IntegerField(null=True),
        ),
    ]