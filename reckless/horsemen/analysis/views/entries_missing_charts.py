from django.shortcuts import render
from ...models import Entries

def entries_missing_charts(request):
    """
    Display entries that have results but no charts.
    """
    # Find horses with results but no charts
    entries_missing_charts = Entries.objects.filter(
        equibase_horse_results_import=True,
        race__equibase_chart_import=False
    ).select_related(
        'race__track',
        'horse'
    ).order_by('-race__race_date')

    return render(request, 'horsemen/entries_missing_charts.html', {
        'entries_missing_charts': entries_missing_charts
    })
