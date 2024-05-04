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
        read_only_fields = (
            'po_number',
            'vendor',
            'quantity',
            'status',
            'order_date',
            'quality_rating',
            'issue_date',
            'acknowledgment_date'
        )

    def create(self, validated_data):
        vendor_id = validated_data.pop('vendor_id')
        vendor = get_object_or_404(Vendor, vendor_code=vendor_id)
        return PurchaseOrder.objects.create(vendor=vendor, **validated_data)

    def update(self, instance, validated_data):
        instance.items = validated_data.get('items', instance.items)
        instance.delivery_date = validated_data.get('delivery_date', instance.delivery_date)
        instance.quantity = 0
        for key, value in instance.items.items():
            instance.quantity += int(value)
        instance.save()
        return instance


class CompletePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = (
            'quality_rating',
        )

    def update(self, instance, validated_data):
        instance.status = 'completed'
        instance.quality_rating = validated_data.get('quality_rating')
        instance.save()
        return instance
