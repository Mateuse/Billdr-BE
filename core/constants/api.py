
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503

REQUEST_CONTEXT_KEY = "request"


HEALTH_OK_MESSAGE = "Service is healthy"
HEALTH_DB_OK_MESSAGE = "Database is connected"
HEALTH_DB_ERROR_MESSAGE = "Database is not connected"

USER_ALREADY_EXISTS_MESSAGE = "User already exists"
USER_CREATION_FAILED_MESSAGE = "User creation failed"
USER_CREATION_SUCCESS_MESSAGE = "User created successfully"
BUSINESS_OWNER_RETRIEVAL_SUCCESS_MESSAGE = "Business owners retrieved successfully"
CUSTOMER_RETRIEVAL_SUCCESS_MESSAGE = "Customers retrieved successfully"


INVOICE_CREATION_FAILED_MESSAGE = "Invoice creation failed"
INVOICE_CREATION_SUCCESS_MESSAGE = "Invoice created successfully"
INVOICE_DUE_DATE_IN_PAST_MESSAGE = "Due date is in the past"
INVOICE_STATUS_INVALID_MESSAGE = "Invalid status"
INVOICE_TOTAL_AMOUNT_INVALID_MESSAGE = "Total amount is invalid"
INVOICE_AMOUNT_PAID_INVALID_MESSAGE = "Amount paid is invalid"
INVOICE_OWNER_REQUIRED_MESSAGE = "Owner is required"
INVOICE_CUSTOMER_REQUIRED_MESSAGE = "Customer is required"
INVOICE_RETRIEVAL_SUCCESS_MESSAGE = "Invoices retrieved successfully"
INVOICE_RETRIEVAL_FAILED_MESSAGE = "Invoices retrieval failed"
INVOICE_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE = "Invoice retrieved successfully"
INVOICE_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE = "Invoice not found"

BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE = "Business owner retrieved successfully"
BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE = "Business owner not found"
CUSTOMER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE = "Customer retrieved successfully"
CUSTOMER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE = "Customer not found"

BUSINESS_OWNER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE = "Business owner invoices retrieved successfully"
BUSINESS_OWNER_INVOICES_RETRIEVAL_FAILED_MESSAGE = "Business owner not found"

CUSTOMER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE = "Customer invoices retrieved successfully"
CUSTOMER_INVOICES_RETRIEVAL_FAILED_MESSAGE = "Customer not found"

INVOICE_DELETION_SUCCESS_MESSAGE = "Invoice deleted successfully"
INVOICE_DELETION_FAILED_MESSAGE = "Invoice not found"
BUSINESS_OWNER_DELETION_SUCCESS_MESSAGE = "Business owner deleted successfully"
BUSINESS_OWNER_DELETION_FAILED_MESSAGE = "Business owner not found"
CUSTOMER_DELETION_SUCCESS_MESSAGE = "Customer deleted successfully"
CUSTOMER_DELETION_FAILED_MESSAGE = "Customer not found"

ALREADY_EXISTS_MESSAGE = "already exists"

PAYMENT_CREATION_SUCCESS_MESSAGE = "Payment processed successfully"
PAYMENT_CREATION_FAILED_MESSAGE = "Payment processing failed"
PAYMENT_AMOUNT_INVALID_MESSAGE = "Payment amount is invalid"
PAYMENT_INVOICE_NOT_FOUND_MESSAGE = "Invoice not found"
PAYMENT_STRIPE_ERROR_MESSAGE = "Stripe payment processing error"
PAYMENT_INVOICE_ALREADY_PAID_MESSAGE = "Invoice is already fully paid"
PAYMENT_AMOUNT_TOO_SMALL_MESSAGE = "Payment amount must be at least $1.00"
PAYMENT_AMOUNT_MUST_BE_POSITIVE_MESSAGE = "Payment amount must be greater than 0"
PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE = "Payment amount cannot exceed amount due"
PAYMENT_AMOUNT_REQUIRED_MESSAGE = "Payment amount is required"

REFUND_SUCCESS_MESSAGE = "Refund processed successfully"
REFUND_FAILED_MESSAGE = "Refund processing failed"
REFUND_INVALID_PAYMENT_MESSAGE = "Cannot refund: payment not found or not successful"
REFUND_ALREADY_REFUNDED_MESSAGE = "Payment has already been refunded"
REFUND_STRIPE_ERROR_MESSAGE = "Stripe refund processing error"
REFUND_NOT_ALLOWED_MESSAGE = "Refund not allowed for this payment"

