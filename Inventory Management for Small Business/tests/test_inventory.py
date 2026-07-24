import json
import os
import tempfile
import unittest

import app as app_module
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

    def test_edit_product_route_accepts_post(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            products_path = os.path.join(tmpdir, "products.json")
            sales_path = os.path.join(tmpdir, "sales.json")
            with open(products_path, "w", encoding="utf-8") as handle:
                json.dump(
                    [
                        {
                            "id": "SKU-001",
                            "name": "Old Name",
                            "category": "Groceries",
                            "price": 1.0,
                            "stock_quantity": 1,
                            "reorder_level": 1,
                            "supplier_contact": "old@example.com",
                        }
                    ],
                    handle,
                )
            with open(sales_path, "w", encoding="utf-8") as handle:
                json.dump([], handle)

            original_products_path = app_module.PRODUCTS_PATH
            original_sales_path = app_module.SALES_PATH
            app_module.PRODUCTS_PATH = products_path
            app_module.SALES_PATH = sales_path
            self.addCleanup(setattr, app_module, "PRODUCTS_PATH", original_products_path)
            self.addCleanup(setattr, app_module, "SALES_PATH", original_sales_path)

            client = app_module.app.test_client()
            response = client.post(
                "/products/edit/SKU-001",
                data={
                    "name": "Updated Name",
                    "category": "Groceries",
                    "price": "2.5",
                    "stock_quantity": "7",
                    "reorder_level": "3",
                    "supplier_contact": "new@example.com",
                },
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            with open(products_path, "r", encoding="utf-8") as handle:
                products = json.load(handle)
            self.assertEqual(products[0]["name"], "Updated Name")
            self.assertEqual(products[0]["price"], 2.5)


if __name__ == "__main__":
    unittest.main()
