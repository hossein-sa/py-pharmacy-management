import curses
from utils import menu_loop, get_string_input


def login(cursor, username, password):
    cursor.execute("SELECT id FROM patients WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    return result[0] if result else None


def register(stdscr, db, cursor):
    while True:
        username = get_string_input(stdscr, "Enter desired username: ")
        password = get_string_input(stdscr, "Enter password: ")
        confirm_password = get_string_input(stdscr, "Confirm password: ")

        if password != confirm_password:
            stdscr.addstr("Passwords do not match. Try again.")
            stdscr.getch()
            continue

        cursor.execute("SELECT id FROM patients WHERE username = %s", (username,))
        if cursor.fetchone():
            stdscr.addstr("Username already exists. Please choose another.")
            stdscr.getch()
            continue

        cursor.execute("INSERT INTO patients (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        stdscr.addstr("Registration successful! You can now log in.")
        stdscr.getch()
        break


def patient_menu(stdscr, db, cursor, patient_id):
    while True:
        choice = menu_loop(stdscr, "Patient Menu", [
            "Add prescription",
            "View confirmed prescriptions",
            "Edit prescription",
            "Delete prescription",
            "View pending prescriptions",
            "Logout"
        ])

        if choice == 0:
            add_prescription(stdscr, db, cursor, patient_id)
        elif choice == 1:
            view_confirmed_prescriptions(stdscr, cursor, patient_id)
        elif choice == 2:
            edit_prescription(stdscr, db, cursor, patient_id)
        elif choice == 3:
            delete_prescription(stdscr, db, cursor, patient_id)
        elif choice == 4:
            view_pending_prescriptions(stdscr, cursor, patient_id)
        elif choice == 5:
            break


def add_prescription(stdscr, db, cursor, patient_id):
    cursor.execute("INSERT INTO prescriptions (patient_id) VALUES (%s)", (patient_id,))
    prescription_id = cursor.lastrowid

    for i in range(10):
        item_name = get_string_input(stdscr, f"Enter item {i + 1} name (or press Enter to finish): ")
        if not item_name:
            break
        cursor.execute("INSERT INTO prescription_items (prescription_id, item_name) VALUES (%s, %s)",
                       (prescription_id, item_name))

    db.commit()
    stdscr.addstr("Prescription added successfully!")
    stdscr.getch()


def view_confirmed_prescriptions(stdscr, cursor, patient_id):
    cursor.execute("""
        SELECT p.id, pi.item_name, pi.price
        FROM prescriptions p
        JOIN prescription_items pi ON p.id = pi.prescription_id
        WHERE p.patient_id = %s AND p.status = 'confirmed'
    """, (patient_id,))
    prescriptions = cursor.fetchall()

    if not prescriptions:
        stdscr.addstr("No confirmed prescriptions found.")
        stdscr.getch()
        return

    stdscr.clear()
    current_prescription_id = None
    total_price = 0
    row = 0

    for prescription in prescriptions:
        if prescription[0] != current_prescription_id:
            if current_prescription_id is not None:
                stdscr.addstr(row, 0, f"Total price: ${total_price:.2f}")
                row += 2
            current_prescription_id = prescription[0]
            stdscr.addstr(row, 0, f"Prescription ID: {current_prescription_id}")
            row += 1
            total_price = 0

        stdscr.addstr(row, 0, f"Item: {prescription[1]}, Price: ${prescription[2]:.2f}")
        row += 1
        total_price += prescription[2]

    stdscr.addstr(row, 0, f"Total price: ${total_price:.2f}")
    stdscr.getch()


def view_pending_prescriptions(stdscr, cursor, patient_id):
    cursor.execute("""
        SELECT p.id, pi.item_name
        FROM prescriptions p
        JOIN prescription_items pi ON p.id = pi.prescription_id
        WHERE p.patient_id = %s AND p.status = 'pending'
    """, (patient_id,))
    prescriptions = cursor.fetchall()

    if not prescriptions:
        stdscr.addstr("No pending prescriptions found.")
        stdscr.getch()
        return

    stdscr.clear()
    current_prescription_id = None
    row = 0

    for prescription in prescriptions:
        if prescription[0] != current_prescription_id:
            if current_prescription_id is not None:
                row += 1
            current_prescription_id = prescription[0]
            stdscr.addstr(row, 0, f"Prescription ID: {current_prescription_id}")
            row += 1

        stdscr.addstr(row, 0, f"Item: {prescription[1]}")
        row += 1

    stdscr.getch()


def edit_prescription(stdscr, db, cursor, patient_id):
    view_pending_prescriptions(stdscr, cursor, patient_id)
    prescription_id = int(get_string_input(stdscr, "Enter prescription ID to edit: "))

    cursor.execute("SELECT id FROM prescriptions WHERE id = %s AND patient_id = %s AND status = 'pending'",
                   (prescription_id, patient_id))
    if not cursor.fetchone():
        stdscr.addstr("Prescription not found or cannot be edited.")
        stdscr.getch()
        return

    while True:
        choice = menu_loop(stdscr, f"Editing Prescription {prescription_id}", [
            "Add item",
            "Remove item",
            "Finish editing"
        ])

        if choice == 0:
            item_name = get_string_input(stdscr, "Enter new item name: ")
            cursor.execute("INSERT INTO prescription_items (prescription_id, item_name) VALUES (%s, %s)",
                           (prescription_id, item_name))
        elif choice == 1:
            cursor.execute("SELECT id, item_name FROM prescription_items WHERE prescription_id = %s",
                           (prescription_id,))
            items = cursor.fetchall()
            if not items:
                stdscr.addstr("No items in this prescription.")
                stdscr.getch()
                continue

            item_choices = [f"{item[1]}" for item in items] + ["Cancel"]
            item_choice = menu_loop(stdscr, "Select item to remove", item_choices)

            if item_choice < len(items):
                cursor.execute("DELETE FROM prescription_items WHERE id = %s", (items[item_choice][0],))
        elif choice == 2:
            break

    db.commit()
    stdscr.addstr("Prescription updated successfully!")
    stdscr.getch()


def delete_prescription(stdscr, db, cursor, patient_id):
    view_pending_prescriptions(stdscr, cursor, patient_id)
    prescription_id = int(get_string_input(stdscr, "Enter prescription ID to delete: "))

    cursor.execute("SELECT id FROM prescriptions WHERE id = %s AND patient_id = %s AND status = 'pending'",
                   (prescription_id, patient_id))
    if not cursor.fetchone():
        stdscr.addstr("Prescription not found or cannot be deleted.")
        stdscr.getch()
        return

    confirm = get_string_input(stdscr, "Are you sure you want to delete this prescription? (y/n): ").lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM prescription_items WHERE prescription_id = %s", (prescription_id,))
        cursor.execute("DELETE FROM prescriptions WHERE id = %s", (prescription_id,))
        db.commit()
        stdscr.addstr("Prescription deleted successfully!")
    else:
        stdscr.addstr("Deletion cancelled.")
    stdscr.getch()