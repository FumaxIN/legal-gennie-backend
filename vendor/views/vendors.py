from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from utils.mixins import PartialUpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from vendor.models import Vendor
from vendor.serializers import VendorSerializer


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
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "vendor_code"
