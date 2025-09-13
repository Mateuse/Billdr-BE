DEFAULT_CURRENCY = "CAD"

BUSINESS_OWNER_RELATED_NAME = "business_owner"
CUSTOMER_RELATED_NAME = "customer"
INVOICE_RELATED_NAME = "invoice"

COMPANY_NAME_FIELD_NAME = "company_name"
ID_FIELD_NAME = "id"
NAME_FIELD_NAME = "name"
EMAIL_FIELD_NAME = "email"
DUE_DATE_FIELD_NAME = "due_date"
ISSUED_AT_FIELD_NAME = "issued_at"
TOTAL_AMOUNT_FIELD_NAME = "total_amount"
AMOUNT_PAID_FIELD_NAME = "amount_paid"
STATUS_FIELD_NAME = "status"
UPDATED_AT_FIELD_NAME = "updated_at"
NUMBER_FIELD_NAME = "number"
CURRENCY_FIELD_NAME = "currency"
OWNER_FIELD_NAME = "owner"
CUSTOMER_FIELD_NAME = "customer"
OWNER_NAME_FIELD_NAME = "owner_name"
CUSTOMER_NAME_FIELD_NAME = "customer_name"
OWNER_COMPANY_NAME_SOURCE = "owner.company_name"
CUSTOMER_NAME_SOURCE = "customer.name"
PAYMENT_STATUS_FIELD_NAME = "payment_status"

AMOUNT_PAID_FIELD_NAME = "amount_paid"
INVOICE_FIELD_NAME = "invoice"

INVOICE_STATUS_CHOICES = [
    ("sent", "Sent"),
    ("partial", "Partially Paid"),
    ("paid", "Paid"),
    ("canceled", "Canceled"),
    ("overdue", "Overdue"),
    ("refunded", "Refunded"),
]

INVOICE_STATUS_SENT = "sent"
INVOICE_STATUS_PARTIALLY_PAID = "partial"
INVOICE_STATUS_PAID = "paid"
INVOICE_STATUS_CANCELED = "canceled"
INVOICE_STATUS_OVERDUE = "overdue"
INVOICE_STATUS_REFUNDED = "refunded"

PAYMENT_STATUS_CHOICES = [
    ("requires_payment_method", "Requires Payment Method"),
    ("requires_confirmation", "Requires Confirmation"),
    ("requires_action", "Requires Action"),
    ("processing", "Processing"),
    ("succeeded", "Succeeded"),
    ("canceled", "Canceled"),
    ("refunded", "Refunded"),
]

PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD = "requires_payment_method"
PAYMENT_STATUS_REQUIRES_CONFIRMATION = "requires_confirmation"
PAYMENT_STATUS_REQUIRES_ACTION = "requires_action"
PAYMENT_STATUS_PROCESSING = "processing"
PAYMENT_STATUS_SUCCEEDED = "succeeded"
PAYMENT_STATUS_CANCELED = "canceled"
PAYMENT_STATUS_REFUNDED = "refunded"

STRIPE_PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
STRIPE_PAYMENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"

STRIPE_CHARGE_DISPUTE_CREATED = "charge.dispute.created"
STRIPE_REFUND_CREATED = "refund.created"
STRIPE_REFUND_UPDATED = "refund.updated"

STRIPE_WEBHOOK_SECRET_KEY = "STRIPE_WEBHOOK_SECRET"
STRIPE_API_SECRET_KEY = "STRIPE_API_SECRET"
STRIPE_API_PK_KEY = "STRIPE_API_PK"

PAYMENT_METHOD_CARD = "card"


STRIPE_PAYMENT_STATUS_MAPPING = {
    "requires_payment_method": PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
    "requires_confirmation": PAYMENT_STATUS_REQUIRES_CONFIRMATION,
    "requires_action": PAYMENT_STATUS_REQUIRES_ACTION,
    "processing": PAYMENT_STATUS_PROCESSING,
    "succeeded": PAYMENT_STATUS_SUCCEEDED,
    "canceled": PAYMENT_STATUS_CANCELED,
}

TEST_COMPANY_NAME_TECHCORP = "TechCorp Solutions"
TEST_COMPANY_NAME_DESIGN_STUDIO = "Design Studio Pro"
TEST_COMPANY_NAME_CONSULTING = "Consulting Experts"

TEST_CUSTOMER_NAME_ALICE = "Alice Johnson"
TEST_CUSTOMER_EMAIL_ALICE = "alice@example.com"
TEST_CUSTOMER_NAME_BOB = "Bob Smith"
TEST_CUSTOMER_EMAIL_BOB = "bob@example.com"
TEST_CUSTOMER_NAME_CAROL = "Carol Wilson"
TEST_CUSTOMER_EMAIL_CAROL = "carol@example.com"
TEST_CUSTOMER_NAME_DAVID = "David Brown"
TEST_CUSTOMER_EMAIL_DAVID = "david@example.com"
TEST_CUSTOMER_NAME_EMMA = "Emma Davis"
TEST_CUSTOMER_EMAIL_EMMA = "emma@example.com"
TEST_CUSTOMER_NAME_FRANK = "Frank Miller"
TEST_CUSTOMER_EMAIL_FRANK = "frank@example.com"

POPULATE_TEST_DATA_HELP = "Populate database with test data"
POPULATE_CREATING_MESSAGE = "Creating test data..."
POPULATE_SUCCESS_MESSAGE_TEMPLATE = """Successfully created test data:
- {business_owners_count} business owners
- {customers_count} customers
- {invoices_count} invoices
All invoices have no transactions/payments (amount_paid = 0)"""