from rest_framework.test import APITestCase

from vendor.models import User, Vendor


class VendorTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User1",
            email="testuser1@example.com",
            password="testpass",
        )

        self.vendor_data_a = {
            "name": "Test Vendor 1",
            "address": "Delhi, India",
            "contact_details": "999999999"
        }

        self.vendor_data_b = {
            "name": "Test Vendor 2",
            "address": "Mumbai, India",
            "contact_details": "888888888"
        }

    def test_unauthenticated_user(self):
        response = self.client.get("/api/vendors")
        self.assertEqual(response.status_code, 401)

    def test_create_vendor(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/vendors", self.vendor_data_a, format="json")
        self.assertEqual(response.status_code, 201)
        vendor_code = response.json()["vendor_code"]
        self.assertTrue(Vendor.objects.filter(vendor_code=vendor_code).exists())

    def test_list_vendors(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/vendors")
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue("results" in json)

    def test_retrieve_vendor(self):
        self.client.force_authenticate(user=self.user)
        created_vendor = Vendor.objects.create(**self.vendor_data_b)
        response = self.client.get(f"/api/vendors/{created_vendor.vendor_code}")
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue("name" in json)

    def test_update_vendor(self):
        self.client.force_authenticate(user=self.user)
        created_vendor = Vendor.objects.create(**self.vendor_data_a)
        updated_data = {"contact_details": "777777777"}
        response = self.client.patch(
            f"/api/vendors/{created_vendor.vendor_code}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(json["contact_details"], updated_data["contact_details"])

    def test_delete_vendor(self):
        self.client.force_authenticate(user=self.user)
        created_vendor = Vendor.objects.create(**self.vendor_data_a)
        response = self.client.delete(f"/api/vendors/{created_vendor.vendor_code}")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Vendor.objects.filter(vendor_code=created_vendor.vendor_code).exists())
