from django.db import models
import pytz

class Tracks(models.Model):

    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
    country = models.CharField(max_length=3)
    equibase_chart_name = models.CharField(max_length=255)


class Races(models.Model):

    EQUIBASE_SEX_RESTRICTIONS_CHOICES = [
        ('N', 'No sex restrictions'),
        ('M', 'Mares and fillies only'),
        ('C', 'Colts and/or geldings only'),
        ('F', 'Fillies only'),
    ]

    EQUIBASE_AGE_RESTRICTIONS_CHOICES = [
        ('AO', '2-year-olds only'),
        ('AU', '2-year-olds and up'),
        ('BO', '3-year-olds only'),
        ('BU', '3-year-olds and up'),
        ('CO', '4-year-olds only'),
        ('CU', '4-year-olds and up'),
        ('DO', '5-year-olds only'),
        ('DU', '5-year-olds and up'),
        ('EO', '3 & 4-year-olds only'),
        ('EU', '3 & 4-year-olds and up'),
        ('FO', '4 & 5-year-olds only'),
        ('FU', '4 & 5-year-olds and up'),
        ('GO', '3, 4, & 5-year-olds only'),
        ('GU', '3, 4, & 5-year-olds and up'),
        ('HO', 'All ages'),
    ]

    RACE_SURFACE = [
        ('D', 'Dirt'),
        ('T', 'Turf')
    ]

    EQUIBASE_RACE_TYPE_CHOICES = [
        ('ALW', 'Allowance race'),
        ('AOC', 'Allowance/Optional Claiming'),
        ('CLH', 'Claiming Handicap'),
        ('CLM', 'Claiming'),
        ('CST', 'Claiming Stakes'),
        ('HCP', 'Handicap'),
        ('MAT', 'Match Race'),
        ('MCL', 'Maiden Claiming'),
        ('MOC', 'Maiden Optional Claiming'),
        ('MSA', 'Maiden Starter Allowance'),
        ('MSW', 'Maiden Special Weight'),
        ('MST', 'Maiden Stakes'),
        ('OCH', 'Optional Claiming Handicap'),
        ('OCL', 'Optional Claiming'),
        ('SHP', 'Starter Handicap'),
        ('SOC', 'Starter/Optional Claiming'),
        ('SST', 'Starter Stakes'),
        ('STK', 'Stakes'),
        ('STR', 'Starter Allowance'),
        ('TRL', 'Trial'),
        ('WCL', 'Waiver Claiming'),
        ('WMC', 'Waiver Maiden Claiming'),
        
        # Quarter Horse and Mixed Breed Race Types
        ('ALWFL', 'Allowance Final'),
        ('AWT', 'Allowance Trial'),
        ('CAN', 'Cancelled'),
        ('CHM', 'Championship'),
        ('CLS', 'Claiming Stakes'),
        ('CLT', 'Claiming Stakes Trial'),
        ('CON', 'Consolation'),
        ('CST', 'Claiming Stakes/Trial'),
        ('DBY', 'Derby'),
        ('DBYFL', 'Derby Final'),
        ('DCN', 'Derby Consolation'),
        ('DTR', 'Derby Trial'),
        ('EXH', 'Exhibition'),
        ('FCN', 'Futurity Consolation'),
        ('FNL', 'Final'),
        ('FTR', 'Futurity Trial'),
        ('FUT', 'Futurity'),
        ('FUTFL', 'Futurity Final'),
        ('HDS', 'Handicap Stakes'),
        ('IHS', 'Invitational Handicap Stakes'),
        ('INH', 'Invitational Handicap'),
        ('INS', 'Invitational Stakes'),
        ('INV', 'Invitational'),
        ('MCL', 'Maiden Claiming'),
        ('MCN', 'Maturity Consolation'),
        ('MATFL', 'Maturity Final'),
        ('MCH', 'Match Race'),
        ('MDN', 'Maiden'),
        ('MDT', 'Maiden Trial'),
        ('MOC', 'Maiden Optional Claiming'),
        ('MSA', 'Maiden Starter Allowance'),
        ('MTR', 'Maturity Trial'),
        ('OCL', 'Optional Claiming'),
        ('SCN', 'Stakes Consolation'),
        ('SHP', 'Starter Handicap'),
        ('SOC', 'Starter Optional Claiming'),
        ('SPC', 'Speed Index Consolation'),
        ('SPF', 'Speed Index Final'),
        ('SPI', 'Speed Index Race'),
        ('SPT', 'Speed Index Trial'),
        ('STA', 'Starter Allowance'),
        ('STK', 'Stakes'),
        ('STR', 'Stakes Trial'),
        ('TRL', 'Trials'),
        ('UNK', 'Unknown Race Type'),
        ('WCL', 'Waiver Claiming'),
        ('ZRC', 'Cancelled Race'),
    ]

    DAY_EVENING_CHOICES = [
        ('D', 'Day'),
        ('E', 'Evening')
    ]

    DRF_AGE_RESTRICTION_CHOICES = [
        ('02', '2 yo'),
        ('03', '3 yo'),
        ('04', '4 yo'),
        ('05', '5 yo'),
        ('06', '6 yo'),
        ('07', '7 yo'),
        ('08', '8 yo'),
        ('09', '9 yo'),
        ('23', '2 & 3 yo\'s'),
        ('2U', '2 yo\'s & up'),
        ('34', '3 & 4 yo\'s'),
        ('35', '3, 4, & 5 yo\'s'),
        ('36', '3, 4, 5, & 6 yo\'s'),
        ('3U', '3 yo\'s & up'),
        ('45', '4 & 5 yo\'s'),
        ('46', '4, 5, & 6 yo\'s'),
        ('47', '4, 5, 6, & 7 yo\'s'),
        ('4U', '4 yo\'s & up'),
        ('56', '5 & 6 yo\'s'),
        ('57', '5, 6, & 7 yo\'s'),
        ('58', '5, 6, 7, & 8 yo\'s'),
        ('59', '5, 6, 7, 8, & 9 yo\'s'),
        ('5U', '5 yo\'s & up'),
        ('67', '6 & 7 yo\'s'),
        ('68', '6, 7, & 8 yo\'s'),
        ('69', '6, 7, 8, & 9 yo\'s'),
        ('6U', '6 yo\'s & up'),
        ('78', '7 & 8 yo\'s'),
        ('79', '7, 8, & 9 yo\'s'),
        ('7U', '7 yo\'s & up'),
        ('8U', '8 yo\'s & up'),
        ('9U', '9 yo\'s & up'),
    ]

    DRF_SEX_RESTRICTION_CHOICES = [
        ('O', 'Open'),             # Blank or open
        ('A', 'C & G (colts and geldings)'),  # Colts and geldings
        ('B', 'F & M (fillies and mares)'),  # Fillies and mares
        ('C', 'C (colts)'),       # Colts
        ('D', 'C & F (colts and fillies)'),  # Colts and fillies
        ('E', 'F & G (fillies and geldings)'),  # Fillies and geldings
        ('F', 'F (fillies)'),     # Fillies
        ('G', 'G (geldings)'),   # Geldings
        ('H', 'H (horses only)'),  # Horses only
        ('M', 'M (mares only)'),  # Mares only
    ]

    BREED_CHOICES = [
        ('TB', 'Thoroughbred'),   # Thoroughbred
        ('QH', 'Quarter Horse'),  # Quarter Horse
        ('AR', 'Arabian'),        # Arabian
        ('PT', 'Paint'),          # Paint
        ('MX', 'Mixed Breeds'),   # Mixed Breeds
    ]

    # Common
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)
    race_date = models.DateField()
    race_number = models.IntegerField()

    # DRF TRACKS
    drf_tracks_import = models.BooleanField(default=False)
    day_evening = models.CharField(max_length=1, choices=DAY_EVENING_CHOICES, null=True)
    final = models.BooleanField(default=False)

    # DRF Entries
    drf_entries_import = models.BooleanField(default=False)
    post_time = models.DateTimeField(null=True)
    age_restriction = models.CharField(null=True, max_length=2, choices=DRF_AGE_RESTRICTION_CHOICES)
    sex_restiction = models.CharField(null=True, max_length=1, choices=DRF_SEX_RESTRICTION_CHOICES)
    minimum_claiming_price = models.FloatField(null=True)
    maximum_claiming_price = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    purse = models.IntegerField(null=True)
    wager_text = models.CharField(max_length=255, null=True)
    breed = models.CharField(max_length=2, null=True, choices=BREED_CHOICES)
    cancelled = models.BooleanField(default=False)

    # EQB Entries
    eqb_entries_import = models.BooleanField(default=False)

    def create_drf_entries_url(self):

        # format the date
        url_formatted_date = self.race_date.strftime('%m-%d-%Y')

        # return the url
        return f'https://www.drf.com/entries/entryDetails/id/{self.track.code}/country/{self.track.country}/date/{url_formatted_date}'
    

