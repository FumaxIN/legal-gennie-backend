from datetime import timedelta
import time
import math
from django.utils.timezone import now
from rest_framework.test import APITestCase

from vendor.models import User, Vendor, PurchaseOrder
from vendor.tasks.performance import calculate_avg_response_time, calculate_performance_metrics


class POPerformanceTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User1",
            email="testuser1@example.com",
            password="testpass",
        )

        self.vendor_a = Vendor.objects.create(
            name="Test Vendor 1",
            address="Delhi, India",
            contact_details="999999999"
        )

        self.purchase_order_data_a = {
            "items": {
                "item1": 2,
                "item2": 5
            },
            "delivery_date": now() + timedelta(days=2)
        }

        self.purchase_order_data_b = {
            "items": {
                "item1": 3,
                "item2": 4
            },
            "delivery_date": now() + timedelta(seconds=4)
        }

        self.po_a = PurchaseOrder.objects.create(
            vendor=self.vendor_a,
            **self.purchase_order_data_a
        )

        self.po_b = PurchaseOrder.objects.create(
            vendor=self.vendor_a,
            **self.purchase_order_data_b
        )

        self.vendor_a.cache_data["tot_pos"] = 2
        self.vendor_a.save()

    def test_acknowledge_purchase_order_a(self):
        self.client.force_authenticate(user=self.user)
        time.sleep(2)

        response = self.client.post(f"/api/purchase_orders/{self.po_a.po_number}/acknowledge")
        self.assertEqual(response.status_code, 200)
        calculate_avg_response_time(self.po_a.po_number)
        response = self.client.post(f"/api/purchase_orders/{self.po_b.po_number}/acknowledge")
        self.assertEqual(response.status_code, 200)
        calculate_avg_response_time(self.po_b.po_number)

        self.po_a.refresh_from_db()
        self.po_b.refresh_from_db()
        self.vendor_a.refresh_from_db()
        self.assertIsNotNone(self.po_a.acknowledgment_date)
        self.assertIsNotNone(self.po_b.acknowledgment_date)
        self.assertIsNotNone(self.vendor_a.avg_response_time)
        tot_response_time = (self.po_a.acknowledgment_date - self.po_a.issue_date).seconds + \
                            (self.po_b.acknowledgment_date - self.po_b.issue_date).seconds
        avg = tot_response_time / (self.vendor_a.cache_data["tot_acknowledged_pos"])
        self.assertEqual(math.floor(self.vendor_a.avg_response_time), math.floor(avg))

    def test_complete_purchase_order_b(self):
        self.client.force_authenticate(user=self.user)

        # On Time
        response = self.client.post(f"/api/purchase_orders/{self.po_a.po_number}/acknowledge")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(f"/api/purchase_orders/{self.po_a.po_number}/complete", {
            "quality_rating": 7
        })
        self.assertEqual(response.status_code, 200)
        self.po_a.refresh_from_db()
        self.vendor_a.refresh_from_db()
        self.assertEqual(self.po_a.status, "completed")
        calculate_avg_response_time(self.po_a.po_number)

        # Delayed
        response = self.client.post(f"/api/purchase_orders/{self.po_b.po_number}/acknowledge")
        self.assertEqual(response.status_code, 200)
        time.sleep(5)
        response = self.client.post(f"/api/purchase_orders/{self.po_b.po_number}/complete", {
            "quality_rating": 8
        })
        self.assertEqual(response.status_code, 200)
        self.po_b.refresh_from_db()
        self.vendor_a.refresh_from_db()
        self.assertEqual(self.po_a.status, "completed")
        calculate_avg_response_time(self.po_b.po_number)

        self.po_a.refresh_from_db()
        self.po_b.refresh_from_db()

        calculate_performance_metrics(self.po_a.po_number)
        calculate_performance_metrics(self.po_b.po_number)
        self.vendor_a.refresh_from_db()

        self.assertEqual(self.vendor_a.on_time_delivery_rate, 0.5)
        self.assertEqual(self.vendor_a.fulfillment_rate, 1.0)
        self.assertEqual(self.vendor_a.quality_rating_avg, 7.5)
