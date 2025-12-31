from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db.models import Avg

class Property(models.Model):
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('condominium', 'Condominium'),
        ('traditional', 'Traditional House'),
    )

    LOCATION = (
        ('semit', 'Semit'),
        ('tuludimtu', 'Tulu Dimtu'),
        ('koye-feche', 'Koye-Feche'),
        ('arabsa', 'Arabsa'),
        ('bulbula', 'Bulbula'),
        ('abado', 'Abado'),
        ('bole', 'Bole'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price = models.PositiveIntegerField()
    location = models.CharField(max_length=100, choices=LOCATION)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=8, decimal_places=2)  # in square meters
    is_furnished = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)
    has_backup_generator = models.BooleanField(default=False, verbose_name="Has Generator")
    has_internet = models.BooleanField(default=False, verbose_name="Internet Ready")
    pet_friendly = models.BooleanField(default=False)
    
    # Date field for when property becomes available
    available_from = models.DateField(null=True, blank=True, verbose_name="Available From")
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True) 
    is_available = models.BooleanField(default=True)
    
    rejection_reason = models.TextField(blank=True) 
    is_rejected = models.BooleanField(default=False)
    is_resubmit = models.BooleanField(default=False)
    rejected_at = models.DateTimeField(null=True, blank=True)
    auto_delete_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # verification fields 
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.get_location_display()}"

    def get_primary_image(self):
        """Return the primary image if available, otherwise the first image, otherwise None."""
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None
    def save(self, *args, **kwargs):
        # Set auto_delete_at when property is rejected
        if self.is_rejected and not self.auto_delete_at:
            from django.utils import timezone
            self.auto_delete_at = timezone.now() + timezone.timedelta(hours=24)
        
        # Reset auto_delete_at if property is edited/resubmitted
        if not self.is_rejected and self.auto_delete_at:
            self.auto_delete_at = None
            
        super().save(*args, **kwargs)
    
    def get_status(self):
        """Returns property status"""
        if self.is_verified:
            return 'verified'
        elif self.is_rejected:
            return 'rejected'
        else:
            return 'pending'
        
    @property  
    def get_view_count(self):
        return self.views.count()
        
    @property  
    def get_save_count(self):
        from accounts.models import Favorite
        return Favorite.objects.filter(
            property=self, 
        ).count()
    @property
    def average_rating(self):
        reviews = self.reviews.filter(review_type='review', parent_review__isnull=True)
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(review_type='review', parent_review__isnull=True).count()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField(folder='yebetkiray/properties/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-viewed_at']
        unique_together = ['user', 'property']