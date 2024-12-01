from django.shortcuts import render
from ...models import Entries, PointsOfCall

def entries_without_points(request):
    """
    Display entries that are missing points of call data.
    """
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

    return render(request, 'horsemen/entries_without_points.html', {
        'entries_without_points': entries_without_points
    })
