# messaging/models.py
from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from properties.models import Property

class Conversation(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation about {self.property.title}"
    
    def get_other_participant(self, current_user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=current_user.id).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(read=False).exclude(sender=user).count()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    
    # File attachments
    attachment = CloudinaryField(
        folder='yebetkiray/messages/attachments/',
        null=True,
        blank=True,
        resource_type='auto'
    )
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_type = models.CharField(max_length=50, blank=True)  # image, pdf, doc
    
    # Read receipts
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"
    
    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()

class MessageTemplate(models.Model):
    """Quick reply templates for landlords"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_templates')
    name = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('greeting', '👋 Greeting'),
        ('viewing', '👀 Viewing Request'),
        ('documents', '📄 Document Request'),
        ('questions', '❓ Follow-up Questions'),
        ('rejection', '🚫 Not Suitable'),
        ('confirmation', '✅ Confirmation'),
    ])
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

# messaging/models.py
class Notification(models.Model):
    """Real-time notifications"""
    NOTIFICATION_TYPES = [
        # Messages
        ('message', '💬 New Message'),
        
        # Property Status
        ('verification', '✅ Property Verified'),
        ('rejection', '❌ Property Rejected'),
        
        # Property Interactions  
        ('property_view', '👀 Property Viewed'),
        ('property_saved', '❤️ Property Saved'),
        ('property_inquiry', '❓ New Inquiry'),
        ('property_review', '⭐ Property Review/Question'),
        ('review_reply', '👑 Review Reply'),
        
        # NEW: Featured property notifications
        ('featured_upgrade', '🌟 Property Upgraded to Featured'),
        ('featured_expiring', '⚠️ Featured Status Expiring Soon'),
        ('featured_expired', '📉 Featured Status Expired'),
        ('featured_renewed', '✅ Featured Status Renewed'),
        ('payment_failed', '❌ Featured Payment Failed'),
            
        # Admin notifications (NEW)
        ('property_submission', '📝 New Property Submitted'),
        ('property_resubmission', '🔄 Property Resubmitted'),
        ('new_user', '👤 New User Registered'),
            
        # User Actions
        ('profile_update', '👤 Profile Updated'),
        ('account_alert', '⚠️ Account Alert'),
        
        # System
        ('welcome', '👋 Welcome to YebetKiray'),
        ('tip', '💡 Pro Tip'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True)
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.user}"
    
    def get_link(self):
        """Return appropriate link for each notification type"""
        if self.notification_type == 'message' and self.related_conversation:
            return f"/messaging/?conversation={self.related_conversation.id}"
        elif self.notification_type in ['payment_failed', 'featured_renewed', 'featured_expired', 'featured_expiring', 'featured_upgrade', 'verification', 'rejection', 'property_view', 'property_saved', 'property_inquiry', 'property_review', 'review_reply'] and self.related_property:
            return f"/properties/detail/{self.related_property.id}"
        elif self.notification_type == 'profile_update':
            return "/accounts/edit/"
        elif self.notification_type == 'property_submission':
            return "/properties/admin/verify/" 
        elif self.notification_type == 'property_resubmission':
            return "/properties/admin/verify/"
        elif self.notification_type == 'new_user' and self.related_user:
            return f"/admin/accounts/userrole/{self.related_user.id}/change/"
        elif self.notification_type in ['welcome', 'tip', 'account_alert']:
            return "/analytics/"
        return "#"

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    contact_preference = models.CharField(max_length=10, choices=[('phone', 'Phone'), ('email', 'Email')])
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('contacted', 'Contacted'), ('closed', 'Closed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

REVIEW_TYPES = [
    ('question', '❓ Question'),
    ('review', '⭐ Review'),
    ('tip', '💡 Tip'),
]

class PropertyReview(models.Model):
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPES, default='review')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_reviews')
    rating = models.IntegerField(choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], null=True, blank=True)
    comment = models.TextField()  # Can be question OR review
    is_question = models.BooleanField(default=False)  # Flag: question vs review
    parent_review = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['property', 'reviewer', 'parent_review']    # One review per user per property
    
    def __str__(self):
        return f"{self.reviewer} - {self.property} - {self.rating}⭐"
