import json
import os
import subprocess
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session['instagram_username'] = username
        request.session['instagram_password'] = password
                
        base_url = reverse('outreach:dashboard')
        query_string = urlencode({'success': 'You have been logged in successfully.'})
        return redirect(f'{base_url}?{query_string}')
            
    return render(request, 'outreach/login.html')
        
        
def logout_view(request):
    request.session.flush()
    
    data_file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'scraped_users.json')
    with open(data_file_path, 'w') as f:
        json.dump([], f)
        
    base_url = reverse('outreach:login')
    query_string = urlencode({'success': 'You have been logged out successfully.'})
    return redirect(f'{base_url}?{query_string}')

def dashboard(request):
    if 'instagram_username' not in request.session:
        return redirect('outreach:login')

    data_file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'scraped_users.json')
    try:
        with open(data_file_path, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    return render(request, 'outreach/dashboard.html', {'users': users})

def run_outreach(request):
    if 'instagram_username' not in request.session:
        return HttpResponse(status=401)

    try:
        subprocess.run(
            [os.path.join(settings.BASE_DIR, '..', 'insta-bot-venv', 'Scripts', 'python.exe'), 'main.py'],
            check=True,
            cwd=os.path.join(settings.BASE_DIR, '..'),
            env={
                **os.environ,
                'INSTAGRAM_USERNAME': request.session['instagram_username'],
                'INSTAGRAM_PASSWORD': request.session['instagram_password'],
            }
        )
        return HttpResponse(status=200)
    except subprocess.CalledProcessError as e:
        return HttpResponse(status=500)

def clear_users(request):
    if 'instagram_username' not in request.session:
        return redirect('outreach:login')

    data_file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'scraped_users.json')
    with open(data_file_path, 'w') as f:
        json.dump([], f)
    base_url = reverse('outreach:dashboard')
    query_string = urlencode({'success': 'All users have been cleared successfully.'})
    return redirect(f'{base_url}?{query_string}')

def remove_user(request, username):
    if 'instagram_username' not in request.session:
        return redirect('outreach:login')

    data_file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'scraped_users.json')
    try:
        with open(data_file_path, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    users = [user for user in users if user['username'] != username]

    with open(data_file_path, 'w') as f:
        json.dump(users, f, indent=4)

    base_url = reverse('outreach:dashboard')
    query_string = urlencode({'success': f'User {username} has been removed successfully.'})
    return redirect(f'{base_url}?{query_string}')
