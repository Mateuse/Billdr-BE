from rest_framework.views import APIView
from core.serializers.user import BusinessOwnerSerializer, CustomerSerializer
from core.utils.serializer import handle_serializer_save
from core.constants.api import (
    USER_CREATION_SUCCESS_MESSAGE,
    USER_CREATION_FAILED_MESSAGE,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    BUSINESS_OWNER_RETRIEVAL_SUCCESS_MESSAGE,
    BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
    BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    REQUEST_CONTEXT_KEY,
    CUSTOMER_RETRIEVAL_SUCCESS_MESSAGE,
    CUSTOMER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
    CUSTOMER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    BUSINESS_OWNER_DELETION_SUCCESS_MESSAGE,
    BUSINESS_OWNER_DELETION_FAILED_MESSAGE,
    CUSTOMER_DELETION_SUCCESS_MESSAGE,
    CUSTOMER_DELETION_FAILED_MESSAGE,
)
from core.constants.logging import (
    API_REQUEST_RECEIVED,
    API_REQUEST_COMPLETED,
    USER_RETRIEVED,
    USER_RETRIEVAL_FAILED,
    USER_CREATION_FAILED as LOG_USER_CREATION_FAILED
)
from core.models.user import BusinessOwner, Customer
from core.utils.custom_response import custom_response
from core.services.logger_service import db_logger, get_request_context
from core.models.logger import LogCategory


class BusinessOwnerView(APIView):
    def get(self, request, company_name=None):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        if company_name:
            try:
                business_owner = BusinessOwner.objects.get(id=company_name)
                serializer = BusinessOwnerSerializer(business_owner)

                db_logger.info(
                    category=LogCategory.USER,
                    message_template=USER_RETRIEVED,
                    context_data={
                        'user_type': 'BusinessOwner',
                        'user_id': str(business_owner.id)
                    },
                    **context
                )

                return custom_response(
                    HTTP_200_OK, BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE, serializer.data
                )
            except BusinessOwner.DoesNotExist:
                db_logger.warning(
                    category=LogCategory.USER,
                    message_template=USER_RETRIEVAL_FAILED,
                    context_data={
                        'user_type': 'BusinessOwner',
                        'user_id': company_name
                    },
                    **context
                )

                return custom_response(
                    HTTP_404_NOT_FOUND, BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE, None
                )
        else:
            business_owners = BusinessOwner.objects.all()
            serializer = BusinessOwnerSerializer(business_owners, many=True)

            db_logger.info(
                category=LogCategory.USER,
                message_template=USER_RETRIEVED,
                context_data={
                    'user_type': 'BusinessOwner',
                    'user_id': 'all',
                    'count': len(business_owners)
                },
                **context
            )

            return custom_response(
                HTTP_200_OK, BUSINESS_OWNER_RETRIEVAL_SUCCESS_MESSAGE, serializer.data
            )

    def post(self, request):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        serializer = BusinessOwnerSerializer(
            data=request.data, context={REQUEST_CONTEXT_KEY: request}
        )

        if not serializer.is_valid():
            db_logger.error(
                category=LogCategory.USER,
                message_template=LOG_USER_CREATION_FAILED,
                context_data={
                    'user_type': 'BusinessOwner',
                    'error': str(serializer.errors)
                },
                **context
            )

        return handle_serializer_save(
            serializer, USER_CREATION_SUCCESS_MESSAGE, USER_CREATION_FAILED_MESSAGE
        )

    def delete(self, request, company_name):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        try:
            business_owner = BusinessOwner.objects.get(id=company_name)
            business_owner.delete()

            db_logger.info(
                category=LogCategory.API,
                message_template=API_REQUEST_COMPLETED,
                context_data={
                    'method': request.method,
                    'endpoint': request.path,
                    'status_code': HTTP_200_OK
                },
                **context
            )

            return custom_response(
                HTTP_200_OK,
                BUSINESS_OWNER_DELETION_SUCCESS_MESSAGE,
                None,
            )
        except BusinessOwner.DoesNotExist:
            db_logger.warning(
                category=LogCategory.USER,
                message_template=USER_RETRIEVAL_FAILED,
                context_data={
                    'user_type': 'BusinessOwner',
                    'user_id': company_name
                },
                **context
            )

            return custom_response(
                HTTP_404_NOT_FOUND,
                BUSINESS_OWNER_DELETION_FAILED_MESSAGE,
                None,
            )


class CustomerView(APIView):
    def get(self, request, customer_id=None):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                serializer = CustomerSerializer(customer)

                db_logger.info(
                    category=LogCategory.USER,
                    message_template=USER_RETRIEVED,
                    context_data={
                        'user_type': 'Customer',
                        'user_id': str(customer.id)
                    },
                    **context
                )

                return custom_response(
                    HTTP_200_OK, CUSTOMER_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE, serializer.data
                )
            except Customer.DoesNotExist:
                db_logger.warning(
                    category=LogCategory.USER,
                    message_template=USER_RETRIEVAL_FAILED,
                    context_data={
                        'user_type': 'Customer',
                        'user_id': customer_id
                    },
                    **context
                )

                return custom_response(
                    HTTP_404_NOT_FOUND, CUSTOMER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE, None
                )
        else:
            customers = Customer.objects.all()
            serializer = CustomerSerializer(customers, many=True)

            db_logger.info(
                category=LogCategory.USER,
                message_template=USER_RETRIEVED,
                context_data={
                    'user_type': 'Customer',
                    'user_id': 'all',
                    'count': len(customers)
                },
                **context
            )

            return custom_response(
                HTTP_200_OK, CUSTOMER_RETRIEVAL_SUCCESS_MESSAGE, serializer.data
            )

    def post(self, request):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        serializer = CustomerSerializer(
            data=request.data, context={REQUEST_CONTEXT_KEY: request}
        )

        if not serializer.is_valid():
            db_logger.error(
                category=LogCategory.USER,
                message_template=LOG_USER_CREATION_FAILED,
                context_data={
                    'user_type': 'Customer',
                    'error': str(serializer.errors)
                },
                **context
            )

        return handle_serializer_save(
            serializer, USER_CREATION_SUCCESS_MESSAGE, USER_CREATION_FAILED_MESSAGE
        )

    def delete(self, request, customer_id):
        context = get_request_context(request)

        db_logger.info(
            category=LogCategory.API,
            message_template=API_REQUEST_RECEIVED,
            context_data={
                'method': request.method,
                'endpoint': request.path,
                'ip_address': context['ip_address']
            },
            **context
        )

        try:
            customer = Customer.objects.get(id=customer_id)
            customer.delete()

            db_logger.info(
                category=LogCategory.API,
                message_template=API_REQUEST_COMPLETED,
                context_data={
                    'method': request.method,
                    'endpoint': request.path,
                    'status_code': HTTP_200_OK
                },
                **context
            )

            return custom_response(
                HTTP_200_OK,
                CUSTOMER_DELETION_SUCCESS_MESSAGE,
                None,
            )
        except Customer.DoesNotExist:
            db_logger.warning(
                category=LogCategory.USER,
                message_template=USER_RETRIEVAL_FAILED,
                context_data={
                    'user_type': 'Customer',
                    'user_id': customer_id
                },
                **context
            )

            return custom_response(
                HTTP_404_NOT_FOUND,
                CUSTOMER_DELETION_FAILED_MESSAGE,
                None,
            )
