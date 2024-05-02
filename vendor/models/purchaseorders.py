from uuid import uuid4
from django.db import models

from .vendors import Vendor


class PurchaseOrder(models.Model):
    po_number = models.UUIDField(default=uuid4, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateField()
    delivery_date = models.DateField()  # expected delivery date
    items = models.JSONField()
    quantity = models.IntegerField()    # number of items in the PO
    status = models.CharField(max_length=20, default="pending")
    quality_rating = models.FloatField(default=0.0, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)    # date when the PO was issued to vendor
    acknowledgment_date = models.DateField(blank=True, null=True)    # date when the vendor acknowledged the PO

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.po_number}"

    def save(self, *args, **kwargs):
        self.status = self.status.lower()
        if self.status not in ["pending", "completed", "cancelled"]:
            raise ValueError("Invalid status.")

        if self.status == "completed" and not self.quality_rating:
            raise ValueError("Quality rating is required for completed POs.")

        if not self.quantity:
            self.quantity = 0
            for key, value in self.items.items():
                self.quantity += int(value)

        return super().save(*args, **kwargs)
