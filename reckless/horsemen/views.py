from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch, Count, Q, Max, Exists, OuterRef
from django.http import JsonResponse
from .models import Tracks, Races, Entries, PointsOfCall, FractionalTimes, Workouts, Horses, SplitCallVelocities
import math

# Constants for unit conversion
FURLONG_TO_METERS = 201.168  # 1 furlong = 201.168 meters

def home(request):
    # Get date range
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # Get tracks with races in the date range
    tracks = Tracks.objects.prefetch_related(
        Prefetch(
            'races_set',
            queryset=Races.objects.filter(
                race_date__gte=seven_days_ago
            ).order_by('race_date', 'race_number'),
            to_attr='recent_races'
        )
    ).filter(
        races__race_date__gte=seven_days_ago
    ).distinct()
    
    return render(request, 'horsemen/home.html', {
        'tracks': tracks
    })

def race_detail(request, race_id):
    # Get race with related track
    race = get_object_or_404(Races.objects.select_related('track'), id=race_id)
    
    # Get entries with related horses, jockeys, and trainers
    entries = Entries.objects.filter(race=race).select_related(
        'horse',
        'jockey',
        'trainer'
    ).order_by('post_position')
    
    return render(request, 'horsemen/race_detail.html', {
        'race': race,
        'entries': entries
    })

def past_performance(request, race_id):
    """
    Display past performance view for a race showing detailed entry information.
    """
    # Get race with related track
    race = get_object_or_404(
        Races.objects.select_related('track'),
        id=race_id
    )
    
    # Get entries with all related data
    entries = Entries.objects.filter(race=race).select_related(
        'horse',
        'jockey',
        'trainer'
    ).prefetch_related(
        # Get past entries for each horse
        Prefetch(
            'horse__entries_set',
            queryset=Entries.objects.filter(
                race__race_date__lt=race.race_date
            ).select_related(
                'race',
                'race__track'
            ).prefetch_related(
                'pointsofcall_set'
            ).order_by('-race__race_date'),
            to_attr='past_entries'
        ),
        # Get workouts for each horse
        Prefetch(
            'horse__workouts_set',
            queryset=Workouts.objects.filter(
                workout_date__lt=race.race_date
            ).select_related('track').order_by('-workout_date'),
            to_attr='recent_workouts'
        ),
        # Get points of call for entry
        'pointsofcall_set'
    ).order_by('program_number')

    # Get fractional times for the race
    fractional_times = FractionalTimes.objects.filter(race=race).order_by('point')
    
    return render(request, 'horsemen/past_performance.html', {
        'race': race,
        'entries': entries,
        'fractional_times': fractional_times
    })

def data_collection_report(request):
    """
    Display data collection report for tomorrow's AQU races.
    """
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Get all entries for tomorrow's AQU races
    entries = Entries.objects.filter(
        race__track__code='AQU',
        race__race_date=tomorrow
    ).select_related(
        'race',
        'horse'
    ).prefetch_related(
        # Get past entries counts
        Prefetch(
            'horse__entries_set',
            queryset=Entries.objects.filter(
                race__race_date__lt=tomorrow
            ),
            to_attr='past_entries'
        ),
        # Get past entries with charts
        Prefetch(
            'horse__entries_set',
            queryset=Entries.objects.filter(
                race__race_date__lt=tomorrow,
                race__equibase_chart_import=True
            ),
            to_attr='past_entries_with_charts'
        ),
        # Get workouts
        Prefetch(
            'horse__workouts_set',
            queryset=Workouts.objects.all(),
            to_attr='all_workouts'
        )
    ).order_by(
        'race__race_number',
        'program_number'
    )
    
    return render(request, 'horsemen/data_collection_report.html', {
        'entries': entries,
        'report_date': tomorrow
    })

def analysis_home(request):
    """
    Display the analysis home page.
    """
    return render(request, 'horsemen/analysis_home.html')

def velocity_histogram(request):
    """
    Display the velocity histogram visualization.
    """
    return render(request, 'horsemen/velocity_histogram.html')

def workout_velocity_histogram(request):
    """
    Display the workout velocity histogram visualization.
    """
    return render(request, 'horsemen/workout_velocity_histogram.html')

