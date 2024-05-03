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

    cache_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.cache_data:
            self.cache_data = {
                "tot_pos": 0,
                "tot_completed_pos": 0,
                "tot_on_time_deliveries": 0,
                "tot_acknowledged_pos": 0,
            }

        return super().save(*args, **kwargs)
