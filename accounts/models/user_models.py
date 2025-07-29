from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model for Observer platform.
    Extends Django's AbstractUser to allow future customization.
    """
    # Additional fields can be added here as needed
    # For example:
    # middle_name = models.CharField(max_length=50, blank=True)
    # employee_id = models.CharField(max_length=20, blank=True, unique=True)
    
    class Meta:
        app_label = 'accounts'
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'