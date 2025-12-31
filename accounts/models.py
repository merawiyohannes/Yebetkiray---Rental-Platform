from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from properties.models import Property

class UserRole(models.Model):
    
    USER_TYPES = (
        ('landlord', 'Landlord'),
        ('renter', 'Renter'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField(
        folder='yebetkiray/profiles/', 
        null=True, 
        blank=True
    )
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user_type})"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
    
class PropertyView(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['viewer', 'property'] 