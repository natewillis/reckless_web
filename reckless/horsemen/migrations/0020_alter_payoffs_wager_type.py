# Generated by Django 5.1.2 on 2024-11-14 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horsemen', '0019_remove_tracks_equibase_chart_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payoffs',
            name='wager_type',
            field=models.CharField(choices=[('0', 'Choose 6'), ('C', 'Classix'), ('Z', 'Consolation Double'), ('M', 'Consolation Pick 3'), ('8', 'Countdown'), ('D', 'Daily Double'), ('E', 'Exacta'), ('J', 'Exactor'), ('N', 'Future Wager'), ('X', 'Grand Slam'), ('H', 'Head2Head'), ('P', 'Jockey Challenge'), ('V', 'Odd or Even'), ('O', 'Omni'), ('F', 'Perfecta'), ('G', 'Perfector'), ('I', 'Pick 10'), ('3', 'Pick 3'), ('4', 'Pick 4'), ('5', 'Pick 5'), ('6', 'Pick 6'), ('7', 'Pick 7'), ('9', 'Pick 9'), ('L', 'Place Pick All'), ('Q', 'Quinella'), ('1', 'Roulette'), ('Y', 'Super Bet'), ('B', 'Super Tri'), ('S', 'Superfecta'), ('U', 'Tri Super'), ('A', 'Triactor'), ('T', 'Trifecta'), ('R', 'Triple'), ('W', 'Twin Trifecta'), ('2', 'Two in the Money'), ('K', 'Win Four'), ('HJ', 'Super High Five Jackpot')], max_length=2),
        ),
    ]
