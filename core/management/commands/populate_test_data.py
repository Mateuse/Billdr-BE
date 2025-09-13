from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from decimal import Decimal
from core.constants.db import (
    TEST_COMPANY_NAME_TECHCORP,
    TEST_COMPANY_NAME_DESIGN_STUDIO,
    TEST_COMPANY_NAME_CONSULTING,
    TEST_CUSTOMER_NAME_ALICE,
    TEST_CUSTOMER_EMAIL_ALICE,
    TEST_CUSTOMER_NAME_BOB,
    TEST_CUSTOMER_EMAIL_BOB,
    TEST_CUSTOMER_NAME_CAROL,
    TEST_CUSTOMER_EMAIL_CAROL,
    TEST_CUSTOMER_NAME_DAVID,
    TEST_CUSTOMER_EMAIL_DAVID,
    TEST_CUSTOMER_NAME_EMMA,
    TEST_CUSTOMER_EMAIL_EMMA,
    TEST_CUSTOMER_NAME_FRANK,
    TEST_CUSTOMER_EMAIL_FRANK,
    INVOICE_STATUS_SENT,
    POPULATE_TEST_DATA_HELP,
    POPULATE_CREATING_MESSAGE,
    POPULATE_SUCCESS_MESSAGE_TEMPLATE,
    OWNER_FIELD_NAME,
    CUSTOMER_FIELD_NAME,
    ISSUED_AT_FIELD_NAME,
    DUE_DATE_FIELD_NAME,
    TOTAL_AMOUNT_FIELD_NAME,
    STATUS_FIELD_NAME,
)


class Command(BaseCommand):
    help = POPULATE_TEST_DATA_HELP

    def handle(self, *args, **options):
        self.stdout.write(POPULATE_CREATING_MESSAGE)

        business_owners = [
            BusinessOwner.objects.create(company_name=TEST_COMPANY_NAME_TECHCORP),
            BusinessOwner.objects.create(company_name=TEST_COMPANY_NAME_DESIGN_STUDIO),
            BusinessOwner.objects.create(company_name=TEST_COMPANY_NAME_CONSULTING),
        ]

        customers = [
            Customer.objects.create(name=TEST_CUSTOMER_NAME_ALICE, email=TEST_CUSTOMER_EMAIL_ALICE),
            Customer.objects.create(name=TEST_CUSTOMER_NAME_BOB, email=TEST_CUSTOMER_EMAIL_BOB),
            Customer.objects.create(name=TEST_CUSTOMER_NAME_CAROL, email=TEST_CUSTOMER_EMAIL_CAROL),
            Customer.objects.create(name=TEST_CUSTOMER_NAME_DAVID, email=TEST_CUSTOMER_EMAIL_DAVID),
            Customer.objects.create(name=TEST_CUSTOMER_NAME_EMMA, email=TEST_CUSTOMER_EMAIL_EMMA),
            Customer.objects.create(name=TEST_CUSTOMER_NAME_FRANK, email=TEST_CUSTOMER_EMAIL_FRANK),
        ]

        now = timezone.now()
        invoices_data = [
            {
                OWNER_FIELD_NAME: business_owners[0],
                CUSTOMER_FIELD_NAME: customers[0],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=30),
                DUE_DATE_FIELD_NAME: now - timedelta(days=0),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("1500.00"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[0],
                CUSTOMER_FIELD_NAME: customers[1],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=15),
                DUE_DATE_FIELD_NAME: now + timedelta(days=15),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("2750.50"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[1],
                CUSTOMER_FIELD_NAME: customers[2],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=45),
                DUE_DATE_FIELD_NAME: now - timedelta(days=15),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("890.25"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[1],
                CUSTOMER_FIELD_NAME: customers[3],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=7),
                DUE_DATE_FIELD_NAME: now + timedelta(days=23),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("3200.00"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[2],
                CUSTOMER_FIELD_NAME: customers[4],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=60),
                DUE_DATE_FIELD_NAME: now - timedelta(days=30),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("575.75"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[2],
                CUSTOMER_FIELD_NAME: customers[5],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=2),
                DUE_DATE_FIELD_NAME: now + timedelta(days=28),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("4100.00"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[0],
                CUSTOMER_FIELD_NAME: customers[2],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=90),
                DUE_DATE_FIELD_NAME: now - timedelta(days=60),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("1250.00"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
            {
                OWNER_FIELD_NAME: business_owners[1],
                CUSTOMER_FIELD_NAME: customers[0],
                ISSUED_AT_FIELD_NAME: now - timedelta(days=5),
                DUE_DATE_FIELD_NAME: now + timedelta(days=25),
                TOTAL_AMOUNT_FIELD_NAME: Decimal("680.50"),
                STATUS_FIELD_NAME: INVOICE_STATUS_SENT
            },
        ]

        for invoice_data in invoices_data:
            Invoice.objects.create(**invoice_data)

        self.stdout.write(
            self.style.SUCCESS(
                POPULATE_SUCCESS_MESSAGE_TEMPLATE.format(
                    business_owners_count=len(business_owners),
                    customers_count=len(customers),
                    invoices_count=len(invoices_data)
                )
            )
        )