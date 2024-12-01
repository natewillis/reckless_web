from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from ..models import Tracks, Races

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
