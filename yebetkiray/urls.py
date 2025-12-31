
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    # path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    # path('reviews/', include('reviews.urls')),
    path('messages/', include('messaging.urls')),
    path('search/', include('search.urls')),
    # path('notifications/', include('notifications.urls')),
    path('analytics/', include('analytics.urls')),
    # path('content/', include('content.urls')),
    # path('locations/', include('locations.urls')),
    # path('support/', include('support.urls')),
    # path('api/', include('api.urls')),
    # path('tasks/', include('tasks.urls')),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
