from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from .models import Tracks, Races, Entries

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
