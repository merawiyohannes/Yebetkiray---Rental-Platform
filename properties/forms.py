from django import forms
from messaging.models import PropertyReview
from .models import Property

CLASS_INPUT = 'w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-800 focus:border-transparent transition duration-200'

class PropertyForm(forms.ModelForm):    
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'price', 'location', 
                 'bedrooms', 'bathrooms', 'area', 'is_available',
                 'is_furnished', 'has_parking', 'has_balcony', 
                 'has_security', 'has_backup_generator', 'has_internet',
                 'pet_friendly', ]
    
    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 5:
            raise forms.ValidationError("You can upload up to 5 images only.")
        return images
    
    
class PropertyReviewForm(forms.ModelForm):
    class Meta:
        model = PropertyReview
        fields = ['review_type', 'rating', 'comment']