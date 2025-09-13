from core.constants.api import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    ALREADY_EXISTS_MESSAGE,
)
from core.utils.custom_response import custom_response


def handle_serializer_save(
    serializer, success_message, error_message, success_data=None
):
    if serializer.is_valid():
        try:
            serializer.save()
            return custom_response(
                HTTP_201_CREATED, success_message, success_data or serializer.data
            )
        except Exception as e:
            error_str = str(e).lower()
            if ALREADY_EXISTS_MESSAGE in error_str:
                return custom_response(HTTP_409_CONFLICT, str(e), {})
            return custom_response(HTTP_400_BAD_REQUEST, str(e), {})
    return custom_response(HTTP_400_BAD_REQUEST, error_message, serializer.errors)


def get_serializer_data(serializer_class, data, context=None):
    """
    Utility function to serialize data using a given serializer class.

    Args:
        serializer_class: The serializer class to use
        data: The data to serialize (can be instance, queryset, list, or None)
        context: Optional context to pass to the serializer

    Returns:
        Serialized data as dict, list, or None
    """
    if data is None:
        return None

    if hasattr(data, '_meta') and hasattr(data._meta, 'model'):
        # Single model instance
        serializer = serializer_class(data, context=context)
        return serializer.data
    elif hasattr(data, '__iter__') and not isinstance(data, (str, dict)):
        # Queryset or list
        if not data:  # Empty queryset or list
            return []
        serializer = serializer_class(data, many=True, context=context)
        return serializer.data
    else:
        # Try single instance
        serializer = serializer_class(data, context=context)
        return serializer.data
