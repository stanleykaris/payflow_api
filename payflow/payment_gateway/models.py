from django.db import models
from django.contrib.auth.models import User
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class Merchant(models.Model):
    merchant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant', null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    METHOD_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ]
    CARD_BRANDS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('diners_club', 'Diners Club'),
        ('jcb', 'JCB'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    gateway_customer_id = models.CharField(max_length=100, blank=True)
    gateway_payment_method_token = models.CharField(max_length=100, blank=True)
    last_four_digits = models.CharField(max_length=4, blank=True)
    expiry_date = models.CharField(max_length=5, blank=True)
    card_brand = models.CharField(max_length=20, choices=CARD_BRANDS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_method_type_display()} - {self.last_four_digits}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    merchant= models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='transaction_log', default=None, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transaction {self.id} - {self.amount}"

class TransactionLog(models.Model):
    LOG_TYPES = [
        ('initiated', 'Initiated'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
        ('voided', 'Voided'),
        ('partially_refunded', 'Partially Refunded'),
        ('partially_voided', 'Partially Voided'),
        ('chargeback', 'Chargeback'),
        ('reversed', 'Reversed'),
        ('settled', 'Settled'),
        ('disputed', 'Disputed'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='logs')
    log_message = models.TextField()
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_logs')
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_logs')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_logs')
    additional_info = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Log for Transaction {self.transaction.id}"

class PaymentGateway(models.Model):
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    api_secret = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    plan_name = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    def __str__(self) -> str:
        return f"{self.plan_name} - {self.user.username}"