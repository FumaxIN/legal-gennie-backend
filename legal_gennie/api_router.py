from core import settings
from django.urls import path, include
from rest_framework_nested import routers

from legal_gennie.views.auth import APIRegistrationView, APILoginView
from legal_gennie.views.lawyers import VerifyLawyerViewSet, LawyersListViewSet, LawyerViewSet
from legal_gennie.views.case import CaseView

app_name = "legal_gennie"

router = routers.SimpleRouter(trailing_slash=False)
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)


auth_urls = [
    path("register", APIRegistrationView.as_view(), name="register"),
    path("login", APILoginView.as_view(), name="login"),
]

router.register(r"lawyers/verify", VerifyLawyerViewSet, basename="verify_lawyers")
router.register(r"lawyers", LawyersListViewSet, basename="lawyers")
router.register(r"lawyers", LawyerViewSet, basename="lawyer")

urlpatterns = [
    path("auth/", include(auth_urls)),
    path("cases", CaseView.as_view(), name="predict_outcome"),
    path("", include(router.urls)),
]
