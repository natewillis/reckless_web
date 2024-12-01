from django.shortcuts import render

def analysis_home(request):
    """
    Display the analysis home page.
    """
    return render(request, 'horsemen/analysis_home.html')
