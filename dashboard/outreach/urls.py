from django.urls import path
from . import views

app_name = 'outreach'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('run_outreach/', views.run_outreach, name='run_outreach'),
    path('clear_users/', views.clear_users, name='clear_users'),
    path('remove_user/<str:username>/', views.remove_user, name='remove_user'),
]
