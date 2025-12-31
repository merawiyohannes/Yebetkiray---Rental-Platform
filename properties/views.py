from django.shortcuts import redirect, render, get_object_or_404
from .models import Property, PropertyImage, RecentlyViewed
from django.contrib import messages
from .forms import PropertyForm, PropertyReviewForm
from django.http import JsonResponse
from messaging.models import Conversation, Message, PropertyReview
from accounts.models import Favorite
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from messaging.models import Notification
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta


ADMIN = User.objects.filter(is_staff=True).first()

def is_staff_user(user):
    return user.is_staff or user.is_superuser

def check_expiring_featured():
    three_days_from_now = timezone.now() + timedelta(days=3)
    expiring_properties = Property.objects.filter(
        is_featured=True,
        featured_until__lte=three_days_from_now,
        featured_until__gt=timezone.now()
    )
    
    for property in expiring_properties:
        days_left = (property.featured_until - timezone.now()).days
        Notification.objects.create(
            user=property.landlord,
            message=f"⚠️ Featured status for '{property.title}' expires in {days_left} days. Renew to maintain visibility.",
            notification_type='featured_expiring',
            related_property=property,
            is_read=False
        )

# properties/views.py
@login_required
def upgrade_to_featured_view(request, property_id):
    """Show upgrade options and handle payment"""
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    
    if request.method == 'POST':
        plan = request.POST.get('plan')
        
        if plan == 'weekly':
            price = 500  # ETB
            days = 7
        elif plan == 'monthly':
            price = 1500  # ETB
            days = 30
        else:
            messages.error(request, 'Invalid plan selected')
            return redirect('upgrade_to_featured', property_id=property.id)
        
        # Here you'll integrate with Chapa/TeleBirr API
        # payment = True
        # if not payment:
        #     Notification.objects.create(
        #         user=property.landlord,
        #         message=f"❌ Payment failed for upgrading '{property.title}' to featured status. Please try again.",
        #         notification_type='payment_failed',
        #         related_property=property,
        #         is_read=False
        #     )
        
        # When featured status expires
        # Notification.objects.create(
        #     user=property.landlord,
        #     message=f"📉 Featured status for '{property.title}' has expired. It is no longer highlighted in search results.",
        #     notification_type='featured_expired',
        #     related_property=property,
        #     is_read=False
        # ) 
        property.is_featured = True
        property.featured_until = timezone.now() + timedelta(days=days)
        property.save()
        
        Notification.objects.create(
            user=property.landlord,
            message=f"Your property '{property.title}' has been upgraded to featured status for {days} days! It will be highlighted until {property.featured_until.strftime('%b %d, %Y')}.",
            notification_type='featured_upgrade',
            related_property=property,
            is_read=False
        )
        
        # Also notify admin (if you have admin notifications)
        Notification.objects.create(
            user=ADMIN,
            message=f"{property.landlord.email} upgraded property '{property.title}' to featured. Payment: {price} ETB.",
            notification_type='featured_upgrade',
            related_property=property,
            is_read=False
        )
        
        
        messages.success(request, f'Property featured for {days} days!')
        return redirect('dashboard_view')
    
    # GET request - show upgrade options
    context = {
        'property': property,
        'weekly_price': 500,
        'monthly_price': 1500,
    }
    return render(request, 'properties/upgrade_featured.html', context)

@user_passes_test(is_staff_user)
def admin_verify_view(request):
    """Simple admin page to manually verify properties"""
    unverified_properties = Property.objects.filter(is_verified=False, is_resubmit=True)
    context = {
        'unverified_properties': unverified_properties,
        'unverified_count': unverified_properties.count(),
    }
    return render(request, 'properties/admin_verify.html', context)

@user_passes_test(is_staff_user)
def verify_property_view(request, property_id):
    """Approve a property - ONE CLICK"""
    if request.method == 'POST':
        try:
            property = Property.objects.get(id=property_id)
            property.is_verified = True
            property.is_resubmit = False
            property.verified_by = request.user
            property.verified_at = timezone.now()
            property.save()
            
            Notification.objects.create(
            user=property.landlord,
            message=f"Your property '{property.title}' has been verified and is now live!",
            notification_type='verification',
            related_property=property,
            is_read=False
        )
            
            messages.success(request, f'Property "{property.title}" approved and published!')
        except Property.DoesNotExist:
            messages.error(request, 'Property not found')
    
    return redirect('admin_verify')