class Horses(models.Model):

    # common data
    horse_name = models.CharField(max_length=255, unique=True)

    # drf entries
    registration_number = models.CharField(max_length=255, null=True)
    sire = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name='children_of_sire')
    dam = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name='children_of_dam')
    dam_sire = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name= 'grandchildren')

    # equibase entries
    equibase_horse_id = models.IntegerField(null=True)
    equibase_horse_type = models.CharField(max_length=3, null=True)
    equibase_horse_registry = models.CharField(max_length=1, null=True)
    horse_state_or_country = models.CharField(max_length=3, null=True)


class Jockeys(models.Model):

    # common
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)

    # drf entries
    drf_jockey_id = models.IntegerField(null=True)
    drf_jockey_type = models.CharField(max_length=2, blank=True)
    alias = models.CharField(max_length=255, blank=True)

    # equibase entries
    equibase_jockey_id = models.IntegerField(null=True)
    equibase_jockey_type = models.CharField(max_length=3, null=True)


class Trainers(models.Model):

    # common data
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)

    # drf entries
    drf_trainer_id = models.IntegerField(null=True)
    drf_trainer_type = models.CharField(max_length=2, blank=True)
    alias = models.CharField(max_length=255, blank=True)

    # equibase entries
    equibase_trainer_id = models.IntegerField(null=True)
    equibase_trainer_type = models.CharField(max_length=3, null=True)