STRIPE_API_VERSION = "2024-12-18.acacia"
STRIPE_CURRENCY_CAD = "cad"
STRIPE_PAYMENT_INTENT_STATUS_SUCCEEDED = "succeeded"
STRIPE_PAYMENT_INTENT_STATUS_REQUIRES_PAYMENT_METHOD = "requires_payment_method"
STRIPE_PAYMENT_INTENT_STATUS_REQUIRES_CONFIRMATION = "requires_confirmation"
STRIPE_PAYMENT_INTENT_STATUS_REQUIRES_ACTION = "requires_action"
STRIPE_PAYMENT_INTENT_STATUS_PROCESSING = "processing"
STRIPE_PAYMENT_INTENT_STATUS_CANCELED = "canceled"

PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE = "Payment history retrieved successfully"
PAYMENT_HISTORY_RETRIEVAL_FAILED_MESSAGE = "Payment history retrieval failed"
PAYMENT_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE = "Payment retrieved successfully"
PAYMENT_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE = "Payment not found"

API_RESPONSE_CODE_KEY = "code"
API_RESPONSE_MESSAGE_KEY = "message"
API_RESPONSE_DATA_KEY = "data"

HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_DELETE = "DELETE"

CUSTOMER_EMAIL_FIELD = "customer_email"
CUSTOMER_NAME_FIELD = "customer_name"
BUSINESS_OWNER_NAME_FIELD = "business_owner_name"
INVOICE_NUMBER_FIELD = "invoice_number"
PAYMENT_INTENT_ID_FIELD = "payment_intent_id"
CLIENT_SECRET_FIELD = "client_secret"
AMOUNT_FIELD = "amount"
PAYMENT_AMOUNT_FIELD = "payment_amount"
CURRENCY_FIELD_API = "currency"
STRIPE_PAYMENTS_FIELD = "stripe_payments"
INVOICE_TOTAL_FIELD = "invoice_total"
INVOICE_AMOUNT_PAID_FIELD = "invoice_amount_paid"
INVOICE_STATUS_FIELD_API = "invoice_status"
INVOICE_PAYMENT_STATUS_FIELD_API = "invoice_payment_status"
PAYMENT_CREATED_FIELD = "payment_created"
PAYMENT_ID_FIELD = "payment_id"
ERROR_FIELD = "error"

INVOICE_ALREADY_PAID_MESSAGE = "Invoice is already paid in full"
PAYMENT_INTENT_CREATED_MESSAGE = "Payment intent created successfully"
INVOICE_NOT_FOUND_MESSAGE = "Invoice not found"
INVOICE_ID_REQUIRED_MESSAGE = "invoice_id is required"
INVALID_JSON_MESSAGE = "Invalid JSON"
PROCESSING_SUCCESSFUL_PAYMENT_MESSAGE = "Processing successful payment"
PROCESSING_FAILED_PAYMENT_MESSAGE = "Processing failed payment"
SUCCESSFULLY_PROCESSED_PAYMENT_MESSAGE = "Successfully processed payment"
NO_PAYMENT_PROCESSED_MESSAGE = "No payment processed"
FAILED_TO_PROCESS_PAYMENT_MESSAGE = "Failed to process payment"
PROCESSING_SUCCESSFUL_REFUND_MESSAGE = "Processing successful refund"
SUCCESSFULLY_PROCESSED_REFUND_MESSAGE = "Successfully processed refund for payment"
FAILED_TO_PROCESS_REFUND_MESSAGE = "Failed to process refund for payment"
REFUND_PAYMENT_INTENT_NOT_FOUND_MESSAGE = "Payment intent not found for refund"
ERROR_IN_TEST_PAYMENT_MESSAGE = "Error in test payment creation"

