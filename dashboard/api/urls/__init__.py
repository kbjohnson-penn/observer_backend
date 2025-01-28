from django.urls import path, include

urlpatterns = [
    path('v1/', include(('dashboard.api.urls.v1', 'v1'), namespace='v1')),
]
