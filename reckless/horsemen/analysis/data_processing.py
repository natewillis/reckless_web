from horsemen.constants import METERS_PER_FURLONG, METERS_PER_LENGTH
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from django.db.models import Q
from horsemen.models import Entries, FractionalTimes, PointsOfCall, SplitCallVelocities
import logging

logger = logging.getLogger(__name__)


def get_position_velocity_array_from_fractions_and_points_of_call(fractions, points_of_call, num_points=5):
    """Calculate velocity array from fractional times and points of call."""
    try:
        logger.debug(f"Starting velocity calculation with {len(fractions)} fractions, {len(points_of_call)} points")
        
        # get the race distance (everything in meters)
        race_distance = fractions.last().distance * METERS_PER_FURLONG
        
        # get the array of distances based on num points
        evaluation_distances = np.linspace(0, race_distance, num_points+1)
        
        # points of call data formatting
        horse_lb_distance=[0]
        horse_lb=[0]
        for point_of_call in points_of_call:
            if point_of_call.distance > 0:
                horse_lb_distance.append(point_of_call.distance * METERS_PER_FURLONG)
                horse_lb.append(point_of_call.lengths_back * METERS_PER_LENGTH if point_of_call.position > 1 else 0)
        
        # fractional data formatting
        fractional_distances = [0]
        fractional_times = [0]
        for fraction in fractions:
            fractional_distances.append(fraction.distance * METERS_PER_FURLONG)
            fractional_times.append(fraction.time)
            
        logger.debug(f"Data prepared - Distances: {len(fractional_distances)}, Times: {len(fractional_times)}")
            
        # get horses lengths back from leader at each interval
        horse_lb_at_distance = np.interp(
            evaluation_distances,
            horse_lb_distance,
            horse_lb
        )
        
        # get leaders position when horse is crossing each interval
        leader_distance_at_horse_distance = np.array(evaluation_distances) + horse_lb_at_distance
        
        # must use a spline to do the extrapolation in case the horse inst the leader
        # and leader distance is longer than the race distance
        fractional_distance_time_spline = InterpolatedUnivariateSpline(
            fractional_distances,
            fractional_times,
            k=1 # linear extrapolation
        )
        
        # get leaders time at those positions (which is the horses time at the intervals)
        horse_times = fractional_distance_time_spline(leader_distance_at_horse_distance)

        # get velocity
        horse_velocities = (evaluation_distances[1]-evaluation_distances[0]) / np.diff(horse_times)

        if np.max(horse_velocities) > 30:
            logger.error(f'bad velocity calculate for {points_of_call.first().entry}, distance: {race_distance}, fracs:{fractional_times}, horse_lb: {horse_lb}, horse_lb_distance: {horse_lb_distance}')
        
        logger.debug(f"Velocity calculation complete - {len(horse_velocities)} points")
        return horse_velocities, horse_times, horse_lb_at_distance, evaluation_distances
        
    except Exception as e:
        logger.error(f"Velocity calculation error: {str(e)}", exc_info=True)
        raise


def calculate_split_call_velocities(recalculate_all=False):
    """
    Calculate split call velocities for entries that don't have them.
    
    Args:
        recalculate_all (bool): If True, delete all existing velocities and recalculate them.
    """
    try:
        if recalculate_all:
            count = SplitCallVelocities.objects.all().count()
            logger.info(f"Deleting {count} existing velocities")
            SplitCallVelocities.objects.all().delete()
        
        # Get entries that need velocities calculated
        entries = Entries.objects.filter(
            pointsofcall__isnull=False,
            race__fractionaltimes__isnull=False
        ).distinct()
        
        total_entries = entries.count()
        logger.info(f"Processing {total_entries} entries")
        
        success_count = 0
        error_count = 0
        
        for i, entry in enumerate(entries, 1):
            try:
                # Get fractional times
                fractions = FractionalTimes.objects.filter(
                    race=entry.race
                ).order_by('point')
                
                if not fractions:
                    logger.warning(f"Entry {entry.id}: No fractional times")
                    continue
                    
                # Get points of call
                points_of_call = PointsOfCall.objects.filter(
                    entry=entry
                ).order_by('point')
                
                if not points_of_call:
                    logger.warning(f"Entry {entry.id}: No points of call")
                    continue
                
                logger.debug(f"Entry {entry.id}: Processing with {len(fractions)} fractions, {len(points_of_call)} points")
                
                # Calculate velocities
                velocities, times, lengths_back, distances = get_position_velocity_array_from_fractions_and_points_of_call(
                    fractions,
                    points_of_call
                )
                
                # Create velocity records
                for i, velocity in enumerate(velocities):

                    # get start and end distance of this fraction
                    start_distance = distances[i] if i < len(distances) else distances[-1]
                    end_distance = distances[i+1] if i+1 < len(distances) else distances[-1]

                    # Calculate split time and total time
                    split_time = times[i+1] - times[i] if i+1 < len(times) else 0
                    total_time = times[i+1] if i+1 < len(times) else 0
                    
                    # Calculate lengths back
                    current_lengths_back = lengths_back[i+1] if i+1 < len(times) else 0
                    
                    SplitCallVelocities.objects.create(
                        entry=entry,
                        point=i,
                        start_distance=start_distance,
                        end_distance=end_distance,
                        split_time=split_time,
                        total_time=total_time,
                        velocity=velocity,
                        lengths_back=current_lengths_back
                    )

                success_count += 1
                if i % 100 == 0:
                    logger.info(f"Processed {i}/{total_entries} entries")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Entry {entry.id} error: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Complete - Processed: {total_entries}, Success: {success_count}, Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise
