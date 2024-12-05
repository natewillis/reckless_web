from django.shortcuts import render
from ...models import Races, FractionalTimes

def races_without_fractions(request):
    """
    Display races that are missing fractional times, excluding Quarter Horse races
    and races with hurdles.
    """
    # Find races without fractional times, excluding Quarter Horse races and hurdle races
    races_without_fractions = Races.objects.filter(
        equibase_chart_import=True,
        cancelled=False
    ).exclude(
        id__in=FractionalTimes.objects.values('race')
    ).exclude(
        breed='QH'  # Exclude Quarter Horse races
    ).exclude(
        hurdles=True  # Exclude races with hurdles
    ).select_related('track').order_by('-race_date')

    return render(request, 'horsemen/races_without_fractions.html', {
        'races_without_fractions': races_without_fractions
    })
