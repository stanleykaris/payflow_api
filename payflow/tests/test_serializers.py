import unittest
from unittest.mock import patch
from payment_gateway.serializers import UserSerializer, TransactionSerializer, SubscriptionSerializer, TransactionLogSerializer
from payment_gateway.models import User, Transaction, Subscriptions, TransactionLog

class TestSerializers(unittest.TestCase):

    def setUp(self):
        self.user = User(username='testuser', email='test@example.com', balance=100.00)

    def test_user_serializer_serializes_data_correctly(self):
        serializer = UserSerializer(self.user)
        # Check specific fields individually instead of the whole dict
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertEqual(serializer.data['balance'], '100.00')
        self.assertIn('id', serializer.data)
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)

    def test_transaction_serializer_includes_status_display(self, mock_get_status_display):
        transaction = Transaction(status='completed')
        serializer = TransactionSerializer(transaction)
        self.assertEqual(serializer.data['status_display'], 'Completed')
        

    def test_subscription_serializer_serializes_data_correctly(self):
        subscription = Subscriptions(plan_name='Premium', status='active')
        serializer = SubscriptionSerializer(subscription)
        self.assertEqual(serializer.data['plan_name'], 'Premium')
        self.assertEqual(serializer.data['status'], 'active')

    def test_user_serializer_handles_missing_phone(self):
        serializer = UserSerializer(self.user)
        self.assertNotIn('phone', serializer.data)

    def test_transaction_log_serializer_handles_null_additional_info(self):
        transaction_log = TransactionLog(additional_info=None)
        serializer = TransactionLogSerializer(transaction_log)
        self.assertIsNone(serializer.data['additional_info'])

if __name__ == '__main__':
    unittest.main()