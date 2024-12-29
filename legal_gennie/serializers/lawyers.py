from rest_framework import serializers
from legal_gennie.models import User, LawyerMetadata


class VerifyLawyerSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=255, min_length=3)
    class Meta:
        model = User
        fields = (
            'registration_number',
        )


class LawyersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = LawyerMetadata
        fields = (
            'id',
            'name',
            'lawyer_type',
            'consultation_fee',
            'call_fee',
        )
        read_only_fields = (
            'id',
            'name',
            'lawyer_type',
            'consultation_fee',
            'call_fee',
        )