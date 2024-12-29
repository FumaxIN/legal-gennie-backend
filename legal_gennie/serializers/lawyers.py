from rest_framework import serializers
from legal_gennie.models import User


class VerifyLawyerSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=255, min_length=3)
    class Meta:
        model = User
        fields = (
            'registration_number',
        )
