from uuid import uuid4
from django.db import models


class Vendor(models.Model):
    vendor_code = models.UUIDField(default=uuid4, unique=True, db_index=True)

    name = models.CharField(max_length=80, blank=True)
    contact_details = models.TextField(blank=True)
    address = models.TextField(blank=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    avg_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
