from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Transaction, TransactionLog
import logging

logger = logging.getLogger('payflow.payment_gateway.signals')

# Custom signals
payment_processed = Signal()  # Provides transaction instance
payment_failed = Signal()  # Provides transaction instance and error message
user_balance_updated = Signal()  # Provides user instance and amount

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction)
def transaction_post_save(sender, instance: Transaction, created: bool, **kwargs) -> None:
    """Log transaction creation and updates."""
    if created:
        logger.info(f"New transaction created: {instance.id} for amount {instance.amount}")
    else:
        status_dict = dict(Transaction.STATUS_CHOICES)
        if instance.status in status_dict:
            logger.info(f"Transaction updated: {instance.id}, status: {instance.status}")
        else:
            logger.warning(f"Transaction updated: {instance.id} with invalid status: {instance.status}")

@receiver(payment_processed)
def update_user_balance(sender, transaction, **kwargs):
    """Update user balance when payment is processed successfully"""
    if transaction.status == 'completed':
        user = transaction.user
        user.balance = F('balance') + transaction.amount
        try:
            user.save()
            user_balance_updated.send(
                sender=Transaction,
                user=user,
                amount=transaction.amount
            )
            logger.info(f"User {user.id} balance updated: +{transaction.amount}")
        except Exception as e:
            logger.error(f"Failed to update user {user.id} balance: {str(e)}")

@receiver(payment_failed)
def handle_payment_failure(sender, transaction, error_message, **kwargs):
    """Handle payment failure"""
    logger.error(f"Payment failed for transaction {transaction.id}: {error_message}")
    # Create a transaction log for the failure
    TransactionLog.objects.create(
        transaction=transaction,
        log_message=f"Payment failed: {error_message}",
        log_type='failed',
        user=transaction.user,
        merchant=transaction.merchant,
        payment_method=transaction.payment_method
    )