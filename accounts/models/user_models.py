from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets
import string

class User(AbstractUser):
    """
    Custom User model for Observer platform.
    Extends Django's AbstractUser to allow future customization.
    """
    # Override email to make it unique
    email = models.EmailField(unique=True)
    
    # Additional fields can be added here as needed
    # For example:
    # middle_name = models.CharField(max_length=50, blank=True)
    # employee_id = models.CharField(max_length=20, blank=True, unique=True)
    
    class Meta:
        app_label = 'accounts'
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class EmailVerificationToken(models.Model):
    """
    Model to store email verification tokens for user registration.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'accounts'
        db_table = 'accounts_email_verification_token'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Generate a unique verification token"""
        while True:
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            if not EmailVerificationToken.objects.filter(token=token).exists():
                return token
    
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def __str__(self):
        return f"Verification token for {self.user.email}"