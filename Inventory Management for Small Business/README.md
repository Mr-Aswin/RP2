# Inventory Management System for Small Business

A Flask-based inventory and sales management dashboard for retail stores and small warehouses. The app helps users manage products, reduce stock when sales are recorded, review low-stock alerts, and analyze sales revenue.

## Features
- Add and edit products with category, price, stock quantity, reorder level, and supplier contact
- Record sales and automatically reduce stock
- Highlight low-stock items below the reorder threshold
- Review sales history and daily/weekly revenue summaries
- Search and filter inventory by name and category
- Input validation and structured exception handling for robust workflows

## Project Structure
- app.py: Flask application and business logic
- templates/: HTML templates for the dashboard, inventory, sales, and reports
- static/: CSS and JavaScript for styling and small UI interactions
- data/: JSON files storing product and sale records

## Setup
1. Create a virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app
   ```bash
   python app.py
   ```
4. Open http://127.0.0.1:5000/

## Screenshots
- Dashboard overview with summary cards and low-stock alerts
- Inventory management view with search and filters
- Sales recording and reports pages
