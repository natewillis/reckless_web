from django.shortcuts import render
from django.db.models import Q
from ...models import Horses, Workouts

def horses_without_workouts(request):
    """
    Display horses that are missing workout data.
    """
    # Find horses without workouts
    horses_without_workouts = Horses.objects.filter(
        Q(entries__equibase_horse_results_import=True) |
        Q(entries__equibase_horse_entries_import=True)
    ).exclude(
        id__in=Workouts.objects.values('horse')
    ).distinct()

    return render(request, 'horsemen/horses_without_workouts.html', {
        'horses_without_workouts': horses_without_workouts
    })
