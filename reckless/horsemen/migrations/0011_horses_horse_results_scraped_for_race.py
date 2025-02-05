# Generated by Django 5.1.2 on 2024-11-11 20:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0010_horses_equibase_horse_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='horses',
            name='horse_results_scraped_for_race',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='horses_scraped_for_equibase_results', to='horsemen.races'),
        ),
    ]
