import unittest

from app import calculate_revenue, update_stock_on_sale, validate_product_data


class InventoryTests(unittest.TestCase):
    def test_validate_product_data_rejects_invalid_values(self):
        errors = validate_product_data(
            {
                "name": "  ",
                "category": "Groceries",
                "price": "-1",
                "stock_quantity": "-4",
                "reorder_level": "abc",
            }
        )
        self.assertIn("Product name is required", errors)
        self.assertIn("Price must be greater than 0", errors)
        self.assertIn("Stock quantity cannot be negative", errors)
        self.assertIn("Reorder level must be a non-negative number", errors)

    def test_update_stock_on_sale_reduces_inventory(self):
        products = [{"id": "SKU-001", "stock_quantity": 10}]
        updated, message = update_stock_on_sale(products, "SKU-001", 3)
        self.assertTrue(updated)
        self.assertEqual(products[0]["stock_quantity"], 7)
        self.assertIn("Stock updated", message)

    def test_update_stock_on_sale_rejects_insufficient_stock(self):
        products = [{"id": "SKU-001", "stock_quantity": 2}]
        updated, message = update_stock_on_sale(products, "SKU-001", 3)
        self.assertFalse(updated)
        self.assertIn("not enough stock", message)

    def test_calculate_revenue_uses_quantity_and_price(self):
        product = {"price": 5.5, "stock_quantity": 10}
        self.assertAlmostEqual(calculate_revenue(product, 2), 11.0)


if __name__ == "__main__":
    unittest.main()
