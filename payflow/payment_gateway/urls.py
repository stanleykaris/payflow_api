from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    UserViewSet, MerchantViewSet, PaymentMethodViewSet, 
    TransactionViewSet, TransactionLogViewSet, 
    PaymentGatewayViewSet, SubscriptionViewSet
)

# Create a router for the API viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'merchants', MerchantViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'transaction-logs', TransactionLogViewSet)
router.register(r'payment-gateways', PaymentGatewayViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    # Include the payment gateway URLs for version 1 to allow for versioning of the API
    path('v1/', include('payment_gateway.urls_v1')),
    # Include the REST API endpoints for model resources
    path('v1/resources/', include(router.urls)),
]