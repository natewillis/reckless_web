from django.db.models import F, FloatField, Avg, Count, StdDev
from horsemen.models import Entries, SplitCallVelocities, Workouts
from django.db.models.expressions import ExpressionWrapper
from scipy.stats import gaussian_kde
import numpy as np
from horsemen.constants import METERS_PER_FURLONG, METERS_PER_LENGTH


MONTE_CARLO_RACE_COUNT = 1000

class Simulation:
    def __init__(self, race, num_points=5):
        
        # store race
        self.race = race

        # create a simulation entry
        self.simulation_entries = {}
        for entry in race.entries_set.all():
            if not entry.scratched and entry.program_number:
                self.simulation_entries[entry.program_number] = SimulationEntry(entry)

        # setup sim data
        race_distance = self.race.distance * METERS_PER_FURLONG
        evaluation_distances, simulation_step_distance = np.linspace(0, race_distance, num_points+1, retstep=True)
        evaluation_distances = evaluation_distances[1:]

        # run monte carlo
        for simulation_number in range(MONTE_CARLO_RACE_COUNT):

            # store time it takes to race
            finish_times = {}
            for program_number in self.simulation_entries.keys():
                finish_times[program_number] = 0

            for point, end_distance in enumerate(evaluation_distances):
                for program_number, simulation_entry in self.simulation_entries.items():

                    # get a velocity from the de
                    kde = simulation_entry.kde[point]
                    random_velocity = kde.resample(size=1)[0]

                    # calculate time
                    finish_times[program_number] += simulation_step_distance / random_velocity

            # Sort finish_times by value (finish times)
            sorted_finish_times = sorted(finish_times.items(), key=lambda item: item[1])

            # Iterate through the first four horses and update their finish places
            for finish_index, (program_number, finish_time) in enumerate(sorted_finish_times[:3], start=0):
                # Increment the corresponding simulation finish counter
                self.simulation_entries[program_number].simulation_finishes[finish_index+1] += 1




class SimulationEntry:
    def __init__(self, entry):

        # base data
        self.entry = entry
        self.horse = entry.horse
        self.race = entry.race

        # simulation data
        self.simulation_finishes = {
            1: 0,
            2: 0,
            3: 0,
            4: 0
        }
        
        # Get all previous entries for this horse
        self.previous_entries = Entries.objects.filter(
            horse=self.horse,
            race__race_date__lt=self.race.race_date
        ).select_related('race').order_by('-race__race_date')
        
        # Get all previous split call velocities
        self.previous_split_call_velocities = SplitCallVelocities.objects.filter(
            entry__in=self.previous_entries
        ).order_by('entry__race__race_date', 'point')
        
        # Organize velocities by point
        self.velocity_by_point = {}
        self.same_distance_velocity_by_point = {}
        for point in range(5):
            self.velocity_by_point[point] = []
            self.same_distance_velocity_by_point[point] = []
        for velocity in self.previous_split_call_velocities:
            self.velocity_by_point[velocity.point].append(velocity.velocity)
            if abs(velocity.entry.race.distance - self.race.distance)/self.race.distance < 0.1:
                self.same_distance_velocity_by_point[velocity.point].append(velocity.velocity)

        # Get workout velocity
        self.workout_stats = Workouts.objects.filter(
            horse=self.horse,
            workout_date__lt=self.race.race_date
        ).annotate(
            calculated_velocity=ExpressionWrapper(
                F('distance') / F('time_seconds'),
                output_field=FloatField()
            )
        ).aggregate(
            average_velocity=Avg('calculated_velocity'),
            standard_deviation=StdDev('calculated_velocity'),
            count=Count('calculated_velocity')
        )

        # create guassian Kernel Density Estimation 
        self.kde = {}
        for point in self.same_distance_velocity_by_point.keys():
            velocities = self.same_distance_velocity_by_point[point]
            if len(velocities)<2:
                self.kde[point] = None
            else:
                self.kde[point] = gaussian_kde(np.array(velocities))

