from rest_framework import viewsets
from .models import User, Transaction, Merchant, PaymentMethod, TransactionLog, PaymentGateway, Subscriptions
from .serializers import (
    UserSerializer, TransactionSerializer, MerchantSerializer, 
    PaymentMethodSerializer, TransactionLogSerializer, 
    PaymentGatewaySerializer, SubscriptionSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        queryset = PaymentMethod.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

class TransactionLogViewSet(viewsets.ModelViewSet):
    queryset = TransactionLog.objects.all()
    serializer_class = TransactionLogSerializer
    
    def get_queryset(self):
        queryset = TransactionLog.objects.all()
        transaction_id = self.request.query_params.get('transaction_id', None)
        if transaction_id is not None:
            queryset = queryset.filter(transaction_id=transaction_id)
        return queryset

class PaymentGatewayViewSet(viewsets.ModelViewSet):
    queryset = PaymentGateway.objects.all()
    serializer_class = PaymentGatewaySerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        queryset = Subscriptions.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset