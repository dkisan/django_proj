# MainApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('upload/', views.upload_csv, name='upload_csv'),
    # Add other URL patterns as needed
]
