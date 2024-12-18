# Generated by Django 5.1.2 on 2024-11-11 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0013_alter_entries_jockey_alter_entries_post_position_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entries',
            name='drf_entries_import',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='entries',
            name='scratch_indicator',
            field=models.CharField(blank=True, default='', max_length=1),
        ),
        migrations.AlterField(
            model_name='entries',
            name='weight',
            field=models.FloatField(null=True),
        ),
    ]
