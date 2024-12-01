from django.shortcuts import render

def data_quality(request):
    """
    Display data quality analysis landing page.
    """
    return render(request, 'horsemen/data_quality.html')
