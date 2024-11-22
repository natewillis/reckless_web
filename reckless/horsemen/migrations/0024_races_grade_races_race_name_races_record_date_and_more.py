# Generated by Django 5.1.2 on 2024-11-21 19:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0023_rename_sex_restiction_races_sex_restriction'),
    ]

    operations = [
        migrations.AddField(
            model_name='races',
            name='grade',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='race_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='record_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='record_horse_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='record_time',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='age_restriction',
            field=models.CharField(choices=[('02', 'Two year old'), ('03', 'Three year old'), ('04', 'Four year old'), ('05', 'Five year old'), ('06', 'Six year old'), ('07', 'Seven year old'), ('08', 'Eight year old'), ('09', 'Nine year old'), ('23', 'Two and Three year olds'), ('2U', 'Two year olds and older'), ('34', 'Three and Four year olds'), ('35', 'Three, Four, and Five year olds'), ('36', 'Three, Four, Five, and Six year olds'), ('3U', 'Three year olds and older'), ('45', 'Four and Five year olds'), ('46', 'Four, Five, and Six year olds'), ('47', 'Four, Five, Six, and Seven year olds'), ('4U', 'Four year olds and older'), ('56', 'Five and Six year olds'), ('57', 'Five, Six, and Seven year olds'), ('58', 'Five, Six, Seven, and Eight year olds'), ('59', 'Five, Six, Seven, Eight, and Nine year olds'), ('5U', 'Five year olds and older'), ('67', 'Six and Seven year olds'), ('68', 'Six, Seven, and Eight year olds'), ('69', 'Six, Seven, Eight, and Nine year olds'), ('6U', 'Six year olds and older'), ('78', 'Seven and Eight year olds'), ('79', 'Seven, Eight, and Nine year olds'), ('7U', 'Seven year olds and older'), ('8U', 'Eight year olds and older'), ('9U', 'Nine year olds and older')], max_length=2, null=True),
        ),
        migrations.CreateModel(
            name='SplitCallVelocities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
                ('start_distance', models.FloatField()),
                ('end_distance', models.FloatField()),
                ('split_time', models.FloatField()),
                ('total_time', models.FloatField()),
                ('velocity', models.FloatField()),
                ('lengths_back', models.FloatField()),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horsemen.races')),
            ],
        ),
    ]