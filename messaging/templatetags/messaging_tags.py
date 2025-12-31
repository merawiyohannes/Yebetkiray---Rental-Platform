# messaging/templatetags/messaging_tags.py
from django import template
from messaging.models import Notification

register = template.Library()

# messaging/templatetags/messaging_tags.py
@register.simple_tag(takes_context=True)
def get_unread_message_count(context):
    """Count only MESSAGE notifications"""
    request = context['request']
    if request.user.is_authenticated:
        # Use the count from context if available, otherwise query
        if 'message_unread' in context:
            return context['message_unread']
        return Notification.objects.filter(
            user=request.user,
            notification_type='message',
            is_read=False
        ).count()
    return 0

@register.simple_tag(takes_context=True)
def get_unread_property_count(context):
    """Count property-related notifications"""
    request = context['request']
    if request.user.is_authenticated:
        if 'other_unread' in context:
            return context['other_unread']
        return Notification.objects.filter(
            user=request.user,
            notification_type__in=['verification', 'rejection', 'property_view', 'property_saved', 'property_inquiry'],
            is_read=False
        ).count()
    return 0

@register.simple_tag(takes_context=True)
def get_unread_system_count(context):
    """Count system notifications"""
    request = context['request']
    if request.user.is_authenticated:
        return Notification.objects.filter(
            user=request.user,
            notification_type__in=['profile_update', 'account_alert', 'welcome', 'tip'],
            is_read=False
        ).count()
    return 0

@register.inclusion_tag('messaging/notification_dropdown.html', takes_context=True)
def notification_dropdown(context):
    """Render notification dropdown with latest notifications"""
    request = context['request']
    notifications = []
    
    if request.user.is_authenticated:
        # Exclude message notifications - they have their own bell
        notifications = Notification.objects.filter(
            user=request.user
        ).exclude(
            notification_type='message'
        ).order_by('-created_at')[:10] # Last 10 notifications
    
    return {'notifications': notifications}