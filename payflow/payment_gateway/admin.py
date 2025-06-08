from django.contrib import admin
from .models import User, Merchant, Transaction, TransactionLog, PaymentMethod, Subscriptions
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display= ('username', 'email', 'phone', 'balance', 'created_at', 'updated_at')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display= ('name', 'email', 'phone', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'last_four_digits', 'expiry_date', 'card_brand', 'created_at')
    search_fields = ('user__username', 'method_type', 'last_four_digits', 'expiry_date', 'card_brand')
    list_filter = ('method_type', 'card_brand', 'created_at')
    ordering = ('-created_at',)
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'merchant', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'merchant__name', 'amount', 'status')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    
@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'log_type', 'created_at')
    search_fields = ('transaction__id', 'log_type')
    list_filter = ('log_type', 'created_at')
    ordering = ('-created_at',)
    
@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'start_date', 'end_date', 'status')
    search_fields = ('user__username', 'plan_name', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-start_date',)