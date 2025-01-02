from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, F, FloatField
from django.db.models.expressions import ExpressionWrapper
from collections import defaultdict
from horsemen.models import Races, Entries, SplitCallVelocities, PointsOfCall
from .simulate import Simulation
import numpy as np

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
        
        # Prepare velocity data with dates for all races
        velocity_data = [
            {
                'date': v.entry.race.race_date.strftime('%Y-%m-%d'),
                'velocity': v.calculated_velocity
            } for v in velocities
        ]
        
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

def race_simulation(request, race_id):
    race = get_object_or_404(Races, id=race_id)
    simulation = Simulation(race)
    
    # Get actual race results
    race_results = PointsOfCall.objects.filter(
        entry__race=race,
        point=6  # final point of call
    ).select_related('entry', 'entry__horse').order_by('position')
    
    # Prepare data for each horse
    horse_data = []
    for program_number, sim_entry in simulation.simulation_entries.items():
        # Generate points for KDE plot
        kde_data = []
        velocity_data = []
        for point in range(5):
            if sim_entry.kde[point] is not None:
                # Generate points for KDE curve
                x_range = np.linspace(
                    min(sim_entry.same_distance_velocity_by_point[point]),
                    max(sim_entry.same_distance_velocity_by_point[point]),
                    100
                )
                y_values = sim_entry.kde[point].evaluate(x_range)
                
                # Prepare actual velocity points
                point_velocities = sim_entry.same_distance_velocity_by_point[point]
                
                kde_data.append({
                    'point': point,
                    'x_values': x_range.tolist(),
                    'y_values': y_values.tolist(),
                    'velocities': point_velocities
                })
        
        # Calculate win percentages
        finish_percentages = {
            position: (count / simulation.simulation_count * 100) 
            for position, count in sim_entry.simulation_finishes.items()
        }
        
        horse_data.append({
            'program_number': program_number,
            'horse_name': sim_entry.horse.horse_name,
            'kde_data': kde_data,
            'finish_percentages': finish_percentages
        })
    
    # Sort exotic wager results and calculate percentages
    exotic_results = {
        'exactas': [],
        'trifectas': [],
        'superfectas': []
    }
    
    for wager_type in ['exactas', 'trifectas', 'superfectas']:
        results = simulation.results[wager_type]
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        exotic_results[wager_type] = [
            {
                'combination': combo,
                'count': count,
                'percentage': (count / simulation.simulation_count * 100)
            }
            for combo, count in sorted_results[:10]  # Show top 10 combinations
        ]
    
    context = {
        'race': race,
        'horse_data': sorted(horse_data, key=lambda x: -x['finish_percentages'][1]),  # Sort by win percentage
        'exotic_results': exotic_results,
        'simulation_count': simulation.simulation_count,
        'race_results': race_results  # Add race results to context
    }
    
    return render(request, 'horsemen/race_simulation.html', context)
