import json
from django.shortcuts import render, redirect
import subprocess
from django.http import HttpResponse

def dashboard(request):
    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
    try:
        with open(data_file_path, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    return render(request, 'outreach/dashboard.html', {'users': users})

def run_outreach(request):
    try:
        subprocess.run(
            ['c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\insta-bot-venv\\Scripts\\python.exe', 'main.py'],
            check=True,
            cwd='c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation'
        )
        return HttpResponse(status=200)
    except subprocess.CalledProcessError as e:
        return HttpResponse(status=500)

def clear_users(request):
    data_file_path = 'c:\\Users\\Youssef.Chaker\\Desktop\\Instagram-bot-automation\\data\\scraped_users.json'
    with open(data_file_path, 'w') as f:
        json.dump([], f)
    return redirect('outreach:dashboard')

def remove_user(request, username):
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
