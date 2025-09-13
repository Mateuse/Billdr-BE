# Logging message constants for the Billdr application

# User-related logging messages
USER_CREATED = "User created successfully: {user_type} - {user_id}"
USER_CREATION_FAILED = "Failed to create user: {user_type} - {error}"
USER_RETRIEVED = "User retrieved successfully: {user_type} - {user_id}"
USER_RETRIEVAL_FAILED = "Failed to retrieve user: {user_type} - {user_id}"
USER_DELETED = "User deleted successfully: {user_type} - {user_id}"
USER_DELETION_FAILED = "Failed to delete user: {user_type} - {user_id}"
USER_UPDATED = "User updated successfully: {user_type} - {user_id}"
USER_UPDATE_FAILED = "Failed to update user: {user_type} - {user_id}"

# Invoice-related logging messages
INVOICE_CREATED = "Invoice created successfully: {invoice_id} for customer {customer_id}"
INVOICE_CREATION_FAILED = "Failed to create invoice: {error}"
INVOICE_RETRIEVED = "Invoice retrieved successfully: {invoice_id}"
INVOICE_RETRIEVAL_FAILED = "Failed to retrieve invoice: {invoice_id}"
INVOICE_UPDATED = "Invoice updated successfully: {invoice_id}"
INVOICE_UPDATE_FAILED = "Failed to update invoice: {invoice_id}"
INVOICE_DELETED = "Invoice deleted successfully: {invoice_id}"
INVOICE_DELETION_FAILED = "Failed to delete invoice: {invoice_id}"
INVOICE_STATUS_CHANGED = "Invoice status changed: {invoice_id} from {old_status} to {new_status}"
INVOICE_NUMBER_GENERATED = "Invoice number generated: {invoice_number} for invoice {invoice_id}"

# Payment-related logging messages
PAYMENT_INITIATED = "Payment initiated: {payment_id} for invoice {invoice_id}"
PAYMENT_COMPLETED = "Payment completed successfully: {payment_id}"
PAYMENT_FAILED = "Payment failed: {payment_id} - {error}"
PAYMENT_PROCESSING = "Processing payment: {payment_id}"
STRIPE_WEBHOOK_RECEIVED = "Stripe webhook received: {event_type} - {event_id}"
STRIPE_WEBHOOK_PROCESSED = "Stripe webhook processed successfully: {event_id}"
STRIPE_WEBHOOK_FAILED = "Failed to process Stripe webhook: {event_id} - {error}"

# Transaction-related logging messages
TRANSACTION_CREATED = "Transaction created: {transaction_id} - {transaction_type}"
TRANSACTION_UPDATED = "Transaction updated: {transaction_id}"
TRANSACTION_FAILED = "Transaction failed: {transaction_id} - {error}"

# Database-related logging messages
DB_CONNECTION_SUCCESS = "Database connection established successfully"
DB_CONNECTION_FAILED = "Database connection failed: {error}"
DB_QUERY_EXECUTED = "Database query executed: {query_type}"
DB_QUERY_FAILED = "Database query failed: {query_type} - {error}"

# API-related logging messages
API_REQUEST_RECEIVED = "API request received: {method} {endpoint} from {ip_address}"
API_REQUEST_COMPLETED = "API request completed: {method} {endpoint} - {status_code}"
API_REQUEST_FAILED = "API request failed: {method} {endpoint} - {error}"
INVALID_REQUEST_DATA = "Invalid request data received: {endpoint} - {errors}"
AUTHENTICATION_FAILED = "Authentication failed for request: {endpoint}"
AUTHORIZATION_FAILED = "Authorization failed for user {user_id} on {endpoint}"

# Health check logging messages
HEALTH_CHECK_SUCCESS = "Health check passed: {check_type}"
HEALTH_CHECK_FAILED = "Health check failed: {check_type} - {error}"

# Error logging messages
UNEXPECTED_ERROR = "Unexpected error occurred: {error}"
VALIDATION_ERROR = "Validation error: {field} - {error}"
SERIALIZATION_ERROR = "Serialization error: {serializer} - {error}"

# System logging messages
APPLICATION_STARTUP = "Billdr application starting up"
APPLICATION_SHUTDOWN = "Billdr application shutting down"
MIGRATION_STARTED = "Database migration started"
MIGRATION_COMPLETED = "Database migration completed"
MIGRATION_FAILED = "Database migration failed: {error}"