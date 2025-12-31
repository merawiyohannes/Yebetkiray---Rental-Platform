from django.contrib import admin
from .models import FeaturedPayment

@admin.register(FeaturedPayment)
class FeaturedPaymentAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'amount', 'status', 'created_at']
    list_filter = ['status', 'plan_type']
    search_fields = ['property__title', 'user__email', 'tx_ref']