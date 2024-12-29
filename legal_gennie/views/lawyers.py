from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.response import Response

from utils.mixins import PartialUpdateModelMixin
from utils.helpers import verify_lawyer_dl

from legal_gennie.models import User
from legal_gennie.serializers.lawyers import VerifyLawyerSerializer


class VerifyLawyerViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = VerifyLawyerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
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
        return Response(
            {"message": "Lawyer verified successfully"},
            status=status.HTTP_200_OK,
        )
