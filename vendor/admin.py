from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin

from .models.users import User
from .models.vendors import Vendor
from .models.purchaseorders import PurchaseOrder


@admin.register(User)
class UserAdmin(DjangoQLSearchMixin, BaseUserAdmin):
    list_display = (
        'email',
        'name',
        'is_admin'
    )
    list_display_links = list_display
    ordering = ('email',)
    filter_horizontal = (*BaseUserAdmin.filter_horizontal,)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "external_id",
                )
            },
        ),
        (
            "User info",
            {
                "fields": (
                    "name",
                    "is_admin",
                    "deleted",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        )
    )


@admin.register(Vendor)
class VendorAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass
