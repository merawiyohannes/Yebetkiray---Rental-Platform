from django.urls import path
from . import views

urlpatterns = [
    path('<int:property_id>/upgrade-featured/', 
         views.upgrade_featured, name='upgrade_featured'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('return/', views.payment_return, name='payment_return'),
]