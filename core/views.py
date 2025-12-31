from django.shortcuts import render
from properties.models import Property
from accounts.models import Favorite
def home_view(request):
    featured_properties = Property.objects.filter(is_featured=True, is_available=True)
    all_properties = Property.objects.filter(is_verified=True, is_available=True)
    
    # Get list of property IDs that current user has favorited
    if request.user.is_authenticated:
        favorited_ids = Favorite.objects.filter(
            user=request.user
        ).values_list('property_id', flat=True)
        
        # Add is_favorited attribute to each property
        for prop in featured_properties:
            prop.is_favorited = prop.id in favorited_ids
        
        for prop in all_properties:
            prop.is_favorited = prop.id in favorited_ids
    else:
        # For non-logged in users, set all to False
        for prop in featured_properties:
            prop.is_favorited = False
        
        for prop in all_properties:
            prop.is_favorited = False
    
    context = {
        'featured_properties': featured_properties,
        'all_properties': all_properties
    }
    return render(request, 'core/home.html', context)