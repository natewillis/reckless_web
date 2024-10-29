from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('core:home')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'core/login.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('core:home')
    return redirect('core:home')
