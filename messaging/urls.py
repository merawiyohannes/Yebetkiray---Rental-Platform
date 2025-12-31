# messaging/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox_view'),
    path('property/<int:property_id>', views.send_property_message_view, name='send_new_message'),
    path('send/<int:conversation_id>/', views.send_message_view, name='send_message'),
    path('conversation/<int:conversation_id>/', views.conversation_detail_view, name='conversation_view'),
    
    # APIs
    # Message APIs (for envelope icon)
    path('api/unread-message-count/', views.get_unread_message_count_api, name='unread_message_count'),
    path('api/messages/check-new/<int:conversation_id>/', views.check_new_messages_api, name='check_new_messages'),
    path('api/messages/mark-conversation-read/<int:conversation_id>/', views.mark_conversation_read_api, name='mark_conversation_read'),
    
    # ========== NOTIFICATIONS (Bell icon) ==========
    # Notification APIs (for bell icon - EXCLUDES messages)
    path('api/notifications/', views.get_notifications_api, name='get_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', views.mark_notification_read_api, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read_api, name='mark_all_notifications_read'),
    # Templates
    path('templates/create/', views.create_template_view, name='create_template'),
    path('templates/', views.template_list_view, name='template_list'),
    path('templates/delete/<int:template_id>/', views.delete_template_view, name='delete_template'),
]