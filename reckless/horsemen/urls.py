from django.urls import path
from .common.views import home
from .data_collection.views import (
    race_detail,
    past_performance,
    data_collection_report
)
from .analysis.views import (
    analysis_home,
    velocity_histogram,
    velocity_data,
    workout_velocity_histogram,
    workout_velocity_data,
    data_quality,
    races_without_fractions,
    entries_velocity_issues,
    entries_without_points,
    entries_missing_charts,
    horses_without_workouts
)

app_name = 'horsemen'

urlpatterns = [
    # Common views
    path('', home, name='home'),
    
    # Data collection views
    path('race/<int:race_id>/', race_detail, name='race_detail'),
    path('race/<int:race_id>/past-performance/', past_performance, name='past_performance'),
    path('data-collection-report/', data_collection_report, name='data_collection_report'),
    
    # Analysis views
    path('analysis/', analysis_home, name='analysis_home'),
    path('analysis/velocity-histogram/', velocity_histogram, name='velocity_histogram'),
    path('analysis/workout-velocity-histogram/', workout_velocity_histogram, name='workout_velocity_histogram'),
    
    # Data quality views
    path('analysis/data-quality/', data_quality, name='data_quality'),
    path('analysis/data-quality/races-without-fractions/', races_without_fractions, name='races_without_fractions'),
    path('analysis/data-quality/entries-velocity-issues/', entries_velocity_issues, name='entries_velocity_issues'),
    path('analysis/data-quality/entries-without-points/', entries_without_points, name='entries_without_points'),
    path('analysis/data-quality/entries-missing-charts/', entries_missing_charts, name='entries_missing_charts'),
    path('analysis/data-quality/horses-without-workouts/', horses_without_workouts, name='horses_without_workouts'),
    
    # API endpoints
    path('api/velocity-data/', velocity_data, name='velocity_data'),
    path('api/workout-velocity-data/', workout_velocity_data, name='workout_velocity_data'),
]
