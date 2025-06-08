# Payflow API

Payflow API is a Django-based, API-only payment gateway project designed to facilitate business payments using Stripe and PayPal. It provides endpoints for creating and managing payments, handling webhooks, and managing users, merchants, payment methods, transactions, and subscriptions.

## Features

- **API-Only**: No frontend, designed for integration with web or mobile apps.
- **Stripe & PayPal Integration**: Supports payment processing via Stripe (PayPal support can be extended similarly).
- **User & Merchant Management**: Custom user and merchant models for business logic.
- **Payment Methods**: Store and manage multiple payment methods per user.
- **Transactions & Logs**: Track all payment transactions and their logs for auditing.
- **Subscriptions**: Basic subscription management for recurring payments.
- **Signals**: Custom signals for payment processed, failed, and user balance updates.
- **RESTful Endpoints**: Built with Django REST Framework for robust API design.
- **Versioned API**: Supports versioning for future-proofing endpoints.

## Project Structure

```
payflow_api/
├── payflow/                # Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── payment_gateway/        # Main app for payment logic
│   ├── models.py           # User, Merchant, PaymentMethod, Transaction, etc.
│   ├── serializers.py      # DRF serializers for all models
│   ├── views.py            # Stripe/PayPal payment endpoints and webhooks
│   ├── urls.py             # App-specific URL routing
│   ├── signals.py          # Custom Django signals
│   └── tests/              # Unit tests for views and serializers
└── requirements.txt        # Python dependencies
```

## Key Endpoints

- `POST /api/v1/payment-intent/` — Create a Stripe payment intent
- `POST /api/v1/payment-link/` — Generate a Stripe payment link
- `POST /api/v1/checkout-session/` — Create a Stripe checkout session
- `POST /api/v1/webhook/stripe/` — Stripe webhook handler
- (Extendable for PayPal and other gateways)

## Models

- **User**: Custom user with balance and contact info
- **Merchant**: Business entity accepting payments
- **PaymentMethod**: Stores user payment methods (card, wallet, etc.)
- **Transaction**: Records each payment attempt
- **TransactionLog**: Logs events for each transaction
- **PaymentGateway**: Stores gateway credentials
- **Subscriptions**: Manages recurring plans

## Testing

- Unit tests for views and serializers are provided in `payment_gateway/tests/`.
- Use `python manage.py test payment_gateway/tests/` to run all tests.

## Setup & Usage

1. **Clone the repository**
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** in a `.env` file (see `settings.py` for required keys like `STRIPE_SECRET_KEY`).
4. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

6. **Use API endpoints** with tools like Postman or curl.

## Stripe Test Payments

- Use Stripe test keys and test card numbers (e.g., `4242 4242 4242 4242`) for development.
- Webhook endpoints can be tested locally using the [Stripe CLI](https://stripe.com/docs/stripe-cli).

## License

This project is for educational and demonstration purposes. Adapt and secure for production use as needed.
