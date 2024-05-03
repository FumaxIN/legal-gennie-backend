from datetime import datetime

from django.utils import timezone
from celery import shared_task

from vendor.models import PurchaseOrder, HistoricalPerformance


@shared_task
def calculate_avg_response_time(po_id):
    po = PurchaseOrder.objects.get(po_number=po_id)
    vendor = po.vendor
    tot_acknowledged_pos = vendor.cache_data["tot_acknowledged_pos"]
    po_response_time = po.acknowledgment_date - po.issue_date
    po_response_time_minutes = po_response_time.seconds / 60
    vendor.avg_response_time = (
                                       (vendor.avg_response_time * tot_acknowledged_pos) + po_response_time_minutes
                               ) / (tot_acknowledged_pos + 1)

    vendor.cache_data["tot_acknowledged_pos"] += 1

    vendor.save()

    HistoricalPerformance.objects.create(
        vendor=vendor,
        on_time_delivery_rate=vendor.on_time_delivery_rate,
        quality_rating_avg=vendor.quality_rating_avg,
        avg_response_time=vendor.avg_response_time,
        fulfillment_rate=vendor.fulfillment_rate,
    )


@shared_task
def calculate_performance_metrics(po_id):
    po = PurchaseOrder.objects.get(po_number=po_id)
    vendor = po.vendor
    tot_on_time_deliveries = vendor.cache_data["tot_on_time_deliveries"]
    tot_completed_pos = vendor.cache_data["tot_completed_pos"]
    if po.delivery_date > timezone.now() and po.status == "completed":
        tot_on_time_deliveries += 1

    if po.status == "completed":
        tot_completed_pos += 1

    vendor.on_time_delivery_rate = tot_on_time_deliveries / tot_completed_pos

    vendor.fulfillment_rate = tot_completed_pos / vendor.cache_data["tot_pos"]
    vendor.quality_rating_avg = (
                                          (vendor.quality_rating_avg * (tot_completed_pos-1)) + po.quality_rating
                                 ) / tot_completed_pos

    vendor.cache_data["tot_completed_pos"] = tot_completed_pos
    vendor.cache_data["tot_on_time_deliveries"] = tot_on_time_deliveries

    vendor.save()

    HistoricalPerformance.objects.create(
        vendor=vendor,
        on_time_delivery_rate=vendor.on_time_delivery_rate,
        quality_rating_avg=vendor.quality_rating_avg,
        avg_response_time=vendor.avg_response_time,
        fulfillment_rate=vendor.fulfillment_rate,
    )