@user_passes_test(is_staff_user)
def reject_property_view(request, property_id):
    """Reject a property"""
    if request.method == 'POST':
        try:
            print('rejection started')
            property = Property.objects.get(id=property_id)
            reason = request.POST.get('reason', '')
            
            property.is_rejected = True
            property.is_resubmit = False
            property.rejection_reason = reason
            property.rejected_at = timezone.now()
            property.save()
            Notification.objects.create(
                user=property.landlord,
                message=f"Your property '{property.title}' needs revision. Reason: {reason[:50]}...",
                notification_type='rejection',
                related_property=property,
                is_read=False
            )
            print('finihsed')        
            messages.warning(request, f"Property rejected. Reason: '{reason}' Landlord can revise and resubmit within 24 hours.")
        except Property.DoesNotExist:
            messages.error(request, 'Property not found')
    
    return redirect('admin_verify')


# properties/views.py - detail_view
def detail_view(request, id):
    property = get_object_or_404(Property, id=id)
    reviews = property.reviews.filter(parent_review__isnull=True)
    if request.user.is_authenticated and request.user.userrole.user_type == 'renter':
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            property=property,
            defaults={'viewed_at': timezone.now()}
        )
        
    if request.user.is_authenticated and request.user != property.landlord:
        from accounts.models import PropertyView
        PropertyView.objects.get_or_create(
            viewer=request.user,
            property=property
        )
        Notification.objects.create(
            user=property.landlord,
            message=f"{request.user.get_full_name()} viewed your property '{property.title}'",
            notification_type='property_view',
            related_property=property,
            is_read=False
        )
    # Check if property is favorited
    if request.user.is_authenticated:
        property.is_favorited = Favorite.objects.filter(
            user=request.user, 
            property=property
        ).exists()
    else:
        property.is_favorited = False
    
    # Get conversation ONLY if user is authenticated and not the landlord
    conversation = None
    message = None
    
    if request.user.is_authenticated and request.user != property.landlord:
        try:
            # FIXED: Find conversation that has BOTH users as participants
            conversation = Conversation.objects.filter(
                property=property,
                participants=request.user
            ).filter(
                participants=property.landlord
            ).distinct().first()
            
            if conversation:
                message = conversation.messages.last()
                
        except Conversation.MultipleObjectsReturned:
            # Handle duplicate conversations (shouldn't happen but just in case)
            conversation = Conversation.objects.filter(
                property=property,
                participants=request.user
            ).filter(
                participants=property.landlord
            ).distinct().first()
            message = conversation.messages.last() if conversation else None
    user_already_reviewed = False
    if request.user.is_authenticated:
        user_already_reviewed = PropertyReview.objects.filter(
                property=property, 
                reviewer=request.user
            ).exists()
        print(user_already_reviewed)
    if request.method == 'POST' and request.user.is_authenticated:
        rev_form = PropertyReviewForm(request.POST)
        if rev_form.is_valid():
            review = rev_form.save(commit=False)
            review.property = property
            review.reviewer = request.user
            review.save()
            
            # Notify landlord about review
            Notification.objects.create(
                user=property.landlord,
                message=f"{request.user.get_full_name()} left a {'⭐ review' if review.review_type == 'review' else '❓ question'} on '{property.title}'",
                notification_type='property_review',  # NEW type!
                related_property=property,
                is_read=False
            )
            return redirect('detail_view', id=id)
    else:
        rev_form = PropertyReviewForm(request.POST)
    
    context = {
        'property': property,
        'conversation': conversation,  # Could be None
        'message': message,  # Could be None
        'rev_form':rev_form,
        'user_already_reviewed':user_already_reviewed,
        'reviews': reviews,
    }
    return render(request, 'properties/detail.html', context)

