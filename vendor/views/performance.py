from rest_framework import permissions, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from vendor.models import HistoricalPerformance
from vendor.serializers import HistoricalPerformanceSerializer


class HistoricalPerformanceViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "external_id"
