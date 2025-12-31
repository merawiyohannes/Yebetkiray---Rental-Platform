from django.urls import path
from . import views

urlpatterns = [
    path('detail/<int:id>', views.detail_view, name='detail_view'),
    path('', views.property_create_view, name="property_create_view"),
    path('edit/<int:pk>/', views.property_edit_view, name="property_edit_view"),
    path('image/delete/<int:pk>/', views.delete_property_image, name='delete_property_image'),
    path('delete/<int:pk>', views.delete_property, name='delete_view'),
    path('<int:pk>/upload-image/', views.upload_property_image, name='upload_image'),
    path('admin/verify/', views.admin_verify_view, name='admin_verify'),
    path('admin/verify/<int:property_id>/', views.verify_property_view, name='verify_property'),
    path('admin/reject/<int:property_id>/', views.reject_property_view, name='reject_property'),
    path('review/reply/<int:id>/', views.add_reply_view, name='add_reply'),    
]
