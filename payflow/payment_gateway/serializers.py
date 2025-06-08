from rest_framework import serializers
from .models import User, Transaction, Merchant, PaymentMethod, TransactionLog, PaymentGateway, Subscriptions

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'balance', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['phone'] == '':
            representation.pop('phone')
        return representation

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'email', 'phone', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

class PaymentMethodSerializer(serializers.ModelSerializer):
    method_type_display = serializers.CharField(source='get_method_type_display', read_only=True)
    card_brand_display = serializers.CharField(source='get_card_brand_display', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'user', 'method_type', 'method_type_display', 'gateway_customer_id', 
                 'gateway_payment_method_token', 'last_four_digits', 'expiry_date', 
                 'card_brand', 'card_brand_display', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'merchant', 'payment_method', 'amount', 
                 'description', 'status', 'status_display', 'created_at']

class TransactionLogSerializer(serializers.ModelSerializer):
    log_type_display = serializers.CharField(source='get_log_type_display', read_only=True)
    
    class Meta:
        model = TransactionLog
        fields = ['id', 'transaction', 'log_message', 'log_type', 'log_type_display',
                 'user', 'merchant', 'payment_method', 'additional_info', 'created_at']

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'api_key', 'created_at', 'updated_at']
        extra_kwargs = {'api_secret': {'write_only': True}}

class SubscriptionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscriptions
        fields = ['id', 'user', 'plan_name', 'start_date', 'end_date', 'status', 'status_display']