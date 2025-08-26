from django.db import models
from django.conf import settings
from shared.validators import validate_field


class AgreementType(models.Model):
    """Types of agreements (Data Use Agreement, Code of Conduct, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'accounts'


class Agreement(models.Model):
    """Individual agreements that users can sign"""
    agreement_type = models.ForeignKey(AgreementType, on_delete=models.CASCADE, related_name='agreements')
    title = models.CharField(max_length=200)
    version = models.CharField(max_length=20)
    content = models.TextField()  # Full agreement text
    document_url = models.URLField(blank=True, null=True)  # External document link
    project_name = models.CharField(max_length=200, blank=True)  # Associated project
    project_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} v{self.version}"
    
    class Meta:
        app_label = 'accounts'
        unique_together = ['title', 'version']


class UserAgreement(models.Model):
    """Track which agreements users have signed"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signed_agreements')
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.agreement.title}"
    
    class Meta:
        app_label = 'accounts'
        unique_together = ['user', 'agreement']