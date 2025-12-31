# messaging/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Max, Count
from django.contrib import messages

from properties.models import Property
from .models import Message, Conversation, MessageTemplate, Notification
import json

@login_required
def conversation_detail_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Mark all unread messages as read
    conversation.messages.filter(
        read=False
    ).exclude(sender=request.user).update(
        read=True,
        read_at=timezone.now()
    )
    
    # Get all conversations for sidebar
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_archived=False
    ).order_by('-updated_at')
    
    # Calculate unread counts
    for conv in conversations:
        conv.unread_count = conv.messages.filter(
            read=False
        ).exclude(sender=request.user).count()
    
    total_unread = sum(conv.unread_count for conv in conversations)
    
    # For AJAX requests, return only the message thread
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {
            'active_conversation': conversation,
            'request': request,
        }
        return render(request, 'messaging/message_thread.html', context)
    
    # For normal requests, return full page with conversation list
    context = {
        'conversations': conversations,
        'active_conversation': conversation,
        'total_unread': total_unread,
    }
    
    return render(request, 'messaging/inbox.html', context)

@login_required
def inbox_view(request):
    # Get conversations
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_archived=False
    ).order_by('-updated_at')
    
    # Calculate unread counts
    for conv in conversations:
        conv.unread_count = conv.messages.filter(
            read=False
        ).exclude(sender=request.user).count()
    
    total_unread = sum(conv.unread_count for conv in conversations)
    
    # For AJAX requests, return JSON with unread count
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'total_unread': total_unread})
    
    context = {
        'conversations': conversations,
        'active_conversation': None,
        'total_unread': total_unread,
    }
    
    return render(request, 'messaging/inbox.html', context)

@login_required
def send_message_view(request, conversation_id):
    
    if request.method == 'POST':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=request.user
        )
        
        content = request.POST.get('content', '').strip()
        attachment = request.FILES.get('attachment')
        
        if content or attachment:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                attachment=attachment
            )
            
            conversation.updated_at = timezone.now()
            conversation.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully'
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Message cannot be empty'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
@login_required
def send_property_message_view(request, property_id):
    """Send message from property detail page (creates conversation if needed)"""
    property = get_object_or_404(Property, id=property_id)
    
    # Find or create conversation
    conversation, created = Conversation.objects.get_or_create(
        property=property,
    )
    conversation.participants.add(request.user, property.landlord)
    
    # Send message (your existing send logic)
    content = request.POST.get('message', '').strip()
    if content:
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        messages.success(request, 'Message sent! Continue conversation in your inbox.')
        return redirect('detail_view', property_id)
    
    return JsonResponse({'error': 'Message empty'}, status=400)

# MEssage-Related APIs
@login_required
def get_unread_message_count_api(request):
    """Get total unread messages count for envelope icon"""
    unread_count = Message.objects.filter(
        conversation__participants=request.user,  
        read=False,                           
    ).exclude(
        sender=request.user                      
    ).count()
    return JsonResponse({'unread_messages': unread_count})

@login_required
def check_new_messages_api(request, conversation_id):
    """Check for new messages (for envelope icon polling)"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    last_message_time = request.GET.get('last_message_time')
    if last_message_time:
        has_new = conversation.messages.filter(
            created_at__gt=last_message_time
        ).exclude(sender=request.user).exists()
        
        return JsonResponse({'has_new_messages': has_new})
    
    return JsonResponse({'has_new_messages': False})

@require_POST
@login_required
def mark_conversation_read_api(request, conversation_id):
    """Mark all messages in a conversation as read (for envelope icon)"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    # Mark all unread messages in this conversation as read
    updated_count = conversation.messages.filter(
        is_read=False
    ).exclude(
        sender=request.user
    ).update(is_read=True)
    
    # Also mark any message notifications for this conversation as read
    Notification.objects.filter(
        user=request.user,
        notification_type='message',
        related_conversation=conversation,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'count': updated_count
    })
    
    
# Notification-related-APIs

@login_required
def get_notifications_api(request):
    """Get notifications for bell icon (EXCLUDES messages)"""
    notifications = Notification.objects.filter(
        user=request.user
    ).exclude(
        notification_type='message'  # EXCLUDE messages - they have envelope icon
    ).order_by('-created_at')
    
    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'id': notif.id,
            'message': notif.message,
            'type': notif.notification_type,
            'is_read': notif.is_read,
            'time': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            'url': notif.get_link() if hasattr(notif, 'get_link') else '#',
        })
    
    return JsonResponse({'notifications': notifications_data})

@require_POST
@login_required
def mark_notification_read_api(request, notification_id):
    """Mark a single notification as read (for bell icon)"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id,
        user=request.user
    )
    
    # Only mark as read if it's not a message notification
    if notification.notification_type != 'message':
        notification.is_read = True
        notification.save()    
    return JsonResponse({'success': True})


@require_POST
@login_required
def mark_all_notifications_read_api(request):
    """Mark all non-message notifications as read (for bell icon)"""
    updated_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).exclude(
        notification_type='message'  # EXCLUDE messages
    ).update(is_read=True)
    return JsonResponse({
        'success': True,
        'count': updated_count,
        'message': f'Marked {updated_count} notifications as read'
    })




# template-related-functions

@login_required
def create_template_view(request):
    """Create a message template"""
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.POST.get('content')
        category = request.POST.get('category')
        
        if name and content:
            MessageTemplate.objects.create(
                user=request.user,
                name=name,
                content=content,
                category=category
            )
            messages.success(request, 'Template created successfully!')
            return redirect('template_list')
    
    return render(request, 'messaging/create_template.html')

@login_required
def template_list_view(request):
    """List all message templates"""
    templates = MessageTemplate.objects.filter(user=request.user)
    return render(request, 'messaging/template_list.html', {'templates': templates})

@login_required
def delete_template_view(request, template_id):
    """Delete a message template"""
    template = get_object_or_404(MessageTemplate, id=template_id, user=request.user)
    template.delete()
    messages.success(request, 'Template deleted successfully!')
    return redirect('template_list')