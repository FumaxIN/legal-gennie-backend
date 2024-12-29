from rest_framework import serializers
from legal_gennie.models import User, LawyerMetadata


class VerifyLawyerSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=255, min_length=3)
    class Meta:
        model = User
        fields = (
            'registration_number',
        )


class LawyersListSerializer(serializers.ModelSerializer):
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


class LawyerSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='lawyer_meta.registration_number', read_only=True)
    lawyer_type = serializers.IntegerField(source='lawyer_meta.lawyer_type')
    consultation_fee = serializers.DecimalField(source='lawyer_meta.consultation_fee', max_digits=10, decimal_places=2)
    call_fee = serializers.DecimalField(source='lawyer_meta.call_fee', max_digits=10, decimal_places=2)

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'email',
            'registration_number',
            'lawyer_type',
            'consultation_fee',
            'call_fee',
        )
        read_only_fields = (
            'id',
            'name',
            'email',
            'registration_number',
        )

    def update(self, instance, validated_data):
        lawyer_meta_data = validated_data.pop('lawyer_meta', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lawyer_meta_data:
            lawyer_meta, created = LawyerMetadata.objects.get_or_create(user=instance)
            for attr, value in lawyer_meta_data.items():
                setattr(lawyer_meta, attr, value)
            lawyer_meta.save()

        return instance