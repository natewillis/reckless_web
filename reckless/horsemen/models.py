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
    
    def get_drf_results_url_for_date(self, race_date):
        return f'https://www.drf.com/results/resultDetails/id/{self.code}/country/{self.country}/date/{race_date.strftime('%m-%d-%Y')}'
    
    def get_drf_entries_url_for_date(self, race_date):
        return f"https://www.drf.com/entries/entryDetails/id/{self.code}/country/{self.country}/date/{race_date.strftime('%m-%d-%Y')}"
    
    def get_equibase_chart_url_for_date(self, race_date):
        return f'https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID={self.code}&CTRY={self.country}&DT={race_date.strftime('%m/%d/%Y')}&DAY=D&STYLE=EQB'
        

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

    def clean(self):
        
        # Individual Field Validation
        if self.distance is not None:
            if self.distance>32 or self.distance<=0:
                raise ValidationError(
                    _("Invalid distance: : %(value)"),
                    params={'value': self.distance},
                    code='invalid_input'
                )
                
        if self.condition:
            if len(self.condition) < 3:
                raise ValidationError(
                    _("Invalid condition: : %(value)"),
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
            if not self.race_type:
                raise ValidationError(
                    _("DRF results import requires valid race_type"),
                    code='missing_input'
                )
            if not self.age_restriction:
                raise ValidationError(
                    _("DRF results import requires valid age restriction"),
                    code='missing_input'
                )
            if not self.sex_restriction:
                raise ValidationError(
                    _("DRF results import requires valid sex restriction"),
                    code='missing_input'
                )
            if self.minimum_claiming_price is None:
                raise ValidationError(
                    _("DRF results import requires valid minimum claiming price"),
                    code='missing_input'
                )
            if self.maximum_claiming_price is None:
                raise ValidationError(
                    _("DRF results import requires valid maximum claiming price"),
                    code='missing_input'
                )
            if not self.distance:
                raise ValidationError(
                    _("DRF results import requires valid distance"),
                    code='missing_input'
                )
            if not self.purse:
                raise ValidationError(
                    _("DRF results import requires valid purse"),
                    code='missing_input'
                )
            if not self.breed:
                raise ValidationError(
                    _("DRF results import requires valid breed"),
                    code='missing_input'
                )
            if not self.race_surface:
                raise ValidationError(
                    _("DRF results import requires valid surface"),
                    code='missing_input'
                )
            if not self.condition:
                raise ValidationError(
                    _("DRF results import requires track condition"),
                    code='missing_input'
                )
        
        # DRF Results Import
        if self.equibase_chart_import:
            if not self.age_restriction:
                raise ValidationError(
                    _("Equibase chart import requires valid age restriction"),
                    code='missing_input'
                )
            if not self.sex_restriction:
                raise ValidationError(
                    _("Equibase chart  import requires valid sex restriction"),
                    code='missing_input'
                )
            if not self.distance:
                raise ValidationError(
                    _("Equibase chart import requires valid distance"),
                    code='missing_input'
                )
            if not self.purse:
                raise ValidationError(
                    _("Equibase chart import requires valid purse"),
                    code='missing_input'
                )
            if not self.breed:
                raise ValidationError(
                    _("Equibase chart import requires valid breed"),
                    code='missing_input'
                )
            if not self.race_surface:
                raise ValidationError(
                    _("Equibase chart import requires valid surface"),
                    code='missing_input'
                )
            if not self.condition:
                raise ValidationError(
                    _("Equibase chart import requires track condition"),
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
    dam_sire = models.ForeignKey('Horses', on_delete=models.CASCADE, null=True, related_name= 'grandchildren')

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
        
        # Individual Field Validation
        if self.registration_number and self.registration_number == '':
            raise ValidationError(
                _("Invalid horse registration number: %(value)"),
                params={'value': self.registration_number},
                code='missing_input'
            )
        if self.equibase_horse_id and self.equibase_horse_id <= 0:
            raise ValidationError(
                _("Invalid horse equibase horse id number: %(value)"),
                params={'value': self.equibase_horse_id},
                code='missing_input'
            )
        if self.equibase_horse_id:
            if not self.equibase_horse_type:
                raise ValidationError(
                    _("Required equibase_horse_type"),
                    code='missing_input'
                )
            elif len(self.equibase_horse_type) < 2:
                 raise ValidationError(
                    _("Invalid equibase_horse_type: %(value)"),
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
                    _("Invalid equibase_horse_registry: %(value)"),
                    params={'value': self.equibase_horse_registry},
                    code='invalid_input'
                )
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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
    
    def clean(self):
        
        # Individual Field Validation
        if self.drf_jockey_id and self.drf_jockey_id == '':
            raise ValidationError(
                _("Invalid drf_jockey_id: %(value)"),
                params={'value': self.drf_jockey_id},
                code='missing_input'
            )
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
    
    def clean(self):
        
        # Individual Field Validation
        if self.drf_trainer_id and self.drf_trainer_id == '':
            raise ValidationError(
                _("Invalid drf_trainer_id: %(value)"),
                params={'value': self.drf_trainer_id},
                code='missing_input'
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
        
        # individual field logic
        # post position
        if self.program_number and self.program_number == '':
            raise ValidationError(
                _("Invalid program number: %(value)"),
                params={'value': self.program_number},
                code='invalid_input'
            )
            
        # drf entries
        if self.drf_entries_import:
            if not self.post_position:
                raise ValidationError(
                    _("Required post_position"),
                    code='missing_input'
                )
            if not self.trainer:
                raise ValidationError(
                    _("Required trainer"),
                    code='missing_input'
                )
            if not self.jockey:
                raise ValidationError(
                    _("Required jockey"),
                    code='missing_input'
                )
            if not self.scratch_indicator:
                raise ValidationError(
                    _("Required scratch_indicator"),
                    code='missing_input'
                )
            if self.medication is None:
                raise ValidationError(
                    _("Required medication"),
                    code='missing_input'
                )
            if self.equipment is None:
                raise ValidationError(
                    _("Required equipment"),
                    code='missing_input'
                )
            if not self.weight:
                raise ValidationError(
                    _("Required weight"),
                    code='missing_input'
                )
            if not self.program_number:
                raise ValidationError(
                    _("Required program number"),
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
        
        # individual field logic
        if self.time_seconds <= 0:
            raise ValidationError(
                _("Invalid time_seconds: %(value)"),
                params={'value': self.time_seconds},
                code='invalid_input'
            )
        if self.distance <= 0:
            raise ValidationError(
                _("Invalid distance: %(value)"),
                params={'value': self.distance},
                code='invalid_input'
            )
        if self.workout_rank <= 0:
            raise ValidationError(
                _("Invalid workout_rank: %(value)"),
                params={'value': self.workout_rank},
                code='invalid_input'
            )
        if self.workout_total <= 0:
            raise ValidationError(
                _("Invalid workout_total: %(value)"),
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
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    point = models.IntegerField()
    start_distance = models.FloatField()
    end_distance = models.FloatField()
    split_time = models.FloatField()
    total_time = models.FloatField()
    velocity = models.FloatField()
    lengths_back = models.FloatField()