@login_required
def add_reply_view(request, id):
    """Add reply to a review/question"""
    parent_review = get_object_or_404(PropertyReview, id=id)
    property = parent_review.property
    
    # Check if user is the property landlord
    if request.user != property.landlord:
        messages.error(request, 'Only the property owner can reply.')
        return redirect('detail_view', id=property.id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            # Create reply (same model, just linked via parent_review)
            PropertyReview.objects.create(
                property=property,
                reviewer=request.user,
                review_type='reply',
                comment=comment,
                parent_review=parent_review
            )
            messages.success(request, 'Reply added successfully!')
            Notification.objects.create(
                user=parent_review.reviewer,  # The person who asked the question
                notification_type='review_reply',  # NEW type!
                message=f"{property.landlord.first_name} replied to your {parent_review.review_type} on '{property.title}'",
                related_property=property,
                is_read=False
            )
        
            messages.success(request, 'Reply added successfully!')
    return redirect('detail_view', id=property.id)

def delete_property(request, pk):
    # Get the property or return 404 if not found
    property = get_object_or_404(Property, id=pk)
    
    if request.method == 'POST':
        # Delete the property
        property_title = property.title
        property.delete()
        messages.success(request, f'Property "{property_title}" has been deleted successfully!')
        return redirect('dashboard_view')
    
    # If GET request, render the confirmation page
    return render(request, 'properties/delete.html', {'property': property})

def delete_property_image(request, pk):
    image = get_object_or_404(PropertyImage, pk=pk, property__landlord=request.user)
    property_pk = image.property.pk
    image.delete()
    return redirect('property_edit_view', property_pk)

def property_edit_view(request, pk):
    try:
        property = Property.objects.get(id=pk, landlord=request.user)
    except Property.DoesNotExist:
        messages.error(request, 'Property not found or access denied')
        return redirect('dashboard_view')
    is_resubmission = property.is_rejected
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            property = form.save(commit=False)
            
            if is_resubmission:
                # Reset rejection status for resubmission
                property.is_rejected = False
                property.is_resubmit = True
                property.is_verified = False  # Needs verification again
                property.rejection_reason = ''
                property.rejected_at = None
                property.auto_delete_at = None
                Notification.objects.create(
                        user=ADMIN,
                        notification_type='property_resubmission',
                        message=f'Property "{property.title}" resubmitted by {request.user.email}',
                        related_property=property
                    )
                messages.success(request, 
                    ' Property resubmitted for verification! It will be reviewed again.')
            else:
                messages.success(request, 'Property updated successfully!')
                
            property.save()
            if property.is_verified:
                return redirect('detail_view', id=pk)
            else:
                return redirect('dashboard_view')
    else:
        form = PropertyForm(instance=property)
        
    return render(request, 'properties/property_edit.html', {
        'form': form,
        'property': property,
        'is_resubmission':is_resubmission
    })
    
def property_create_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            property.save()
            
            # Handle image uploads manually
            images = request.FILES.getlist('images')
            if len(images) > 5:
                form.add_error(None, "You can upload up to 5 images only.")
            else:
                for i, image in enumerate(images):
                    PropertyImage.objects.create(
                        property=property,
                        image=image,
                        is_primary=(i == 0)
                    )
                Notification.objects.create(
                    user=ADMIN,
                    notification_type='property_submission',
                    message=f'New property "{property.title}" submitted by {request.user.email}',
                    related_property=property)
                messages.success(request, 
                f'Property "{property.title}" submitted successfully! '
                f'It is now awaiting verification and will be visible on the homepage '
                f'once approved by our team (usually within 24 hours).'
            )
                return redirect('dashboard_view')
    else:
        form = PropertyForm()
    
    return render(request, 'properties/property_form.html', {'form': form})

def upload_property_image(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        property = get_object_or_404(Property, pk=pk, landlord=request.user)
        
        # Check image limit
        existing_count = property.images.count()
        images = request.FILES.getlist('images')
        
        if existing_count + len(images) > 5:
            return JsonResponse({
                'success': False,
                'error': f'Maximum 5 images allowed. You have {existing_count} already.'
            })
        
        uploaded_images = []
        for i, image in enumerate(images):
            prop_image = PropertyImage.objects.create(
                property=property,
                image=image,
                is_primary=(existing_count == 0 and i == 0)  # First image becomes primary
            )
            uploaded_images.append({
                'id': prop_image.id,
                'url': prop_image.image.url,
                'is_primary': prop_image.is_primary
            })
        
        return JsonResponse({
            'success': True,
            'images': uploaded_images,
            'total_images': property.images.count()
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})