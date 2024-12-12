from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, F, FloatField
from django.db.models.expressions import ExpressionWrapper
from collections import defaultdict
from horsemen.models import Races, Entries, SplitCallVelocities, PointsOfCall

def race_analysis(request, race_id):
    race = get_object_or_404(Races, id=race_id)
    entries = Entries.objects.filter(race=race)
    
    horse_data = []
    for entry in entries:
        # Get velocity data for point 4 (finish) with race dates
        velocities = SplitCallVelocities.objects.filter(
            entry__horse=entry.horse,
            point=4
        ).select_related('entry__race').annotate(
            calculated_velocity=ExpressionWrapper(
                F('end_distance') / F('total_time'),
                output_field=FloatField()
            )
        )
        print(f'number of velocities {len(velocities)}')
        
        # Prepare velocity data with dates for all races
        velocity_data = [
            {
                'date': v.entry.race.race_date.strftime('%Y-%m-%d'),
                'velocity': v.calculated_velocity
            } for v in velocities
        ]
        print(velocity_data)
        
        # Prepare velocity data with dates for same distance races
        same_distance_velocity_data = [
            {
                'date': v.entry.race.race_date.strftime('%Y-%m-%d'),
                'velocity': v.calculated_velocity
            } for v in velocities if v.entry.race.distance == race.distance
        ]
        
        # Get finish positions for all races and count occurrences
        finish_positions = PointsOfCall.objects.filter(
            entry__horse=entry.horse,
            point=6  # final point of call
        ).values('position').annotate(count=Count('position')).order_by('position')
        
        # Convert to format suitable for chart
        position_counts = defaultdict(int)
        for pos in finish_positions:
            position_counts[pos['position']] = pos['count']
        
        # Create lists for chart data
        positions = list(range(1, max(position_counts.keys()) + 1)) if position_counts else []
        counts = [position_counts[pos] for pos in positions]
        
        horse_data.append({
            'horse_name': entry.horse.horse_name,
            'velocity_data': velocity_data,
            'same_distance_velocity_data': same_distance_velocity_data,
            'finish_positions': positions,
            'finish_position_counts': counts,
            'post_position': entry.post_position,
            'program_number': entry.program_number
        })
    
    context = {
        'race': race,
        'horse_data': horse_data
    }
    
    return render(request, 'horsemen/race_analysis.html', context)
