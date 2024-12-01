from django.shortcuts import render
from django.db.models import Q, Exists, OuterRef
from ...models import Entries, PointsOfCall

def entries_velocity_issues(request):
    """
    Display entries with missing or invalid split call velocities.
    """
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

    return render(request, 'horsemen/entries_velocity_issues.html', {
        'entries_velocity_issues': entries_velocity_issues
    })
