from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import FilterSet, OrderingFilter, CharFilter

from utils.mixins import PartialUpdateModelMixin
from utils.permissions import IsSelf
from utils.helpers import verify_lawyer_dl

from legal_gennie.models import LawyerMetadata, User
from legal_gennie.serializers.lawyers import VerifyLawyerSerializer, LawyerSerializer, LawyersListSerializer


class VerifyLawyerViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = VerifyLawyerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.is_verified:
            return Response(
                {"error": "User is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration_number = serializer.validated_data["registration_number"]
        print(registration_number)
        verified = verify_lawyer_dl(registration_number)
        print(verified)
        if not verified:
            print("Invalid registration number")
            return Response(
                {"error": "Invalid registration number"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        user.is_verified = True
        user.is_lawyer = True
        user.save()
        metadata = LawyerMetadata.objects.create(user=user, registration_number=registration_number)
        metadata.save()
        return Response(
            {"message": "Lawyer verified successfully"},
            status=status.HTTP_200_OK,
        )



class LawyerFilter(FilterSet):
    name = CharFilter(field_name="user__name", lookup_expr="icontains")
    lawyer_type = CharFilter(lookup_expr="icontains")

    order_by = OrderingFilter(
        fields=(
            ("consultation_fee", "consultation_fee"),
            ("call_fee", "call_fee"),
        )
    )


class LawyersListViewSet(GenericViewSet, ListModelMixin):
    queryset = LawyerMetadata.objects.filter(deleted=False)
    serializer_class = LawyersListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = LawyerFilter


class LawyerViewSet(GenericViewSet, RetrieveModelMixin, DestroyModelMixin, PartialUpdateModelMixin):
    queryset = User.objects.filter(deleted=False, is_lawyer=True)
    serializer_class = LawyerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    lookup_field = "external_id"
    lookup_url_kwarg = "external_id"

