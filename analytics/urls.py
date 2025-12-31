from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard_view'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
