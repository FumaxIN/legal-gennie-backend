from rest_framework import serializers
from vendor.models import User


class UserSerializer(serializers.ModelSerializer):
    meta = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'external_id',
            'email',
            'name',
            'meta',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('external_id', 'created_at', 'updated_at')

    def get_meta(self, obj):
        return {
            'is_admin': obj.is_admin,
            'is_staff': obj.is_staff,
            'is_superuser': obj.is_superuser
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)