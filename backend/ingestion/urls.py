from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, IngestionView, TravelFetchView, EmissionRowViewSet, HealthView, EmissionFactorViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'rows', EmissionRowViewSet, basename='emissionrow')
router.register(r'factors', EmissionFactorViewSet, basename='emissionfactor')

urlpatterns = [
    path('ingest/', IngestionView.as_view(), name='ingest'),
    path('health/', HealthView.as_view(), name='health'),
    path('travel/fetch/', TravelFetchView.as_view(), name='travel-fetch'),
    path('', include(router.urls)),
]
