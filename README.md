# InventoryHub

A portfolio-ready inventory management system built with Django for handling products, suppliers, purchase orders, stock movements, reporting, and role-based access control.

This project was built to showcase more than basic CRUD screens. It focuses on practical business workflows such as controlled user onboarding, module-based permissions, stock adjustments, purchase order receiving, analytics, and CSV export.

## Project Overview

InventoryHub is a back-office web application for small to mid-sized businesses that need to:

- organize product, brand, category, and supplier data
- monitor inventory levels and reorder thresholds
- record stock-in and stock-out activity with audit-friendly movement logs
- manage purchase orders and receive incoming stock into inventory
- control access to each module based on user responsibility
- export operational data for reporting and review

## Why This Project Goes Beyond Basic CRUD

- Models a connected business workflow from product setup to supplier purchasing and stock receiving
- Uses approval-based onboarding instead of granting immediate access after registration
- Applies module-level permissions so administrators can control who can access Products, Suppliers, Purchase Orders, Inventory, Reports, and Users
- Links purchase order receiving directly to stock movement creation and inventory updates
- Adds analytics and filtered CSV export to support day-to-day operational reporting
- Presents the system through a polished Bootstrap interface so the project feels usable, not just functional

## Core Features

### User Management and Access Control

- Public user registration flow
- Admin approval required before a user can log in
- Module-level permission assignment
- User access review page for activating accounts and assigning permissions

### Product and Supplier Management

- Manage categories, brands, suppliers, and products
- Assign SKU, category, brand, supplier, and price to products
- Add categories and brands while creating products
- Store supplier contact details, lead times, and notes

### Inventory Operations

- Track current stock per product
- Set reorder levels
- Perform stock in and stock out actions
- Keep a movement history with reference and user details
- Highlight low-stock items

### Purchase Orders

- Create purchase orders for suppliers
- Manage multiple line items in a single order
- Track order status as Draft, Ordered, Received, or Cancelled
- Receive purchase orders directly into inventory
- Automatically create stock movement records during receiving

### Reporting and Export

- Dashboard snapshot for inventory activity
- Total products, categories, brands, and suppliers
- Current units in stock and total inventory value
- Low-stock and out-of-stock visibility
- Recent stock movements
- Category coverage and top stocked items
- CSV export for reports and filtered list views

## Technical Highlights

- Multi-app Django project structure across users, products, purchasing, inventory, and reporting
- Service-layer style business logic for workflows such as product creation and purchase order receiving
- Role-based access control using Django permissions
- Search, filtering, pagination, forms, and validation across operational modules
- Transaction-safe inventory updates for stock and receiving flows
- Reusable utilities for pagination, reporting, and CSV export
- Bootstrap-based interface organization with shared layouts and page-level styling

## Main Modules

### Authentication and User Access

- users register through the application
- accounts remain inactive until approved by an administrator
- admins assign module permissions from the Users module

### Products

- categories
- brands
- suppliers
- products

### Inventory

- stock levels
- reorder levels
- stock in and stock out
- movement history

### Purchase Orders

- supplier-linked purchase orders
- order item management
- receiving workflow into inventory

### Reports

- operational dashboard
- inventory summary
- movement insights
- CSV export

## Tech Stack

- Python
- Django 6
- SQLite
- Bootstrap 5
- HTML, CSS, JavaScript

## Project Structure

```text
inventory/
|-- core/              # shared helpers for reporting, pagination, export
|-- inventory/         # project settings and root URLs
|-- inventory_app/     # inventory and stock movement module
|-- products/          # products, suppliers, and purchase orders
|-- static/            # CSS and JavaScript assets
|-- templates/         # shared templates
|-- users/             # registration, approval, access control, dashboard, reports
|-- manage.py
|-- db.sqlite3
```

## Example Workflow

1. An admin or staff user sets up categories, brands, and suppliers.
2. Products are created with SKU, pricing, and supplier references.
3. Inventory levels are reviewed and reorder thresholds are maintained.
4. When stock needs replenishment, a purchase order is created for a supplier.
5. Once the order arrives, the purchase order is received.
6. Inventory quantities are updated automatically and stock movement records are created.
7. Admins and staff review the dashboard and export filtered data to CSV when needed.

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd inventory
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

This project currently uses Django as its main Python dependency.

```bash
pip install "Django>=6,<7"
```

### 4. Apply migrations

```bash
py manage.py migrate
```

If `py` is not available on your machine, use:

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
py manage.py createsuperuser
```

### 6. Run the development server

```bash
py manage.py runserver
```

Open the application:

- App: `http://127.0.0.1:8000/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## How to Use the System

### First-Time Admin Setup

1. Create a superuser.
2. Log in through Django Admin or the main app.
3. Create or approve user accounts.
4. Assign module permissions depending on the user role.

Available module permissions:

- Products
- Suppliers
- Purchase Orders
- Inventory
- Reports
- Users

### Suggested Demo Flow for Reviewers

If you are showcasing this project in a portfolio or interview, a good walkthrough is:

1. Register a new user account and show that it cannot log in until approved.
2. Log in as an admin and activate the user from the Users module.
3. Add a supplier, brand, category, and product.
4. Create a purchase order with one or more items.
5. Receive the purchase order and show the stock update.
6. Open Inventory and Stock Movements to verify the changes.
7. Visit Reports and export a filtered CSV file.

## Export Functionality

CSV export is available for:

- Products
- Suppliers
- Purchase Orders
- Inventory
- Stock Movements
- User Access
- Reports

List-page exports follow the active search and filter state so the downloaded file matches what the user is currently reviewing.

## Testing

Run framework checks:

```bash
py manage.py check
```

Run the test suite:

```bash
py manage.py test products inventory_app users
```

## Notes

- SQLite is used by default for local development and portfolio demos.
- The root URL redirects guests to the login page and authenticated users to the dashboard.
- Password reset UI exists, but email backend configuration is still needed for a full production-ready flow.
- Static assets are organized under `static/` with shared and page-level CSS.

## Possible Next Improvements

- Excel export support
- email notifications for account approval or purchase order events
- supplier performance scorecards
- product image support
- audit trail enhancements
- sales, issuance, or warehouse transfer module


