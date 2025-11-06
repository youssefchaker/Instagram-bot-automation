import json
import os
import subprocess
from django.http import HttpResponse
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # For now, we'll just store the credentials in the session
        # In a real application, you'd want to properly authenticate
        request.session['instagram_username'] = username
        request.session['instagram_password'] = password
        
        return redirect('outreach:dashboard')
    
    return render(request, 'outreach/login.html')

def logout_view(request):
    # Clear the session
    request.session.flush()
    
    # Clear the scraped_users.json file
    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
    with open(data_file_path, 'w') as f:
        json.dump([], f)
        
    return redirect('outreach:login')

def dashboard(request):
    if 'instagram_username' not in request.session:
        return redirect('outreach:login')

    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
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
            ['c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\insta-bot-venv\\Scripts\\python.exe', 'main.py'],
            check=True,
            cwd='c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation',
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

    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
    with open(data_file_path, 'w') as f:
        json.dump([], f)
    return redirect('outreach:dashboard')

def remove_user(request, username):
    if 'instagram_username' not in request.session:
        return redirect('outreach:login')

    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
    try:
        with open(data_file_path, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    users = [user for user in users if user['username'] != username]

    with open(data_file_path, 'w') as f:
        json.dump(users, f, indent=4)

    return redirect('outreach:dashboard')
