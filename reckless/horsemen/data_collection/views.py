from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from ..models import Races, Entries, FractionalTimes, Workouts

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
