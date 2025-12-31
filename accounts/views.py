from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from properties.models import Property
from messaging.models import Notification
from .models import Favorite
from django.http import JsonResponse
from .forms import UserForm, UserRoleForm, UserProfileForm
from django.contrib.auth.models import User

ADMIN = User.objects.filter(is_staff=True).first()

@login_required
def toggle_favorite_view(request, id):
    property = get_object_or_404(Property, id=id)
    
    if request.user.is_authenticated and request.user != property.landlord:
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            property=property
        )
        
        if not created:
            # Already exists, so delete it (unfavorite)
            favorite.delete()
            is_favorited = False
            
        else:
            is_favorited = True
            Notification.objects.create(
                user=property.landlord,
                message=f"{request.user.get_full_name()} saved your property '{property.title}'",
                notification_type='property_saved',
                related_property=property,
                is_read=False
            )
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
        })
    
    return redirect('detail_view', id=id)

def edit_profile(request):
    user = request.user
    user_role = user.userrole
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_role)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                user=request.user,
                message="Your profile has been updated successfully",
                notification_type='profile_update',
                is_read=False
            )
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard_view')
    else:
        form = UserProfileForm(instance=user_role)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def signup_view(request):
    user_form = UserForm()
    role_form = UserRoleForm()
    if request.method == "POST":
        user_form = UserForm(request.POST)
        role_form = UserRoleForm(request.POST)
        
        if user_form.is_valid() and role_form.is_valid():
            user = user_form.save(commit=False)
            user.username = user_form.cleaned_data['email']
            user.save()
            
            user_role = role_form.save(commit=False)
            user_role.user = user
            user_role.save()
            
            # When new user registers
            Notification.objects.create(
                user=ADMIN,  # Your admin variable
                notification_type='new_user',
                message=f'New user registered: {user.email} ({user.get_full_name()})',
                related_user=user  # If you have this field
            )

            Notification.objects.create(
                user=user,
                message=" Welcome to YebetKiray! Complete your profile to get started.",
                notification_type='welcome',
                is_read=False
            )
            
            Notification.objects.create(
                user=user,
                message=" Tip: Browse properties and save your favorites for quick access.",
                notification_type='tip',
                is_read=False
            )
            messages.success(request, 'Account created successfully!')
            return redirect('login_view')
    else:
        user_form = UserForm()
        role_form = UserRoleForm()
    
    context = {
        'user_form':user_form,
        'role_form':role_form
    }
    return render(request, 'accounts/signup.html', context)