from django.shortcuts import render
from django.http import JsonResponse
from ...models import SplitCallVelocities
import math

def velocity_histogram(request):
    """
    Display the velocity histogram visualization.
    """
    return render(request, 'horsemen/velocity_histogram.html')

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
