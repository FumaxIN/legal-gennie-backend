from rest_framework.test import APITestCase
from django.utils.timezone import now
from datetime import timedelta

from vendor.models import User, Vendor, PurchaseOrder


class PurchaseOrderTestCase(APITestCase):
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

        self.vendor_b = Vendor.objects.create(
            name="Test Vendor 2",
            address="Mumbai, India",
            contact_details="888888888"
        )

        self.purchase_order_data_a = {
            "items": {
                "item1": 2,
                "item2": 5
            },
            "delivery_date": now().date() + timedelta(days=1)
        }

        self.purchase_order_data_b = {
            "items": {
                "item1": 3,
                "item2": 4
            },
            "delivery_date": now().date() + timedelta(days=2)
        }

        self.purchase_order_data_c = {
            "vendor_id": self.vendor_a.vendor_code,
            "items": {
                "item1": 2,
                "item2": 1
            },
            "delivery_date": now().date() + timedelta(days=2)
        }

        self.po_a = PurchaseOrder.objects.create(
            vendor=self.vendor_a,
            **self.purchase_order_data_a
        )

        self.po_b = PurchaseOrder.objects.create(
            vendor=self.vendor_b,
            **self.purchase_order_data_b
        )

    def test_create_purchase_order_unauthenticated(self):
        response = self.client.post("/api/purchase_orders", self.purchase_order_data_c, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create_purchase_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/purchase_orders", self.purchase_order_data_c, format="json")
        self.assertEqual(response.status_code, 201)
        po_number = response.json()["po_number"]
        self.assertTrue(PurchaseOrder.objects.filter(po_number=po_number).exists())

    def test_list_purchase_orders(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/purchase_orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)

    def test_filter_purchase_orders_by_vendor_code(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/purchase_orders?vendor_code=" + str(self.vendor_a.vendor_code))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

    def test_filter_purchase_orders_by_vendor_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/purchase_orders?vendor_name=Vendor 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

    def test_update_purchase_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/purchase_orders/{self.po_a.po_number}",
            {"items": {"item1": 3, "item2": 5}},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quantity"], 8)
