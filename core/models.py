from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

# Create your models here.

class LoyaltyTier(models.TextChoices):
    BRONZE = 'BRONZE', 'Bronze'
    SILVER = 'SILVER', 'Silver'
    GOLD = 'GOLD', 'Gold'
    PLATINUM = 'PLATINUM', 'Platinum'

class PollVisibility(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Public'
    PRIVATE = 'PRIVATE', 'Private'
    FRIENDS = 'FRIENDS', 'Friends'

class User(AbstractUser):
    """Enhanced User model matching Spring Boot User entity"""
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    loyalty_tier = models.CharField(
        max_length=10,
        choices=LoyaltyTier.choices,
        default=LoyaltyTier.BRONZE
    )
    
    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
    
    def save(self, *args, **kwargs):
        # Update loyalty tier based on points
        if self.loyalty_points >= 1000:
            self.loyalty_tier = LoyaltyTier.PLATINUM
        elif self.loyalty_points >= 500:
            self.loyalty_tier = LoyaltyTier.GOLD
        elif self.loyalty_points >= 100:
            self.loyalty_tier = LoyaltyTier.SILVER
        else:
            self.loyalty_tier = LoyaltyTier.BRONZE
        
        if not self.pk:  # New user
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)

class Poll(models.Model):
    """Enhanced Poll model matching Spring Boot Poll entity"""
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=500, null=False, blank=False)
    options = models.JSONField(default=list)  # List of option strings
    votes = models.JSONField(default=dict)  # Map of option -> vote count
    category = models.CharField(max_length=100, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    duration = models.DateTimeField(null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    visibility = models.CharField(
        max_length=10,
        choices=PollVisibility.choices,
        default=PollVisibility.PUBLIC
    )
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'polls'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New poll
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def total_votes(self):
        return sum(self.votes.values()) if self.votes else 0

class Vote(models.Model):
    """Vote model for tracking individual votes"""
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    option = models.CharField(max_length=255)  # The option text that was voted for
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'poll_votes'
        unique_together = ['user', 'poll']  # One vote per user per poll

class UserProfile(models.Model):
    """Legacy UserProfile model - keeping for backward compatibility"""
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    preferred_cinemas = models.JSONField(default=list)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_profiles'

# Signal to auto-create UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
