from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class PaymentRequirementRemovalTests(SimpleTestCase):
    def test_payment_required_page_is_no_longer_routed(self):
        with self.assertRaises(Resolver404):
            resolve("/staff/payment-required/")
