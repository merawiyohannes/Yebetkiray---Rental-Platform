from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search_view'),
    path('search-ajax/', views.search_ajax, name='search_ajax'),
]