class Entries(models.Model):

    SCRATCH_REASON_CHOICES = [
        ('N', 'Not Scratched'),
        ('A', 'Also-Eligible'),
        ('E', 'Early'),
        ('G', 'Gate'),
        ('M', 'Main-Track-Only'),
        ('O', 'Off-Turf'),
        ('S', 'Stewards'),
        ('T', 'Trainer'),
        ('V', 'Veterinarian'),
    ]

    # common data
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    horse = models.ForeignKey(Horses, on_delete=models.CASCADE)
    
    # common potentially null data
    post_position = models.IntegerField(null=True)
    trainer = models.ForeignKey(Trainers, on_delete=models.CASCADE, null=True)
    jockey = models.ForeignKey(Jockeys, on_delete=models.CASCADE, null=True)
    program_number = models.CharField(max_length=3, null=True)

    # drf entries
    drf_entries_import = models.BooleanField(default=False, null=True)
    scratch_indicator = models.CharField(max_length=1, default='', blank=True)
    medication = models.CharField(max_length=7, null=True, blank=True)
    equipment = models.CharField(max_length=17, null=True, blank=True)
    weight = models.FloatField(null=True)

    # equibase horse_results
    equibase_horse_results_scraped = models.BooleanField(default=False)
    equibase_horse_entries_scraped = models.BooleanField(default=False)
    equibase_speed_rating = models.IntegerField(null=True)

