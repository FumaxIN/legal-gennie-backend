from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from utils.mixins import PartialUpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from vendor.models import Vendor, PurchaseOrder

from vendor.serializers import VendorSerializer, PurchaseOrderSerializer


class PurchaseOrderViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    PartialUpdateModelMixin,
    GenericViewSet,
):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "po_number"
