from datetime import datetime

from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from utils.mixins import PartialUpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import CharFilter, FilterSet

from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema


from vendor.models import Vendor, PurchaseOrder
from vendor.serializers import PurchaseOrderSerializer, CompletePurchaseOrderSerializer

from vendor.tasks.performance import calculate_avg_response_time, calculate_performance_metrics


class PurchaseOrderFilter(FilterSet):
    vendor_name = CharFilter(field_name="vendor__name", lookup_expr="icontains")
    vendor_code = CharFilter(field_name="vendor__vendor_code", lookup_expr="exact")


class PurchaseOrderViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    PartialUpdateModelMixin,
    GenericViewSet,
):
    queryset = PurchaseOrder.objects.all()
    filterset_class = PurchaseOrderFilter
    serializer_class = PurchaseOrderSerializer
    serializer_action_classes = {
        "complete": CompletePurchaseOrderSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "po_number"

    def perform_create(self, serializer):
        data = self.request.data
        serializer.save()
        vendor = Vendor.objects.get(vendor_code=data["vendor_id"])
        vendor.cache_data["tot_pos"] += 1
        vendor.save()

    @extend_schema(tags=["purchase_orders"], request=None, responses=PurchaseOrderSerializer)
    @action(detail=True, methods=["POST"])
    def acknowledge(self, request, *args, **kwargs):
        instance = self.queryset.get(po_number=kwargs["po_number"])
        if instance.acknowledgment_date:
            return Response(
                {"message": "PO has already been acknowledged."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.acknowledgment_date = datetime.now()
        instance.save()
        calculate_avg_response_time.delay(kwargs["po_number"])
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(tags=["purchase_orders"], request=CompletePurchaseOrderSerializer, responses=CompletePurchaseOrderSerializer)
    @action(detail=True, methods=["POST"])
    def complete(self, request, *args, **kwargs):
        instance = self.queryset.get(po_number=kwargs["po_number"])
        if instance.status == "completed":
            return Response(
                {"message": "PO has already been completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CompletePurchaseOrderSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        calculate_performance_metrics.delay(kwargs["po_number"])
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(tags=["purchase_orders"], request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @action(detail=True, methods=["POST"])
    def cancel(self, request, *args, **kwargs):
        instance = self.queryset.get(po_number=kwargs["po_number"])
        if instance.status == "cancelled":
            return Response(
                {"message": "PO has already been cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = "cancelled"
        instance.save()
        calculate_performance_metrics.delay(kwargs["po_number"])
        return Response(status=status.HTTP_204_NO_CONTENT)
