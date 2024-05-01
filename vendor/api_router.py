from core import settings
from django.urls import path, include
from rest_framework_nested import routers

from vendor.views.auth import APIRegistrationView, APILoginView
from vendor.views.vendors import VendorViewSet

app_name = "vendor"

router = routers.SimpleRouter(trailing_slash=False)
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)


router.register(r"vendors", VendorViewSet)


auth_urls = [
    path("register", APIRegistrationView.as_view(), name="register"),
    path("login", APILoginView.as_view(), name="login"),
]

urlpatterns = [
    path("auth/", include(auth_urls)),
    path("", include(router.urls)),
]
