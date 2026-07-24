import json
import os
from datetime import datetime, date

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "inventory-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")
SALES_PATH = os.path.join(DATA_DIR, "sales.json")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def save_json(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError as exc:
        raise RuntimeError(f"Unable to save data: {exc}") from exc


def load_products():
    return load_json(PRODUCTS_PATH, [])


def load_sales():
    return load_json(SALES_PATH, [])


def save_products(products):
    save_json(PRODUCTS_PATH, products)


def save_sales(sales):
    save_json(SALES_PATH, sales)


def validate_product_data(data):
    errors = []

    name = str(data.get("name", "")).strip()
    if not name:
        errors.append("Product name is required")

    category = str(data.get("category", "")).strip()
    if not category:
        errors.append("Category is required")

    try:
        price = float(data.get("price", 0))
    except (TypeError, ValueError):
        errors.append("Price must be a valid number")
    else:
        if price <= 0:
            errors.append("Price must be greater than 0")

    try:
        stock_quantity = int(data.get("stock_quantity", 0))
    except (TypeError, ValueError):
        errors.append("Stock quantity must be an integer")
    else:
        if stock_quantity < 0:
            errors.append("Stock quantity cannot be negative")

    try:
        reorder_level = float(data.get("reorder_level", 0))
    except (TypeError, ValueError):
        errors.append("Reorder level must be a non-negative number")
    else:
        if reorder_level < 0:
            errors.append("Reorder level must be a non-negative number")

    return errors


def generate_simple_id(products):
    existing_ids = {product.get("id", "") for product in products}
    index = 1
    while True:
        candidate = f"SKU-{index:03d}"
        if candidate not in existing_ids:
            return candidate
        index += 1


def update_stock_on_sale(products, product_id, quantity):
    try:
        requested_quantity = int(quantity)
    except (TypeError, ValueError):
        return False, "Quantity must be a valid integer"

    if requested_quantity <= 0:
        return False, "Quantity must be at least 1"

    for product in products:
        if product.get("id") == product_id:
            if product.get("stock_quantity", 0) < requested_quantity:
                return False, "not enough stock"

            product["stock_quantity"] -= requested_quantity
            return True, "Stock updated successfully"

    return False, "Product not found"


def calculate_revenue(product, quantity):
    return round(float(product.get("price", 0)) * int(quantity), 2)


def get_low_stock_products(products):
    low_stock = []
    for product in products:
        if product.get("stock_quantity", 0) <= product.get("reorder_level", 0):
            low_stock.append(product)
    return low_stock


def build_sales_summary(sales):
    total_revenue = 0.0
    for sale in sales:
        total_revenue += float(sale.get("revenue", 0))

    current_date = datetime.now().date()
    daily_count = 0
    weekly_count = 0
    for sale in sales:
        sale_date = datetime.fromisoformat(sale.get("sale_date", current_date.isoformat())).date()
        if sale_date == current_date:
            daily_count += 1
        if sale_date >= current_date.fromordinal(current_date.toordinal() - 6):
            weekly_count += 1

    return {
        "total_revenue": round(total_revenue, 2),
        "daily_sales": daily_count,
        "weekly_sales": weekly_count,
    }


@app.route("/")
def index():
    products = load_products()
    sales = load_sales()
    low_stock = get_low_stock_products(products)
    summary = build_sales_summary(sales)
    return render_template(
        "index.html",
        products=products,
        low_stock=low_stock,
        summary=summary,
        page_title="Dashboard",
    )


@app.route("/products", methods=["GET", "POST"])
def products():
    products_data = load_products()

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", ""),
            "category": request.form.get("category", ""),
            "price": request.form.get("price", ""),
            "stock_quantity": request.form.get("stock_quantity", ""),
            "reorder_level": request.form.get("reorder_level", ""),
            "supplier_contact": request.form.get("supplier_contact", ""),
        }

        errors = validate_product_data(form_data)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("products.html", products=products_data, page_title="Inventory", errors=errors)

        product_id = request.form.get("product_id", "").strip()
        if product_id:
            for product in products_data:
                if product.get("id") == product_id:
                    product.update(
                        {
                            "name": form_data["name"].strip(),
                            "category": form_data["category"].strip(),
                            "price": float(form_data["price"]),
                            "stock_quantity": int(form_data["stock_quantity"]),
                            "reorder_level": float(form_data["reorder_level"]),
                            "supplier_contact": form_data["supplier_contact"].strip() or "Not provided",
                        }
                    )
                    break
        else:
            new_product = {
                "id": generate_simple_id(products_data),
                "name": form_data["name"].strip(),
                "category": form_data["category"].strip(),
                "price": float(form_data["price"]),
                "stock_quantity": int(form_data["stock_quantity"]),
                "reorder_level": float(form_data["reorder_level"]),
                "supplier_contact": form_data["supplier_contact"].strip() or "Not provided",
            }
            products_data.append(new_product)

        try:
            save_products(products_data)
        except RuntimeError as exc:
            flash(str(exc), "error")
            return redirect(url_for("products"))

        flash("Product saved successfully", "success")
        return redirect(url_for("products"))

    query = request.args.get("query", "").strip().lower()
    category_filter = request.args.get("category", "").strip().lower()

    filtered_products = []
    for product in products_data:
        matches_query = not query or query in product.get("name", "").lower()
        matches_category = not category_filter or category_filter == product.get("category", "").lower()
        if matches_query and matches_category:
            filtered_products.append(product)

    return render_template("products.html", products=filtered_products, page_title="Inventory")


@app.route("/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    products_data = load_products()
    selected_product = None
    for product in products_data:
        if product.get("id") == product_id:
            selected_product = product
            break

    if selected_product is None:
        flash("Product not found", "error")
        return redirect(url_for("products"))

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", ""),
            "category": request.form.get("category", ""),
            "price": request.form.get("price", ""),
            "stock_quantity": request.form.get("stock_quantity", ""),
            "reorder_level": request.form.get("reorder_level", ""),
            "supplier_contact": request.form.get("supplier_contact", ""),
        }

        errors = validate_product_data(form_data)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "products.html",
                products=products_data,
                selected_product=selected_product,
                page_title="Edit Product",
                errors=errors,
            )

        selected_product.update(
            {
                "name": form_data["name"].strip(),
                "category": form_data["category"].strip(),
                "price": float(form_data["price"]),
                "stock_quantity": int(form_data["stock_quantity"]),
                "reorder_level": float(form_data["reorder_level"]),
                "supplier_contact": form_data["supplier_contact"].strip() or "Not provided",
            }
        )

        try:
            save_products(products_data)
        except RuntimeError as exc:
            flash(str(exc), "error")
            return redirect(url_for("products"))

        flash("Product updated successfully", "success")
        return redirect(url_for("products"))

    return render_template("products.html", products=products_data, selected_product=selected_product, page_title="Edit Product")


@app.route("/sales", methods=["GET", "POST"])
def sales():
    products_data = load_products()
    sales_data = load_sales()

    if request.method == "POST":
        product_id = request.form.get("product_id", "")
        quantity = request.form.get("quantity", "")
        updated, message = update_stock_on_sale(products_data, product_id, quantity)
        if not updated:
            flash(message, "error")
            return redirect(url_for("sales"))

        selected_product = None
        for product in products_data:
            if product.get("id") == product_id:
                selected_product = product
                break

        if selected_product is None:
            flash("Product not found", "error")
            return redirect(url_for("sales"))

        revenue = calculate_revenue(selected_product, quantity)
        sales_entry = {
            "id": len(sales_data) + 1,
            "product_id": product_id,
            "product_name": selected_product.get("name"),
            "quantity": int(quantity),
            "revenue": revenue,
            "sale_date": datetime.now().isoformat(),
        }
        sales_data.append(sales_entry)

        try:
            save_products(products_data)
            save_sales(sales_data)
        except RuntimeError as exc:
            flash(str(exc), "error")
            return redirect(url_for("sales"))

        flash(f"Sale recorded: {sales_entry['quantity']} unit(s) sold", "success")
        return redirect(url_for("sales"))

    return render_template("sales.html", products=products_data, sales=sales_data, page_title="Sales")


@app.route("/reports")
def reports():
    sales_data = load_sales()
    products_data = load_products()
    product_lookup = {product.get("id"): product for product in products_data}

    daily_revenue = {}
    weekly_revenue = {}

    for sale in sales_data:
        sale_date = datetime.fromisoformat(sale.get("sale_date", datetime.now().isoformat())).date()
        day_key = sale_date.strftime("%Y-%m-%d")
        week_key = f"Week {sale_date.isocalendar().week}"
        daily_revenue[day_key] = daily_revenue.get(day_key, 0.0) + float(sale.get("revenue", 0))
        weekly_revenue[week_key] = weekly_revenue.get(week_key, 0.0) + float(sale.get("revenue", 0))

    enriched_sales = []
    for sale in sales_data:
        sale_product = product_lookup.get(sale.get("product_id"), {})
        enriched_sales.append(
            {
                **sale,
                "product_name": sale_product.get("name", sale.get("product_name", "Unknown")),
            }
        )

    return render_template(
        "reports.html",
        sales=enriched_sales,
        daily_revenue=daily_revenue,
        weekly_revenue=weekly_revenue,
        page_title="Reports",
    )


if __name__ == "__main__":
    app.run(debug=True)
