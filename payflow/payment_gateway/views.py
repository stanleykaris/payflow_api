import os
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, TransactionLog, Merchant, PaymentMethod, User
from .signals import payment_processed, payment_failed, user_balance_updated
import stripe

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
class StripePaymentView(ViewSet):
    """
    API endpoints for Stripe payment processing.
    
    Version: v1
    """
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    def create_payment_intent(self, request):
        try:
            amount = request.data.get('amount', 0)
            payment_method_id = request.data.get('payment_method_id', '')
            user_id = request.data.get('user_id')
        
            if amount is None or payment_method_id is None or user_id is None or float(amount) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Amount must be a positive number, and payment method ID, and user ID are required.")
            
            user = get_object_or_404(User, pk=user_id)
            
            intent = stripe.PaymentIntent.create(
                amount=int(Decimal(amount) * 100),
                currency='usd',
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                metadata={
                    'user_id': user_id,
                    'description': request.data.get('description', '')
                }
            )

            if intent.status == 'succeeded':
                # Get merchant - either from request or default to first merchant
                merchant_id = request.data.get('merchant_id')
                if merchant_id:
                    merchant = get_object_or_404(Merchant, pk=merchant_id)
                else:
                    merchant = Merchant.objects.first()
                
                # Get payment method - either from request or default to first for user
                payment_method = PaymentMethod.objects.filter(user=user).first()
                if not payment_method:
                    # Create a default payment method if none exists
                    payment_method = PaymentMethod.objects.create(
                        user=user,
                        method_type='credit_card',
                        gateway_payment_method_token=payment_method_id,
                        last_four_digits='1234'  # Default value
                    )
                
                transaction = Transaction.objects.create(
                    user=user,
                    merchant=merchant,
                    payment_method=payment_method,
                    amount=Decimal(amount),
                    description=request.data.get('description', ''),
                    status='completed'
                )
                
                # Send signal that payment was processed
                payment_processed.send(
                    sender=self.__class__,
                    transaction=transaction
                )
            
            return Response(status=status.HTTP_200_OK, data=intent)
            
        except stripe.error.CardError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.error.message)
        except stripe.error.StripeError as e:
            # If we have user info, create a failed transaction and send signal
            if 'user' in locals():
                merchant = Merchant.objects.first()
                payment_method = PaymentMethod.objects.filter(user=user).first()
                if payment_method:
                    transaction = Transaction.objects.create(
                        user=user,
                        merchant=merchant,
                        payment_method=payment_method,
                        amount=Decimal(amount),
                        description=request.data.get('description', ''),
                        status='failed'
                    )
                    
                    payment_failed.send(
                        sender=self.__class__,
                        transaction=transaction,
                        error_message=str(e)
                    )
                
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="An internal error occurred.")
            
    def create_payment_link(self, request):
        try:
            user_id = request.data.get('user_id')
            amount = request.data.get('amount', 0)
            product_name = request.data.get('product_name', 'Product')
            description = request.data.get('description', '')
            
            if not user_id or not amount:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="User ID and amount are required.")
            
            user = get_object_or_404(User, pk=user_id)
            
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': int(Decimal(amount) * 100),
                    },
                    'quantity': 1,
                }],
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        'url': request.build_absolute_uri(reverse('success')),
                    },
                },
                metadata={
                    'user_id': user_id,
                    'description': description
                }
            )

            # Get merchant - either from request or default to first merchant
            merchant_id = request.data.get('merchant_id')
            if merchant_id:
                merchant = get_object_or_404(Merchant, pk=merchant_id)
            else:
                merchant = Merchant.objects.first()
                if not merchant:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="No merchant available.")
            
            # Get payment method - either from request or default to first for user
            payment_method = PaymentMethod.objects.filter(user=user).first()
            if not payment_method:
                # Create a default payment method if none exists
                payment_method = PaymentMethod.objects.create(
                    user=user,
                    method_type='credit_card',
                    gateway_payment_method_token='pm_default',
                    last_four_digits='1234'  # Default value
                )
            
            transaction = Transaction.objects.create(
                user=user,
                merchant=merchant,
                payment_method=payment_method,
                amount=Decimal(amount),
                description=description,
                status='pending'
            )
            
            # Log the transaction
            TransactionLog.objects.create(
                transaction=transaction,
                log_message=f"Payment link created: {payment_link.url}",
                log_type='initiated',
                user=user
            )
            
            return Response({
                'payment_link': payment_link.url,
                'transaction_id': transaction.id
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="An internal error occurred.")
        
    def checkout_session(self, request):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="User ID is required.")
                
            user = get_object_or_404(User, pk=user_id)
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': request.data.get('product_name', 'Product'),
                            },
                            'unit_amount': int(Decimal(request.data.get('amount', 0)) * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                customer=user.stripe_customer_id if hasattr(user, 'stripe_customer_id') else None,\
                success_url=request.build_absolute_uri(reverse('success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('cancel')) + '?cancel=true',
                metadata={
                    'user_id': user_id,
                    'description': request.data.get('description', '')
                }
            )
            return Response(status=status.HTTP_200_OK, data=session)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="An internal error occurred.")
        
    def payment_success(self, request):
        if 'success' in request.GET or 'session_id' in request.GET:
            session_id = request.GET.get('session_id')
            if session_id:
                # Try to find transaction related to this session
                transaction = Transaction.objects.filter(
                    payment_method__gateway_payment_method_token=session_id
                ).first()
                
                if transaction:
                    transaction.status = 'completed'
                    transaction.save()
                    
                    # Send signal that payment was processed
                    payment_processed.send(
                        sender=self.__class__,
                        transaction=transaction
                    )
                    
            return Response(status=status.HTTP_200_OK, data="Payment was successful!")
    def log_transaction(self, request, user, intent, log_type):
        merchant_id = intent.metadata.get('merchant_id') if hasattr(intent, 'metadata') else None
        if not merchant_id:
            logger.error("Merchant ID is missing in intent metadata.")
            return
        merchant = get_object_or_404(Merchant, pk=merchant_id)
        payment_method = get_object_or_404(PaymentMethod, user=user)
        transaction = Transaction.objects.create(
            user=user,
            merchant=merchant,
            payment_method=payment_method,
            amount=Decimal(intent.amount / 100),
            description=intent.metadata.get('description', ''),
            status='completed' if log_type == 'succeeded' else 'failed'
        )
        TransactionLog.objects.create(
            transaction=transaction,
            log_message=f"Transaction {log_type} for amount {intent.amount}",
            log_type=log_type,
            user=user
        )
        if 'success' in request.GET or 'session_id' in request.GET:
            session_id = request.GET.get('session_id')
            if session_id:
                # Try to find transaction related to this session
                transaction = Transaction.objects.filter(
                    payment_method__gateway_payment_method_token=session_id
                ).first()
                
                if transaction:
                    transaction.status = 'completed'
                    transaction.save()
                    
                    # Send signal that payment was processed
                    payment_processed.send(
                        sender=self.__class__,
                        transaction=transaction
                    )
        if not merchant:
            logger.error("Merchant not found for the provided ID.")
            return
        if not payment_method:
            logger.error("Payment method not found for the user.")
            return
        if not intent or not hasattr(intent, 'amount'):
            logger.error("Invalid payment intent or amount.")
            return
        
        TransactionLog.objects.create(
            transaction=transaction,
            log_message=f"Transaction {log_type} for amount {intent.amount}",
            log_type=log_type,
            user=user
        )

class StripeWebhookView(APIView):
    """
    Webhook handler for Stripe events.
    
    Version: v1
    """
    def post(self, request):
        # Verify the webhook signature, process the event, and return a response
        if 'HTTP_STRIPE_SIGNATURE' not in request.META:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Missing Stripe signature header")
        
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe.api_key  # Use your actual Stripe webhook secret here
            )
            # Handle Stripe webhook events
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                logger.info(f"PaymentIntent was successful: {payment_intent.id}")
                self.log_transaction_event(payment_intent.id, 'succeeded')
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                logger.error(f"PaymentIntent failed: {payment_intent.id}")
                self.log_transaction_event(payment_intent.id, 'failed')
            elif event.type == 'checkout.session.completed':
                session = event.data.object
                logger.info(f"Checkout session completed: {session.id}")
                self.log_transaction_event(session, 'completed')
            elif event.type == 'checkout.session.async_payment_succeeded':
                session = event.data.object
                logger.info(f"Async payment succeeded for session: {session.id}")
                self.log_transaction_event(session, 'completed')
            elif event.type == 'checkout.session.async_payment_failed':
                session = event.data.object
                logger.error(f"Async payment failed for session: {session.id}")
                self.log_transaction_event(session, 'failed')
            else:
                logger.info(f"Unhandled event type: {event.type}")
            return Response(status=status.HTTP_200_OK, data="Webhook received successfully")
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f"Invalid signature: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="An internal error occurred.")

    def log_transaction_event(self, event_object, status):
        payment_method_token = getattr(event_object, 'payment_method', None)
        if payment_method_token:
            transaction = Transaction.objects.filter(payment_method__gateway_payment_method_token=payment_method_token).first()
            if transaction:
                old_status = transaction.status
                transaction.status = status
                transaction.save()
                
                # Create transaction log
                TransactionLog.objects.create(
                    transaction=transaction,
                    log_message="Webhook event processed",
                    log_type=status,
                    user=transaction.user,
                    merchant=transaction.merchant,
                    payment_method=transaction.payment_method,
                    additional_info=event_object.metadata if hasattr(event_object, 'metadata') else None
                )
                
                # Send appropriate signal based on status
                if status == 'completed' or status == 'succeeded':
                    payment_processed.send(
                        sender=self.__class__,
                        transaction=transaction
                    )
                elif status == 'failed':
                    payment_failed.send(
                        sender=self.__class__,
                        transaction=transaction,
                        error_message=f"Payment failed for transaction {transaction.id}"
                    )