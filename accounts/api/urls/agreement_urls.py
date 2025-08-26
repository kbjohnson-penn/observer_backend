from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.api.views.agreement_views import UserAgreementViewSet, AgreementViewSet

router = DefaultRouter()
router.register(r'user-agreements', UserAgreementViewSet, basename='user_agreements')
router.register(r'agreements', AgreementViewSet, basename='agreements')

urlpatterns = [
    path('', include(router.urls)),
]