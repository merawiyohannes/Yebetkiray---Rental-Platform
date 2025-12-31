from django.shortcuts import render, redirect
from properties.models import Property, RecentlyViewed
from django.contrib.auth.decorators import login_required
from messaging.models import Message, Conversation
from accounts.models import Favorite
from messaging.models import Notification
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

@login_required
def dashboard(request):
    user_properties = Property.objects.filter(landlord=request.user)
    total_fields = 3  # Adjust based on how many fields you want to track
    completed_fields = 0
    total_view = 0
    user = request.user
    user_role = user.userrole
    recently_viewed = []
    
    if request.user.userrole.user_type == 'renter':
        recently_viewed = Property.objects.filter(
            recentlyviewed__user=request.user
        ).order_by('-recentlyviewed__viewed_at')[:10]

    
    for pro in user_properties:
        total_view += pro.get_view_count
    
    if user.get_full_name():
        completed_fields += 1
    if user_role.phone:
        completed_fields += 1
    if user_role.profile_picture:
        completed_fields += 1
    # Add more fields as needed
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
    
    # notifications related
    total_notifications = Notification.objects.filter(
        user=request.user
    )
    unread_notifications = Notification.objects.filter(
        user=request.user, is_read=False
    )
    
    # Calculate percentage
    if total_fields > 0:
        profile_completion = int((completed_fields / total_fields) * 100)
    else:
        profile_completion = 0
        
    properties_count = Property.objects.filter(landlord=request.user).count()
    
    total_messages = Conversation.objects.filter(participants=request.user).count()
    
    unread_messages = Message.objects.filter(conversation__participants=request.user,read=False).exclude(sender=request.user).count()
    
    recent_messages = Message.objects.filter(conversation__participants=request.user).exclude(sender=request.user).order_by('-created_at')[:5]
    
    saved_count = Favorite.objects.filter(user=request.user).count()
    
    saved_properties = Property.objects.filter(favorited_by__user=request.user)
    
    verified_count = user_properties.filter(is_verified=True, is_rejected=False).count()
    
    pending_count = user_properties.filter(is_verified=False, is_rejected=False).count()
    
    rejected_count =  user_properties.filter(is_rejected=True).count()
    
    rejected_property = user_properties.filter(is_rejected=True) 
    
    return render(request, 'analytics/dashboard.html', {
        "total_count":total_messages,
        'verified_count': verified_count,
        'pending_count': pending_count,
        'messages_count': unread_messages,
        "saved_count":saved_count,
        'rejected_count':rejected_count,
        'recent_messages': recent_messages,
        'user_properties':user_properties,
        'profile_completion':profile_completion,
        'properties_count':properties_count,
        'rejected_property':rejected_property,
        'total_view':total_view,
        'conversations':conversations,
        'total_unread':total_unread,
        'total_notifications':total_notifications,
        'unread_notifications':unread_notifications,
        'saved_properties':saved_properties,
        'recently_viewed':recently_viewed,
    })
    
    
    # views.py


@login_required
def admin_dashboard(request):
    # Only admin can access this
    if not request.user.is_superuser:
        return redirect('dashboard')  # or your regular user dashboard
    
    # Admin-specific analytics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    total_properties = Property.objects.count()
    total_users = User.objects.all().count()
    pending_properties = Property.objects.filter(is_verified=False).count()
    active_properties = Property.objects.filter(is_verified=True).count()
    verified_properties = Property.objects.filter(is_verified=True).count()
    
    total_messages = Message.objects.count()
    unread_admin_messages = Message.objects.filter(
        read=False, 
        sender=request.user
    ).count()
    
    # Financial metrics (if applicable)
    # total_revenue = Payment.objects.filter(
    #     status='completed'
    # ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent activities
    # recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
    
    # User signups chart data (last 7 days)
    today = timezone.now().date()
    signups_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        signups_data.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    context = {
        # Core stats
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'total_properties': total_properties,
        'pending_properties': pending_properties,
        'active_properties': active_properties,
        'unread_admin_messages': unread_admin_messages,
        # 'total_revenue': total_revenue,
        
        # Admin-specific data
        # 'recent_activities': recent_activities,
        'signups_data': signups_data,
        
        # Keep some from original for consistency
        'total_unread': unread_admin_messages,
        'conversations': Message.objects.filter(
            sender=request.user
        ).order_by('-created_at')[:5],
        'verified_properties':verified_properties,
        'total_users':total_users,
    }
    
    return render(request, 'analytics/admin_dashboard.html', context)
    

