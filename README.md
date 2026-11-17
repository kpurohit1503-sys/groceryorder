# Auto-Order Groceries System

A Python command-line grocery ordering application based on the supplied project brief. It stores orders in MySQL and writes a readable text copy of each order.

## Features
- Capture customer name, delivery address and delivery date
- Display a grocery menu and collect quantities
- Create, view, list, update and delete orders
- Calculate order totals
- Persist orders in MySQL
- Save/update a text-file copy in `orders/`

## Requirements
- Python 3.10+
- MySQL Server running locally
- A MySQL account with permission to create a database

## Setup (Windows PowerShell)

1. Open this project folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and enter your MySQL password:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Start MySQL Server.
6. Run the application:

   ```powershell
   python main.py
   ```

The application creates the `grocery_system` database and its tables automatically on first run.

## Project structure

- `main.py` — menu, user input, order display and text-file output
- `database.py` — MySQL connection and CRUD operations
- `schema.sql` — database table definitions
- `.env.example` — example database configuration
- `orders/` — generated text copies of orders

## Notes
- Prices and grocery items in `main.py` are sample values; change them to match your requirements.
- The original document describes automatic supplier restocking based on stock weight as a future improvement. This version implements customer order management; it does not connect to a supplier or automatically reorder inventory.
- Do not commit your real `.env` file or database password to GitHub.
