from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from properties.models import Property

def search_ajax(request):
    # Get filter parameters
    site_location = request.GET.get('site_location')
    property_type = request.GET.get('property_type')
    price_range = request.GET.get('price_range')
    
    # Start with all properties
    properties = Property.objects.filter(is_verified=True)
    
    # Apply filters
    if site_location:
        properties = properties.filter(location__iexact=site_location)
    
    if property_type:
        properties = properties.filter(property_type__iexact=property_type)
    
    if price_range:
        if price_range == '0-5000':
            properties = properties.filter(price__lt=5000)
        elif price_range == '5000-10000':
            properties = properties.filter(price__gte=5000, price__lte=10000)
        elif price_range == '10000-20000':
            properties = properties.filter(price__gte=10000, price__lte=20000)
        elif price_range == '20000+':
            properties = properties.filter(price__gt=20000)
    
    # Format the search criteria for display
    location_display = site_location if site_location else "Any Location"
    type_display = property_type if property_type else "Any Type"
    
    price_display = "Any Price"
    if price_range == '0-5000':
        price_display = "Under 5,000 ETB"
    elif price_range == '5000-10000':
        price_display = "5,000 - 10,000 ETB"
    elif price_range == '10000-20000':
        price_display = "10,000 - 20,000 ETB"
    elif price_range == '20000+':
        price_display = "20,000+ ETB"
    
    # Render the results HTML fragment
    html = render_to_string('search/property_results.html', {
        'properties': properties,
        'site': location_display,
        'type': type_display,
        'price': price_display,
    })
    return HttpResponse(html)

def search(request):
    site_location = request.GET.get('site_location')
    property_type = request.GET.get('property_type')
    price_range = request.GET.get('price_range')
    context = {
        'site':site_location,
        'type':property_type,
        'price':price_range,
        
    }
    return render(request, 'search/search.html', context)




