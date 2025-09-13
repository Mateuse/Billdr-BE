from rest_framework import serializers
from core.models.user import BusinessOwner, Customer
from core.constants.api import USER_ALREADY_EXISTS_MESSAGE
from core.constants.db import (
    COMPANY_NAME_FIELD_NAME,
    ID_FIELD_NAME,
    NAME_FIELD_NAME,
    EMAIL_FIELD_NAME,
)


class BusinessOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessOwner
        fields = [ID_FIELD_NAME, COMPANY_NAME_FIELD_NAME]
        read_only_fields = [ID_FIELD_NAME]

    def create(self, validated_data):
        company_name = validated_data.get(COMPANY_NAME_FIELD_NAME)
        if BusinessOwner.objects.filter(company_name=company_name).exists():
            raise serializers.ValidationError(USER_ALREADY_EXISTS_MESSAGE)
        return super().create(validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [ID_FIELD_NAME, NAME_FIELD_NAME, EMAIL_FIELD_NAME]
        read_only_fields = [ID_FIELD_NAME]

    def create(self, validated_data):
        name = validated_data.get(NAME_FIELD_NAME)
        email = validated_data.get(EMAIL_FIELD_NAME)
        if Customer.objects.filter(name=name, email=email).exists():
            raise serializers.ValidationError(USER_ALREADY_EXISTS_MESSAGE)
        return super().create(validated_data)