def data_quality(request):
    """
    Display data quality analysis page.
    """
    # Find races without fractional times
    races_without_fractions = Races.objects.filter(
        equibase_chart_import=True,
        cancelled=False
    ).exclude(
        id__in=FractionalTimes.objects.values('race')
    ).select_related('track').order_by('-race_date')

    # Find entries with missing/invalid split call velocities
    entries_with_poc = Entries.objects.filter(
        race__equibase_chart_import=True,
        race__cancelled=False,
        scratch_indicator='N'
    ).filter(
        Exists(PointsOfCall.objects.filter(entry=OuterRef('pk')))
    )

    entries_velocity_issues = entries_with_poc.filter(
        Q(splitcallvelocities=None) |  # No velocities
        Q(splitcallvelocities__velocity__gt=22)  # Velocities > 22 m/s
    ).distinct().select_related(
        'race__track',
        'horse'
    ).prefetch_related('splitcallvelocities_set').order_by('-race__race_date')

    # Find entries without points of call
    entries_without_points = Entries.objects.filter(
        race__equibase_chart_import=True,
        race__cancelled=False,
        scratch_indicator='N'
    ).exclude(
        id__in=PointsOfCall.objects.values('entry')
    ).select_related(
        'race__track',
        'horse'
    ).order_by('-race__race_date')

    # Find horses with results but no charts
    entries_missing_charts = Entries.objects.filter(
        equibase_horse_results_import=True,
        race__equibase_chart_import=False
    ).select_related(
        'race__track',
        'horse'
    ).order_by('-race__race_date')

    # Find horses without workouts
    horses_without_workouts = Horses.objects.filter(
        Q(entries__equibase_horse_results_import=True) |
        Q(entries__equibase_horse_entries_import=True)
    ).exclude(
        id__in=Workouts.objects.values('horse')
    ).distinct()

    return render(request, 'horsemen/data_quality.html', {
        'races_without_fractions': races_without_fractions,
        'entries_velocity_issues': entries_velocity_issues,
        'entries_without_points': entries_without_points,
        'entries_missing_charts': entries_missing_charts,
        'horses_without_workouts': horses_without_workouts
    })

def is_valid_velocity(v):
    """Helper function to validate velocity values"""
    try:
        v_float = float(v)
        return v_float is not None and not math.isinf(v_float) and not math.isnan(v_float) and -100 < v_float < 100
    except (TypeError, ValueError):
        return False

def velocity_data(request):
    """
    JSON endpoint that returns velocity data and outliers.
    """
    point_filter = request.GET.get('point')
    
    # Query all velocities with related data
    velocities_query = SplitCallVelocities.objects.select_related(
        'entry__horse',
        'entry__race__track'
    ).filter(velocity__isnull=False)

    if point_filter:
        try:
            point_filter = int(point_filter)
            velocities_query = velocities_query.filter(point=point_filter)
        except (TypeError, ValueError):
            pass

    # Get distinct points for the selector
    points = list(SplitCallVelocities.objects.values_list('point', flat=True)
                 .distinct().order_by('point'))

    # Get velocities and outliers
    velocities = []
    outliers = []
    
    for v in velocities_query:
        if is_valid_velocity(v.velocity):
            v_float = float(v.velocity)
            if v_float > 30:  # 30 meters per second threshold
                outliers.append({
                    'velocity': round(v_float, 2),
                    'point': v.point,
                    'horse': v.entry.horse.horse_name,
                    'race_date': v.entry.race.race_date.strftime('%Y-%m-%d'),
                    'track': v.entry.race.track.name,
                    'race_number': v.entry.race.race_number
                })
            else:
                velocities.append(round(v_float, 2))

    return JsonResponse({
        'velocities': velocities,
        'outliers': outliers,
        'points': points
    })

def workout_velocity_data(request):
    """
    JSON endpoint that returns workout velocity data.
    """
    distance_filter = request.GET.get('distance')
    
    # Query all workouts
    workouts_query = Workouts.objects.all()

    if distance_filter:
        try:
            distance_filter = float(distance_filter)
            workouts_query = workouts_query.filter(distance=distance_filter)
        except (TypeError, ValueError):
            pass

    # Get distinct distances for the selector
    distances = list(Workouts.objects.values_list('distance', flat=True)
                    .distinct().order_by('distance'))

    # Calculate velocities (convert furlongs to meters)
    velocities = []
    
    for w in workouts_query:
        # Convert distance to meters and time to seconds
        distance_meters = w.distance * FURLONG_TO_METERS
        
        # Calculate velocity in meters per second
        velocity = distance_meters / w.time_seconds
        
        if not math.isinf(velocity) and not math.isnan(velocity):
            velocities.append(round(velocity, 2))

    return JsonResponse({
        'velocities': velocities,
        'distances': distances
    })
