# Generated by Django 5.1.2 on 2024-11-08 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0007_remove_entries_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horses',
            name='registration_number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
