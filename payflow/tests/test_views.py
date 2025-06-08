import unittest
import json
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from rest_framework import status
from payment_gateway.views import StripePaymentView
from payment_gateway.models import User

class TestStripePaymentView(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = StripePaymentView.as_view({'post': 'create_payment_intent'})

    @patch('stripe.PaymentIntent.create')
    @patch('payment_gateway.views.get_object_or_404')
    @patch('payment_gateway.models.Transaction.objects.create')
    @patch('payment_gateway.models.PaymentMethod.objects.filter')
    @patch('payment_gateway.models.Merchant.objects.first')
    def test_create_payment_intent_success(self, mock_merchant_first, mock_payment_method_filter, 
                                          mock_transaction_create, mock_get_object_or_404, mock_payment_intent_create):
        # Setup mocks
        mock_user = MagicMock(spec=User)
        mock_get_object_or_404.return_value = mock_user
        
        # Mock payment method filter
        mock_payment_method = MagicMock()
        mock_payment_method_filter.return_value.first.return_value = mock_payment_method
        
        # Mock merchant
        mock_merchant = MagicMock()
        mock_merchant_first.return_value = mock_merchant
        
        # Mock transaction
        mock_transaction = MagicMock()
        mock_transaction_create.return_value = mock_transaction
        
        # Mock payment intent with all required attributes
        mock_intent = MagicMock()
        mock_intent.status = 'succeeded'
        mock_intent.id = 'pi_123456'
        mock_intent.amount = 10000
        mock_intent.metadata = {'description': 'Test payment'}
        mock_payment_intent_create.return_value = mock_intent
        
        request = self.factory.post('/payment-intent', data={
            'amount': '100.00',
            'payment_method_id': 'pm_123',
            'user_id': 1,
            'description': 'Test payment'
        }, content_type='application/json')
        
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_transaction_create.assert_called_once()

    @patch('stripe.PaymentLink.create')
    @patch('payment_gateway.views.get_object_or_404')
    @patch('payment_gateway.models.Transaction.objects.create')
    @patch('payment_gateway.models.PaymentMethod.objects.filter')
    @patch('payment_gateway.models.Merchant.objects.first')
    @patch('payment_gateway.models.TransactionLog.objects.create')
    def test_create_payment_link_success(self, mock_log_create, mock_merchant_first, mock_payment_method_filter, 
                                        mock_transaction_create, mock_get_object_or_404, mock_payment_link_create):
        # Setup mocks
        mock_user = MagicMock(spec=User)
        mock_get_object_or_404.return_value = mock_user
        
        # Mock payment method
        mock_payment_method = MagicMock()
        mock_payment_method_filter.return_value.first.return_value = mock_payment_method
        
        # Mock merchant
        mock_merchant = MagicMock()
        mock_merchant_first.return_value = mock_merchant
        
        # Mock transaction
        mock_transaction = MagicMock()
        mock_transaction.id = 123
        mock_transaction_create.return_value = mock_transaction
        
        # Mock payment link
        mock_payment_link = MagicMock()
        mock_payment_link.url = 'http://example.com/payment-link'
        mock_payment_link_create.return_value = mock_payment_link
        
        request = self.factory.post('/payment-link', data={
            'user_id': 1,
            'amount': '100.00',
            'product_name': 'Test Product',
            'merchant_id': 1
        }, content_type='application/json')
        
        response = StripePaymentView.as_view({'post': 'create_payment_link'})(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_transaction_create.assert_called_once()

    @patch('stripe.checkout.Session.create')
    @patch('payment_gateway.views.get_object_or_404')
    def test_checkout_session_success(self, mock_get_object_or_404, mock_session_create):
        mock_user = MagicMock(spec=User)
        mock_get_object_or_404.return_value = mock_user
        mock_session_create.return_value = MagicMock(id='cs_test_123')
        
        request = self.factory.post('/checkout-session', data={
            'user_id': 1,
            'amount': '100.00',
            'product_name': 'Test Product'
        })
        
        response = StripePaymentView.as_view({'post': 'checkout_session'})(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment_intent_missing_amount(self):
        request = self.factory.post('/payment-intent', data=json.dumps({
            'amount': '100.00',
            'payment_method_id': 'pm_123',
            'user_id': 1,
            'description': 'Test payment'
        }),
        content_type='application/json')
        
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_link_missing_user_id(self):
        request = self.factory.post('/payment-link', data={
            'amount': '100.00',
            'product_name': 'Test Product',
            'merchant_id': 1
        })
        
        response = StripePaymentView.as_view({'post': 'create_payment_link'})(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('stripe.checkout.Session.create', side_effect=Exception("Stripe error"))
    def test_checkout_session_stripe_error(self, mock_session_create):
        request = self.factory.post('/checkout-session', data={
            'user_id': 1,
            'amount': '100.00',
            'product_name': 'Test Product'
        })
        
        response = StripePaymentView.as_view({'post': 'checkout_session'})(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    unittest.main()