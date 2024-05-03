from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from utils.mixins import PartialUpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from vendor.models import Vendor
from vendor.serializers import VendorSerializer, PerformanceSerializer


class VendorViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    PartialUpdateModelMixin,
    GenericViewSet,
):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    serializer_action_classes = {
        "performance": PerformanceSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "vendor_code"

    @extend_schema(tags=["vendors"], responses={200: PerformanceSerializer})
    @action(detail=True, methods=["get"])
    def performance(self, request, vendor_code=None):
        vendor = self.get_object()
        serializer = self.get_serializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)