RECEIVED_WEBHOOK_CALL_MESSAGE = "Received webhook call from Stripe"
MISSING_SIGNATURE_HEADER_MESSAGE = "Missing Stripe signature header"
MISSING_SIGNATURE_HEADER_ERROR = "Missing signature header"
WEBHOOK_NOT_CONFIGURED_MESSAGE = "Stripe webhook secret not configured"
WEBHOOK_NOT_CONFIGURED_ERROR = "Webhook not configured"
WEBHOOK_SECRET_CONFIGURED_MESSAGE = "Webhook secret configured"
INVALID_PAYLOAD_MESSAGE = "Invalid payload"
INVALID_SIGNATURE_MESSAGE = "Invalid signature"
PROCESSING_EVENT_TYPE_MESSAGE = "Processing event type"
PROCESSING_PAYMENT_SUCCEEDED_MESSAGE = "Processing payment_intent.succeeded event"
PROCESSING_PAYMENT_FAILED_MESSAGE = "Processing payment_intent.payment_failed event"
PROCESSING_REFUND_CREATED_MESSAGE = "Processing refund.created event"
PROCESSING_REFUND_UPDATED_MESSAGE = "Processing refund.updated event" 
PROCESSING_CHARGE_DISPUTE_CREATED_MESSAGE = "Processing charge.dispute.created event"
UNHANDLED_EVENT_TYPE_MESSAGE = "Unhandled event type"
WEBHOOK_SUCCESS_RESPONSE = "Success"
WEBHOOK_PROCESSING_ERROR_MESSAGE = "Error processing webhook"
WEBHOOK_PROCESSING_FAILED_MESSAGE = "Webhook processing failed"

SELECT_ONE_QUERY = "SELECT 1"
INVOICE_ID_METADATA_KEY = "invoice_id"
INVOICE_ID_NOT_FOUND_ERROR = "invoice_id not found in Stripe payment metadata"

STATUS_OVERDUE = "overdue"
STATUS_PARTIAL = "partial"
STATUS_SENT = "sent"
STATUS_PAID = "paid"
STATUS_SUCCEEDED = "succeeded"
STATUS_CANCELED = "canceled"

BUSINESS_OWNER_FIELD_NAME = "business_owner"
STRIPE_PAYMENTS_RELATED_NAME = "stripe_payments"

STRIPE_PAYMENT_METHOD_TEST_CARD = "pm_test_card"
STRIPE_PAYMENT_SUCCEEDED_STATUS = "succeeded"
STRIPE_PAYMENT_INTENT_FAILED_ERROR_KEYS = ["code", "message"]

INVOICE_NUMBER_PREFIX = "INV"
INVOICE_NUMBER_FORMAT = "INV-{year}{month:02d}-{count:04d}"

NO_PAYMENT_RETURNED_ERROR = "No payment returned from payment service"
FOUND_STRIPE_PAYMENTS_MESSAGE = "Found {count} Stripe payments for invoice {number}"
PROCESSING_PAYMENT_MESSAGE = "Processing payment {payment_id}"
ERROR_PROCESSING_PAYMENT_MESSAGE = "Error processing payment {payment_id}: {error}"

CUSTOMER_BUSINESS_OWNER_AMOUNT_REQUIRED = "Customer ID, Business Owner ID, and Amount Paid are required"
NO_UNPAID_INVOICE_FOUND = "No unpaid invoice found for this customer and business owner"

HTTP_STRIPE_SIGNATURE_HEADER = "HTTP_STRIPE_SIGNATURE"

ORDERING_NEWEST_FIRST = ["-issued_at", "-id"]
ORDERING_NEWEST_PAYMENT_FIRST_BY_TIME = ["-created_at", "-id"]
ORDERING_NEWEST_PAYMENT_FIRST = ["-created_at", "-id"]

PAYMENT_STATUS_HELP_TEXT = "Payment status based on Stripe payment intent status"

TRANSACTION_ID_FIELD = "transaction_id"
AMOUNT_REFUNDED_FIELD = "amount_refunded"
CURRENCY_FIELD = "currency"
INVOICE_ID_FIELD = "invoice_id"
INVOICE_NUMBER_FIELD = "invoice_number"
PAYMENT_INTENT_ID_FIELD_RESPONSE = "payment_intent_id"
PAYMENT_CREATED_FIELD = "payment_created"
AMOUNT_FIELD_RESPONSE = "amount"
ERROR_FIELD = "error"
STRIPE_PAYMENTS_FIELD = "stripe_payments"
INVOICE_TOTAL_FIELD = "invoice_total"
INVOICE_AMOUNT_PAID_FIELD = "invoice_amount_paid"
INVOICE_STATUS_FIELD = "invoice_status"
INVOICE_PAYMENT_STATUS_FIELD = "invoice_payment_status"

