# Generated by Django 5.1.2 on 2024-11-08 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0006_jockeys_trainers_horses_entries'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entries',
            name='comments',
        ),
    ]
