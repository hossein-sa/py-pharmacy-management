from getpass import getpass


def login(cursor, username, password):
    cursor.execute("SELECT id FROM patients WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    if result:
        print("Login successful!")
        return result[0]
    else:
        print("Invalid username or password.")
        return None


def patient_menu(db, cursor, patient_id):
    while True:
        print("\nPatient Menu")
        print("1. Add prescription")
        print("2. View confirmed prescriptions")
        print("3. Edit prescription")
        print("4. Delete prescription")
        print("5. Logout")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_prescription(db, cursor, patient_id)
        elif choice == "2":
            view_confirmed_prescriptions(cursor, patient_id)
        elif choice == "3":
            edit_prescription(db, cursor, patient_id)
        elif choice == "4":
            delete_prescription(db, cursor, patient_id)
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def add_prescription(db, cursor, patient_id):
    cursor.execute("INSERT INTO prescriptions (patient_id) VALUES (%s)", (patient_id,))
    prescription_id = cursor.lastrowid

    for i in range(10):
        item_name = input(f"Enter item {i + 1} name (or press Enter to finish): ")
        if not item_name:
            break
        cursor.execute("INSERT INTO prescription_items (prescription_id, item_name) VALUES (%s, %s)",
                       (prescription_id, item_name))

    db.commit()
    print("Prescription added successfully!")


def view_confirmed_prescriptions(cursor, patient_id):
    cursor.execute("""
        SELECT p.id, pi.item_name, pi.price
        FROM prescriptions p
        JOIN prescription_items pi ON p.id = pi.prescription_id
        WHERE p.patient_id = %s AND p.status = 'confirmed'
    """, (patient_id,))
    prescriptions = cursor.fetchall()

    if not prescriptions:
        print("No confirmed prescriptions found.")
        return

    current_prescription_id = None
    total_price = 0

    for prescription in prescriptions:
        if prescription[0] != current_prescription_id:
            if current_prescription_id is not None:
                print(f"Total price: ${total_price:.2f}\n")
            current_prescription_id = prescription[0]
            print(f"Prescription ID: {current_prescription_id}")
            total_price = 0

        print(f"Item: {prescription[1]}, Price: ${prescription[2]:.2f}")
        total_price += prescription[2]

    print(f"Total price: ${total_price:.2f}")


def edit_prescription(db, cursor, patient_id):
    prescription_id = int(input("Enter prescription ID to edit: "))
    cursor.execute("SELECT id FROM prescriptions WHERE id = %s AND patient_id = %s AND status = 'pending'",
                   (prescription_id, patient_id))
    if not cursor.fetchone():
        print("Prescription not found or cannot be edited.")
        return

    while True:
        print("\n1. Add item")
        print("2. Remove item")
        print("3. Finish editing")
        choice = input("Enter your choice: ")

        if choice == '1':
            item_name = input("Enter new item name: ")
            cursor.execute("INSERT INTO prescription_items (prescription_id, item_name) VALUES (%s, %s)",
                           (prescription_id, item_name))
        elif choice == '2':
            item_name = input("Enter item name to remove: ")
            cursor.execute("DELETE FROM prescription_items WHERE prescription_id = %s AND item_name = %s",
                           (prescription_id, item_name))
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

    db.commit()
    print("Prescription updated successfully!")


def delete_prescription(db, cursor, patient_id):
    prescription_id = int(input("Enter prescription ID to delete: "))
    cursor.execute("SELECT id FROM prescriptions WHERE id = %s AND patient_id = %s AND status = 'pending'",
                   (prescription_id, patient_id))
    if not cursor.fetchone():
        print("Prescription not found or cannot be deleted.")
        return

    cursor.execute("DELETE FROM prescription_items WHERE prescription_id = %s", (prescription_id,))
    cursor.execute("DELETE FROM prescriptions WHERE id = %s", (prescription_id,))
    db.commit()
    print("Prescription deleted successfully!")
