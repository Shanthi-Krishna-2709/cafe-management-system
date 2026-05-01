import json

from django.test import TestCase
from django.urls import reverse

from .menu_catalog import MENU_CATALOG
from .models import Category, Menu, Order


class MenuCatalogSyncTests(TestCase):
    def test_menu_catalog_is_seeded_after_migrations(self):
        expected_category_count = len(MENU_CATALOG)
        expected_item_count = sum(len(section["items"]) for section in MENU_CATALOG)

        self.assertEqual(Category.objects.count(), expected_category_count)
        self.assertEqual(Menu.objects.count(), expected_item_count)
        self.assertTrue(Menu.objects.filter(name="Espresso", category__name="Hot Coffees").exists())


class ConfirmOrderTests(TestCase):
    def test_confirm_order_creates_order_and_clears_session_cart(self):
        session = self.client.session
        session["cart"] = {"1": 2}
        session["grand_total"] = 16800
        session.save()

        response = self.client.post(
            reverse("confirm_order"),
            {
                "payment_method": "upi",
                "customer_name": "Siva",
                "customer_phone": "9999999999",
                "customer_email": "siva@example.com",
                "items": json.dumps(
                    [
                        {
                            "name": "Espresso",
                            "qty": 2,
                            "unit_price": 80,
                        }
                    ]
                ),
            },
        )

        payload = response.json()
        order = Order.objects.get()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(order.customer_name, "Siva")
        self.assertEqual(order.payment_method, "upi")
        self.assertEqual(order.subtotal, 160)
        self.assertEqual(order.gst, 8)
        self.assertEqual(order.total_amount, 168)

        session = self.client.session
        self.assertEqual(session.get("cart"), {})
        self.assertEqual(session.get("grand_total"), 0)
