from django.db import models
import pytz
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from horsemen.constants import BREED_CHOICES, DAY_EVENING_CHOICES, \
    EQUIBASE_RACE_TYPE_CHOICES, DRF_AGE_RESTRICTION_CHOICES, \
        DRF_SEX_RESTRICTION_CHOICES, RACE_SURFACE, SCRATCH_REASON_CHOICES, \
        BET_CHOICES

class Tracks(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
    country = models.CharField(max_length=3)
    
    def clean(self):
        if self.time_zone and self.time_zone not in dict(self.TIMEZONES):
            raise ValidationError(
                _("Invalid timezone: %(value)s"),
                params={'value': self.time_zone},
                code='invalid_choice'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.code})'
    
    def get_drf_results_url_for_date(self, race_date):
        return f"https://www.drf.com/results/resultDetails/id/{self.code}/country/{self.country}/date/{race_date.strftime('%m-%d-%Y')}"
    
    def get_drf_entries_url_for_date(self, race_date):
        return f"https://www.drf.com/entries/entryDetails/id/{self.code}/country/{self.country}/date/{race_date.strftime('%m-%d-%Y')}"
    
    def get_equibase_chart_url_for_date(self, race_date):
        return f"https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID={self.code}&CTRY={self.country}&DT={race_date.strftime('%m/%d/%Y')}&DAY=D&STYLE=EQB"

    def get_equibase_entries_url_for_date(self, race_date):
        return f'https://www.equibase.com/static/entry/{self.code}{race_date.strftime("%m%d%y")}{self.country}-EQB.html'


