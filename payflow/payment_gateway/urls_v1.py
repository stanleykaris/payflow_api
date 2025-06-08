from django.urls import path
from .views import StripePaymentView, StripeWebhookView

urlpatterns = [
    path('create-payment-intent/', StripePaymentView.as_view({'post': 'create_payment_intent'}), name='create-payment-intent'),
    path('create-payment-link/', StripePaymentView.as_view({'post': 'create_payment_link'}), name='create-payment-link'),
    path('checkout-session/', StripePaymentView.as_view({'post': 'checkout_session'}), name='checkout-session'),
    path('success/', StripePaymentView.as_view({'get': 'payment_success'}), name='success'),
    path('cancel/', StripePaymentView.as_view({'get': 'payment_cancel'}), name='cancel'),
    path('webhook/', StripeWebhookView.as_view(), name='webhook'),
]