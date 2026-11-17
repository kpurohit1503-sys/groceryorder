from datetime import datetime
from database import get_connection, initialize_database, create_order, get_order, list_orders, update_order, delete_order

MENU = {
    1: ("Potatoes", 30.00, "kg"),
    2: ("Tomatoes", 40.00, "kg"),
    3: ("Onions", 35.00, "kg"),
    4: ("Milk", 28.00, "litre"),
    5: ("Bread", 40.00, "packet"),
    6: ("Eggs", 72.00, "dozen"),
    7: ("Rice", 60.00, "kg"),
    8: ("Apples", 120.00, "kg"),
}

def show_menu():
    print("\n========== GROCERY MENU ==========")
    print(f"{'No.':<5}{'Item':<18}{'Price':<12}{'Unit'}")
    for number, (name, price, unit) in MENU.items():
        print(f"{number:<5}{name:<18}Rs. {price:<8.2f}{unit}")
    print("==================================")

def collect_items():
    items = []
    while True:
        show_menu()
        choice = input("Enter item number (or 0 to finish): ").strip()
        if choice == "0":
            break
        if not choice.isdigit() or int(choice) not in MENU:
            print("Please choose a valid menu number.")
            continue
        number = int(choice)
        name, price, unit = MENU[number]
        try:
            quantity = float(input(f"Quantity in {unit}: "))
            if quantity <= 0:
                raise ValueError
        except ValueError:
            print("Quantity must be a number greater than zero.")
            continue
        items.append({
            "name": name, "unit_price": price,
            "quantity": quantity, "unit": unit
        })
        print(f"Added {quantity:g} {unit} of {name}.")
    return items

def create_new_order():
    customer = input("Customer name: ").strip()
    address = input("Delivery address: ").strip()
    delivery_date = input("Delivery date (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(delivery_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return
    if not customer or not address:
        print("Customer name and address are required.")
        return
    items = collect_items()
    if not items:
        print("No items selected. Order was not created.")
        return
    order_id = create_order(customer, address, delivery_date, items)
    order = get_order(order_id)
    save_order_text(order)
    print(f"\nOrder #{order_id} created. Total: Rs. {order['total']:.2f}")
    print(f"Order copy saved in orders/order_{order_id}.txt")

def save_order_text(order):
    Path("orders").mkdir(exist_ok=True)
    path = Path("orders") / f"order_{order['id']}.txt"
    lines = [
        f"GROCERY ORDER #{order['id']}",
        f"Customer: {order['customer_name']}",
        f"Address: {order['address']}",
        f"Delivery date: {order['delivery_date']}",
        "-" * 55,
        f"{'Item':<18}{'Qty':>9}{'Price':>12}{'Amount':>12}",
    ]
    for item in order["items"]:
        amount = item["quantity"] * item["unit_price"]
        lines.append(f"{item['item_name']:<18}{item['quantity']:>9g}{item['unit_price']:>12.2f}{amount:>12.2f}")
    lines.extend(["-" * 55, f"TOTAL: Rs. {order['total']:.2f}"])
    path.write_text("\n".join(lines), encoding="utf-8")

def display_order(order):
    if not order:
        print("Order not found.")
        return
    print(f"\nORDER #{order['id']} | {order['status']}")
    print(f"Customer: {order['customer_name']}")
    print(f"Address: {order['address']}")
    print(f"Delivery date: {order['delivery_date']}")
    print("-" * 58)
    print(f"{'Item':<18}{'Qty':>9}{'Unit price':>14}{'Amount':>14}")
    for item in order["items"]:
        amount = item["quantity"] * item["unit_price"]
        print(f"{item['item_name']:<18}{item['quantity']:>9g}{item['unit_price']:>14.2f}{amount:>14.2f}")
    print("-" * 58)
    print(f"TOTAL: Rs. {order['total']:.2f}")

def view_order():
    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Enter a valid numeric order ID.")
        return
    order = get_order(order_id)
    display_order(order)
    if order:
        save_order_text(order)

def show_all_orders():
    orders = list_orders()
    if not orders:
        print("There are no orders yet.")
        return
    print(f"\n{'ID':<7}{'Customer':<22}{'Delivery date':<17}{'Total':>12}{'Status':>12}")
    for order in orders:
        print(f"{order['id']:<7}{order['customer_name'][:20]:<22}{str(order['delivery_date']):<17}{order['total']:>12.2f}{order['status']:>12}")

def edit_order():
    try:
        order_id = int(input("Enter order ID to update: "))
    except ValueError:
        print("Enter a valid numeric order ID.")
        return
    existing = get_order(order_id)
    if not existing:
        print("Order not found.")
        return
    display_order(existing)
    print("\nEnter new details (press Enter to keep the current value).")
    customer = input(f"Customer [{existing['customer_name']}]: ").strip() or existing["customer_name"]
    address = input(f"Address [{existing['address']}]: ").strip() or existing["address"]
    date_text = input(f"Delivery date [{existing['delivery_date']}] (YYYY-MM-DD): ").strip()
    delivery_date = date_text or str(existing["delivery_date"])
    try:
        datetime.strptime(delivery_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date.")
        return
    replace = input("Replace the item list? (y/n): ").strip().lower()
    items = collect_items() if replace == "y" else None
    if items == []:
        print("No items selected. Update cancelled.")
        return
    update_order(order_id, customer, address, delivery_date, items)
    updated = get_order(order_id)
    save_order_text(updated)
    print("Order updated successfully.")

def remove_order():
    try:
        order_id = int(input("Enter order ID to delete: "))
    except ValueError:
        print("Enter a valid numeric order ID.")
        return
    confirm = input(f"Delete order #{order_id}? (y/n): ").strip().lower()
    if confirm == "y":
        if delete_order(order_id):
            Path("orders", f"order_{order_id}.txt").unlink(missing_ok=True)
            print("Order deleted.")
        else:
            print("Order not found.")

def main():
    print("Connecting to MySQL...")
    initialize_database()
    while True:
        print("""
========== AUTO-ORDER GROCERIES ==========
1. Create a new order
2. View an order
3. Show all orders
4. Update an order
5. Delete an order
6. Exit
==========================================
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            create_new_order()
        elif choice == "2":
            view_order()
        elif choice == "3":
            show_all_orders()
        elif choice == "4":
            edit_order()
        elif choice == "5":
            remove_order()
        elif choice == "6":
            print("Thank you for using Auto-Order Groceries.")
            break
        else:
            print("Invalid option. Choose 1-6.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped.")
    except Exception as error:
        print(f"\nAn error occurred: {error}")
        print("Check your MySQL settings in the .env file and ensure MySQL is running.")
