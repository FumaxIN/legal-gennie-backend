from uuid import uuid4
from django.db import models
from django.utils.timezone import now

from .vendors import Vendor


class HistoricalPerformance(models.Model):
    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2)
    quality_rating_avg = models.DecimalField(max_digits=5, decimal_places=2)
    avg_response_time = models.DecimalField(max_digits=5, decimal_places=2)
    fulfillment_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"

    class Meta:
        db_table = "historical_performance"
        unique_together = ("vendor", "date")
        ordering = ["-date"]

