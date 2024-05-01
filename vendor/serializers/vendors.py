from rest_framework import serializers

from vendor.models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = (
            'vendor_code',
            'name',
            'address',
            'contact_details',
            'on_time_delivery_rate',
            'quality_rating_avg',
            'avg_response_time',
            'fulfillment_rate',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'vendor_code',
            'on_time_delivery_rate',
            'quality_rating_avg',
            'avg_response_time',
            'fulfillment_rate',
            'created_at',
            'updated_at'
        )

