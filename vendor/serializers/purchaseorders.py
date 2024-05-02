from rest_framework import serializers
from django.shortcuts import get_object_or_404

from vendor.models import Vendor
from vendor.models import PurchaseOrder

from .vendors import VendorSerializer


class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_id = serializers.UUIDField(write_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
            'po_number',
            'vendor',
            'vendor_id',
            'items',
            'quantity',
            'order_date',
            'delivery_date',
            'status',
            'quality_rating',
            'issue_date',
            'acknowledgment_date',
        )
        read_only_fields = ('po_number', 'vendor', 'quantity')

    def create(self, validated_data):
        vendor_id = validated_data.pop('vendor_id')
        vendor = get_object_or_404(Vendor, vendor_code=vendor_id)
        return PurchaseOrder.objects.create(vendor=vendor, **validated_data)