class Races(models.Model):
    # Common
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)
    race_date = models.DateField()
    race_number = models.IntegerField()

    # DRF TRACKS
    drf_tracks_import = models.BooleanField(default=False)
    day_evening = models.CharField(max_length=1, choices=DAY_EVENING_CHOICES, null=True)

    # DRF Entries
    drf_entries_import = models.BooleanField(default=False)
    post_time = models.DateTimeField(null=True)
    age_restriction = models.CharField(null=True, max_length=2, choices=DRF_AGE_RESTRICTION_CHOICES)
    sex_restriction = models.CharField(null=True, max_length=1, choices=DRF_SEX_RESTRICTION_CHOICES)
    minimum_claiming_price = models.FloatField(null=True)
    maximum_claiming_price = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    purse = models.IntegerField(null=True)
    wager_text = models.CharField(max_length=255, null=True)
    breed = models.CharField(max_length=2, null=True, choices=BREED_CHOICES)
    cancelled = models.BooleanField(default=False)
    race_surface = models.CharField(max_length=1, choices=RACE_SURFACE, null=True)

    # DRF Results
    drf_results_import = models.BooleanField(default=False)
    condition = models.CharField(max_length=255, null=True)
    off_time = models.DateTimeField(null=True)

    # EQB Entries
    equibase_entries_import = models.BooleanField(default=False)

    # EQB chart
    equibase_chart_import = models.BooleanField(default=False)
    race_type = models.CharField(max_length=5, null=True, choices=EQUIBASE_RACE_TYPE_CHOICES)
    race_name = models.CharField(max_length=255, null=True)
    grade = models.IntegerField(null=True)
    record_horse_name = models.CharField(max_length=255, null=True)
    record_time = models.FloatField(null=True)
    record_date = models.DateField(null=True)
    hurdles = models.BooleanField(default=False)

    def clean(self):
        # Choice Field Validation
        if self.day_evening and self.day_evening not in dict(DAY_EVENING_CHOICES):
            raise ValidationError(
                _("Invalid day/evening choice: %(value)s"),
                params={'value': self.day_evening},
                code='invalid_choice'
            )
        
        if self.age_restriction and self.age_restriction not in dict(DRF_AGE_RESTRICTION_CHOICES):
            raise ValidationError(
                _("Invalid age restriction: %(value)s"),
                params={'value': self.age_restriction},
                code='invalid_choice'
            )
            
        if self.sex_restriction and self.sex_restriction not in dict(DRF_SEX_RESTRICTION_CHOICES):
            raise ValidationError(
                _("Invalid sex restriction: %(value)s"),
                params={'value': self.sex_restriction},
                code='invalid_choice'
            )
            
        if self.breed and self.breed not in dict(BREED_CHOICES):
            raise ValidationError(
                _("Invalid breed: %(value)s"),
                params={'value': self.breed},
                code='invalid_choice'
            )
            
        if self.race_surface and self.race_surface not in dict(RACE_SURFACE):
            raise ValidationError(
                _("Invalid race surface: %(value)s"),
                params={'value': self.race_surface},
                code='invalid_choice'
            )
            
        if self.race_type and self.race_type not in dict(EQUIBASE_RACE_TYPE_CHOICES):
            raise ValidationError(
                _("Invalid race type: %(value)s"),
                params={'value': self.race_type},
                code='invalid_choice'
            )
        
        # Individual Field Validation
        if self.distance is not None:
            if self.distance > 32 or self.distance <= 0:
                raise ValidationError(
                    _("Invalid distance: %(value)s"),
                    params={'value': self.distance},
                    code='invalid_input'
                )
                
        if self.condition:
            if len(self.condition) < 3:
                raise ValidationError(
                    _("Invalid condition: %(value)s"),
                    params={'value': self.condition},
                    code='invalid_input'
                )
        
        # DRF Tracks Import
        if self.drf_tracks_import:
            if not self.day_evening:
                raise ValidationError(
                    _("DRF tracks import requires valid day/evening flag"),
                    code='missing_input'
                )
        
        # DRF Results Import
        if self.drf_results_import:
            required_fields = {
                'race_type': "race type",
                'age_restriction': "age restriction",
                'sex_restriction': "sex restriction",
                'minimum_claiming_price': "minimum claiming price",
                'maximum_claiming_price': "maximum claiming price",
                'distance': "distance",
                'purse': "purse",
                'breed': "breed",
                'race_surface': "surface",
                'condition': "track condition"
            }
            
            for field, name in required_fields.items():
                if getattr(self, field) is None:
                    raise ValidationError(
                        _("DRF results import requires valid %(field)s"),
                        params={'field': name},
                        code='missing_input'
                    )
        
        # Equibase Chart Import
        if self.equibase_chart_import:
            if not self.cancelled:
                required_fields = {
                    'distance': "distance",
                    'purse': "purse",
                    'breed': "breed",
                    'race_surface': "surface",
                    'condition': "track condition"
                }
                
                for field, name in required_fields.items():
                    if getattr(self, field) is None:
                        raise ValidationError(
                            _("Equibase chart import requires valid %(field)s"),
                            params={'field': name},
                            code='missing_input'
                        )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Horses(models.Model):
    # common data
    horse_name = models.CharField(max_length=255, unique=True)

    # drf entries
    registration_number = models.CharField(max_length=255, null=True)
    sire = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name='children_of_sire')
    dam = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name='children_of_dam')
    dam_sire = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name='grandchildren')

    # equibase entries
    equibase_horse_id = models.IntegerField(null=True)
    equibase_horse_type = models.CharField(max_length=3, null=True)
    equibase_horse_registry = models.CharField(max_length=1, null=True)
    horse_state_or_country = models.CharField(max_length=3, null=True)
    
    def get_equibase_horse_results_url(self):
        if self.equibase_horse_id and self.equibase_horse_type and self.equibase_horse_registry:
            return f'https://www.equibase.com/profiles/Results.cfm?type=Horse&refno={self.equibase_horse_id}&registry={self.equibase_horse_registry}&rbt={self.equibase_horse_type}'
        else:
            return ''
    
    def clean(self):

        if '(' in self.horse_name:
            raise ValidationError(
                _("Invalid horse name due to parenthesis: %(value)s"),
                params={'value': self.horse_name},
                code='invalid_input'
            )

        if self.registration_number and self.registration_number == '':
            raise ValidationError(
                _("Invalid horse registration number: %(value)s"),
                params={'value': self.registration_number},
                code='invalid_input'
            )
            
        if self.equibase_horse_id and self.equibase_horse_id <= 0:
            raise ValidationError(
                _("Invalid horse equibase horse id number: %(value)s"),
                params={'value': self.equibase_horse_id},
                code='invalid_input'
            )
            
        if self.equibase_horse_id:
            if not self.equibase_horse_type:
                raise ValidationError(
                    _("Required equibase_horse_type"),
                    code='missing_input'
                )
            elif len(self.equibase_horse_type) < 2:
                raise ValidationError(
                    _("Invalid equibase_horse_type: %(value)s"),
                    params={'value': self.equibase_horse_type},
                    code='invalid_input'
                )
                
            if not self.equibase_horse_registry:
                raise ValidationError(
                    _("Required equibase_horse_registry"),
                    code='missing_input'
                )
            elif len(self.equibase_horse_registry) != 1:
                raise ValidationError(
                    _("Invalid equibase_horse_registry: %(value)s"),
                    params={'value': self.equibase_horse_registry},
                    code='invalid_input'
                )
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Jockeys(models.Model):
    # common
    first_name = models.CharField(max_length=255, null=True)
    first_initials = models.CharField(max_length=10, null=True)
    last_name = models.CharField(max_length=255)

    # drf entries
    drf_jockey_id = models.IntegerField(null=True)
    drf_jockey_type = models.CharField(max_length=2, blank=True)
    alias = models.CharField(max_length=255, blank=True)

    # equibase entries
    equibase_jockey_id = models.IntegerField(null=True)
    equibase_jockey_type = models.CharField(max_length=3, null=True)
    
    def clean(self):
        if self.drf_jockey_id and self.drf_jockey_id == '':
            raise ValidationError(
                _("Invalid drf_jockey_id: %(value)s"),
                params={'value': self.drf_jockey_id},
                code='invalid_input'
            )
        if self.first_name is None and self.first_initials is None:
            raise ValidationError(
                _("Either first_name or first initials must be given"),
                code='invalid_input'
            )
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Trainers(models.Model):
    # common data
    first_name = models.CharField(max_length=255, null=True)
    first_initials = models.CharField(max_length=10, null=True)
    last_name = models.CharField(max_length=255)

    # drf entries
    drf_trainer_id = models.IntegerField(null=True)
    drf_trainer_type = models.CharField(max_length=2, blank=True)
    alias = models.CharField(max_length=255, blank=True)

    # equibase entries
    equibase_trainer_id = models.IntegerField(null=True)
    equibase_trainer_type = models.CharField(max_length=3, null=True)
    
    def clean(self):
        if self.drf_trainer_id and self.drf_trainer_id == '':
            raise ValidationError(
                _("Invalid drf_trainer_id: %(value)s"),
                params={'value': self.drf_trainer_id},
                code='invalid_input'
            )
        if self.first_name is None and self.first_initials is None:
            raise ValidationError(
                _("Either first_name or first initials must be given"),
                code='invalid_input'
            )
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Entries(models.Model):
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
    scratch_indicator = models.CharField(max_length=1, default='N', choices=SCRATCH_REASON_CHOICES)
    medication = models.CharField(max_length=7, null=True, blank=True)
    equipment = models.CharField(max_length=17, null=True, blank=True)
    weight = models.FloatField(null=True)

    # drf results (only some get results data so no import flag)
    win_payoff = models.FloatField(default=0, null=True)
    place_payoff = models.FloatField(default=0, null=True)
    show_payoff = models.FloatField(default=0, null=True)

    # equibase horse_results
    equibase_horse_results_import = models.BooleanField(default=False)
    equibase_speed_rating = models.IntegerField(null=True)
    equibase_horse_entries_import = models.BooleanField(default=False)

    # equibase charts
    comment = models.CharField(max_length=255, null=True)
    
    def clean(self):
        # Choice Field Validation
        if self.scratch_indicator is not None and self.scratch_indicator not in dict(SCRATCH_REASON_CHOICES):
            raise ValidationError(
                _("Invalid scratch indicator: %(value)s"),
                params={'value': self.scratch_indicator},
                code='invalid_choice'
            )
        
        # Individual Field Validation
        if self.program_number is not None and self.program_number == '':
            raise ValidationError(
                _("Invalid program number: %(value)s"),
                params={'value': self.program_number},
                code='invalid_input'
            )
            
        # DRF Entries Import
        if self.drf_entries_import:
            required_fields = {
                'post_position': "post position",
                'trainer': "trainer",
                'jockey': "jockey",
                'scratch_indicator': "scratch indicator",
                'program_number': "program number"
            }
            if self.scratch_indicator and self.scratch_indicator == 'N':
                for field, name in required_fields.items():
                    if not getattr(self, field):
                        raise ValidationError(
                            _("DRF entries import requires valid %(field)s"),
                            params={'field': name},
                            code='missing_input'
                        )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Workouts(models.Model):
    horse = models.ForeignKey(Horses, on_delete=models.CASCADE)
    workout_date = models.DateField()
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)
    surface = models.CharField(max_length=1, choices=RACE_SURFACE, default='D')
    distance = models.FloatField()
    time_seconds = models.FloatField()
    note = models.CharField(max_length=255)
    workout_rank = models.IntegerField()
    workout_total = models.IntegerField()
    
    def clean(self):
        # Choice Field Validation
        if self.surface and self.surface not in dict(RACE_SURFACE):
            raise ValidationError(
                _("Invalid surface: %(value)s"),
                params={'value': self.surface},
                code='invalid_choice'
            )
        
        # Individual Field Validation
        if self.time_seconds <= 0:
            raise ValidationError(
                _("Invalid time_seconds: %(value)s"),
                params={'value': self.time_seconds},
                code='invalid_input'
            )
            
        if self.distance <= 0:
            raise ValidationError(
                _("Invalid distance: %(value)s"),
                params={'value': self.distance},
                code='invalid_input'
            )
            
        if self.workout_rank <= 0:
            raise ValidationError(
                _("Invalid workout_rank: %(value)s"),
                params={'value': self.workout_rank},
                code='invalid_input'
            )
            
        if self.workout_total <= 0:
            raise ValidationError(
                _("Invalid workout_total: %(value)s"),
                params={'value': self.workout_total},
                code='invalid_input'
            )
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Payoffs(models.Model):
    race = models.ForeignKey('Races', on_delete=models.CASCADE)
    wager_type = models.CharField(max_length=2, choices=BET_CHOICES)
    winning_numbers = models.CharField(max_length=255)
    total_pool = models.FloatField(default=0)
    payoff_amount = models.FloatField(default=0)
    base_amount = models.FloatField(default=0)

    def clean(self):
        # Choice Field Validation
        if self.wager_type and self.wager_type not in dict(BET_CHOICES):
            raise ValidationError(
                _("Invalid wager type: %(value)s"),
                params={'value': self.wager_type},
                code='invalid_choice'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class PointsOfCall(models.Model):
    entry = models.ForeignKey(Entries, on_delete=models.CASCADE)
    point = models.IntegerField()
    text = models.CharField(max_length=255)
    distance = models.FloatField()
    position = models.IntegerField()
    lengths_back = models.FloatField()

class FractionalTimes(models.Model):
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    point = models.IntegerField()
    text = models.CharField(max_length=255)
    distance = models.FloatField()
    time = models.FloatField()

class SplitCallVelocities(models.Model):
    entry = models.ForeignKey(Entries, on_delete=models.CASCADE)
    point = models.IntegerField()
    start_distance = models.FloatField()
    end_distance = models.FloatField()
    split_time = models.FloatField()
    total_time = models.FloatField()
    velocity = models.FloatField()
    lengths_back = models.FloatField()
