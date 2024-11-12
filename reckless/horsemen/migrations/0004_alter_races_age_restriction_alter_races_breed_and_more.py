# Generated by Django 5.1.2 on 2024-11-08 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0003_alter_races_post_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='races',
            name='age_restriction',
            field=models.CharField(choices=[('02', '2 yo'), ('03', '3 yo'), ('04', '4 yo'), ('05', '5 yo'), ('06', '6 yo'), ('07', '7 yo'), ('08', '8 yo'), ('09', '9 yo'), ('23', "2 & 3 yo's"), ('2U', "2 yo's & up"), ('34', "3 & 4 yo's"), ('35', "3, 4, & 5 yo's"), ('36', "3, 4, 5, & 6 yo's"), ('3U', "3 yo's & up"), ('45', "4 & 5 yo's"), ('46', "4, 5, & 6 yo's"), ('47', "4, 5, 6, & 7 yo's"), ('4U', "4 yo's & up"), ('56', "5 & 6 yo's"), ('57', "5, 6, & 7 yo's"), ('58', "5, 6, 7, & 8 yo's"), ('59', "5, 6, 7, 8, & 9 yo's"), ('5U', "5 yo's & up"), ('67', "6 & 7 yo's"), ('68', "6, 7, & 8 yo's"), ('69', "6, 7, 8, & 9 yo's"), ('6U', "6 yo's & up"), ('78', "7 & 8 yo's"), ('79', "7, 8, & 9 yo's"), ('7U', "7 yo's & up"), ('8U', "8 yo's & up"), ('9U', "9 yo's & up")], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='breed',
            field=models.CharField(choices=[('TB', 'Thoroughbred'), ('QH', 'Quarter Horse'), ('AR', 'Arabian'), ('PT', 'Paint'), ('MX', 'Mixed Breeds')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='day_evening',
            field=models.CharField(choices=[('D', 'Day'), ('E', 'Evening')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='distance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='final',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='races',
            name='maximum_claiming_price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='minimum_claiming_price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='purse',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='sex_restiction',
            field=models.CharField(choices=[('N', 'Open'), ('A', 'C & G (colts and geldings)'), ('B', 'F & M (fillies and mares)'), ('C', 'C (colts)'), ('D', 'C & F (colts and fillies)'), ('E', 'F & G (fillies and geldings)'), ('F', 'F (fillies)'), ('G', 'G (geldings)'), ('H', 'H (horses only)'), ('M', 'M (mares only)')], max_length=1, null=True),
        ),
    ]