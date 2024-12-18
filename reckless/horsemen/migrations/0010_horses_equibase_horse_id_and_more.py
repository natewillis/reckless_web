# Generated by Django 5.1.2 on 2024-11-09 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0009_remove_entries_scratch_flag_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='horses',
            name='equibase_horse_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='horses',
            name='equibase_horse_registry',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='horses',
            name='equibase_horse_type',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='horses',
            name='horse_state_or_country',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='jockeys',
            name='equibase_jockey_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='jockeys',
            name='equibase_jockey_type',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='eqb_entries_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='trainers',
            name='equibase_trainer_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='trainers',
            name='equibase_trainer_type',
            field=models.CharField(max_length=3, null=True),
        ),
    ]