INVOICE_NUMBER_SERIALIZER_FIELD = "invoice_number"

EXCEEDS_AMOUNT_DUE_VALIDATION = "exceeds amount due"
MUST_BE_AT_LEAST_VALIDATION = "must be at least"
MUST_BE_GREATER_THAN_ZERO_VALIDATION = "must be greater than 0"

STRIPE_PAYMENT_STATUS_SUCCEEDED = "succeeded"
TEST_PAYMENT_METHOD_ID = "pm_test_card"

REFUND_STATUS_SUCCEEDED = "succeeded"
PAYMENT_METHOD_TYPES_CARD = "card"
SERIALIZER_FIELD_TRANSACTION_TIME = "transaction_time"
SERIALIZER_FIELD_AMOUNT_PAID = "amount_paid"
SERIALIZER_FIELD_CUSTOMER = "customer"
SERIALIZER_FIELD_CUSTOMER_NAME = "customer_name"
SERIALIZER_FIELD_BUSINESS_OWNER = "business_owner"
SERIALIZER_FIELD_BUSINESS_OWNER_NAME = "business_owner_name"
SERIALIZER_FIELD_INVOICE_NUMBER = "invoice_number"
SERIALIZER_FIELD_STRIPE_PAYMENT = "stripe_payment"
SERIALIZER_FIELD_TRANSACTION_TYPE = "transaction_type"
SERIALIZER_FIELD_STATUS = "status"
SERIALIZER_FIELD_INVOICE_ID = "invoice_id"
SERIALIZER_FIELD_INVOICE = "invoice"
SERIALIZER_FIELD_CREATED_AT = "created_at"
SERIALIZER_FIELD_CURRENCY = "currency"
SERIALIZER_FIELD_ID = "id"

TRANSACTION_TYPE_PAYMENT = "payment"
TRANSACTION_TYPE_REFUND = "refund"

PAYMENT_METHOD_TYPES_LIST = ["card"]

STRIPE_AUTOMATIC_PAYMENT_METHODS_ENABLED = False

STRIPE_METADATA_INVOICE_NUMBER = "invoice_number"
STRIPE_METADATA_PAYMENT_AMOUNT = "payment_amount"
STRIPE_METADATA_STRIPE_PAYMENT_ID = "stripe_payment_id"
STRIPE_METADATA_REFUND_ID = "refund_id"
STRIPE_METADATA_ORIGINAL_PAYMENT_INTENT = "original_payment_intent"
STRIPE_METADATA_REFUND_AMOUNT = "refund_amount"

LOG_PAYMENT_REQUEST_MESSAGE = "Payment request for invoice {invoice_id}: customer_email={customer_email}, payment_amount={payment_amount}"
LOG_CONVERTED_PAYMENT_AMOUNT_MESSAGE = "Converted payment amount to Decimal: {payment_amount}"
LOG_INVALID_PAYMENT_AMOUNT_MESSAGE = "Invalid payment amount format: {payment_amount}"
LOG_STRIPE_AMOUNT_MESSAGE = "Stripe amount in cents: {amount_in_cents}"
LOG_CREATED_PAYMENT_INTENT_MESSAGE = "Created payment intent {payment_intent_id} for invoice {invoice_number}"
LOG_STRIPE_ERROR_MESSAGE = "Stripe error creating payment intent: {error}"
LOG_ERROR_CREATING_PAYMENT_INTENT_MESSAGE = "Error creating payment intent: {error}"
LOG_ERROR_CREATING_PAYMENT_INTENT_FOR_INVOICE_MESSAGE = "Error creating payment intent for invoice {invoice_id}: {error}"
LOG_ERROR_PROCESSING_REFUND_MESSAGE = "Error processing refund for payment {stripe_payment_id}: {error}"

FAILED_TO_CREATE_PAYMENT_INTENT_MESSAGE = "Failed to create payment intent: {error}"

STRIPE_ERROR_CODE_CHARGE_ALREADY_REFUNDED = "charge_already_refunded"
PAYMENT_ALREADY_REFUNDED_MESSAGE = "This payment has already been refunded"
STRIPE_REFUND_ERROR_MESSAGE_TEMPLATE = "Stripe refund error: {error}"