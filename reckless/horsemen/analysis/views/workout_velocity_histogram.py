from django.shortcuts import render
from django.http import JsonResponse
from ...models import Workouts
import math

# Constants for unit conversion
FURLONG_TO_METERS = 201.168  # 1 furlong = 201.168 meters

def workout_velocity_histogram(request):
    """
    Display the workout velocity histogram visualization.
    """
    return render(request, 'horsemen/workout_velocity_histogram.html')

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
