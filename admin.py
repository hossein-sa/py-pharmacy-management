import curses
from utils import menu_loop, get_string_input, show_message


def login(cursor, username, password):
    cursor.execute("SELECT id FROM admins WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    return result[0] if result else None


def admin_menu(stdscr, db, cursor):
    while True:
        choice = menu_loop(stdscr, "Admin Menu", [
            "View all prescriptions",
            "Confirm prescription",
            "View prescription statistics",
            "Advanced analytics",
            "Logout"
        ])

        if choice == 0:
            view_all_prescriptions(stdscr, cursor)
        elif choice == 1:
            confirm_prescription(stdscr, db, cursor)
        elif choice == 2:
            view_prescription_statistics(stdscr, cursor)
        elif choice == 3:
            advanced_analytics(stdscr, cursor)
        elif choice == 4:
            break


def view_all_prescriptions(stdscr, cursor):
    cursor.execute("""
        SELECT p.id, p.patient_id, p.status, pi.item_name, pi.does_exist, pi.price
        FROM prescriptions p
        JOIN prescription_items pi ON p.id = pi.prescription_id
        ORDER BY p.id, pi.id
    """)
    prescriptions = cursor.fetchall()

    if not prescriptions:
        show_message(stdscr, "No prescriptions found.")
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
            stdscr.addstr(row, 0, f"Patient ID: {prescription[1]}")
            row += 1
            stdscr.addstr(row, 0, f"Status: {prescription[2]}")
            row += 1

        stdscr.addstr(row, 0, f"Item: {prescription[3]}, Exists: {prescription[4]}, Price: ${prescription[5]:.2f}")
        row += 1

    stdscr.getch()


def confirm_prescription(stdscr, db, cursor):
    prescription_id = int(get_string_input(stdscr, "Enter prescription ID to confirm: "))
    cursor.execute("SELECT id FROM prescriptions WHERE id = %s AND status = 'pending'", (prescription_id,))
    if not cursor.fetchone():
        show_message(stdscr, "Prescription not found or already confirmed.")
        return

    cursor.execute("SELECT id, item_name FROM prescription_items WHERE prescription_id = %s", (prescription_id,))
    items = cursor.fetchall()

    for item_id, item_name in items:
        does_exist = get_string_input(stdscr, f"Does '{item_name}' exist? (y/n): ").lower() == 'y'
        if does_exist:
            price = float(get_string_input(stdscr, f"Enter price for '{item_name}': "))
            cursor.execute("UPDATE prescription_items SET does_exist = TRUE, price = %s WHERE id = %s",
                           (price, item_id))
        else:
            cursor.execute("UPDATE prescription_items SET does_exist = FALSE WHERE id = %s", (item_id,))

    cursor.execute("UPDATE prescriptions SET status = 'confirmed' WHERE id = %s", (prescription_id,))
    db.commit()
    show_message(stdscr, "Prescription confirmed successfully!")


def view_prescription_statistics(stdscr, cursor):
    cursor.execute("""
        SELECT 
            COUNT(*) as total_prescriptions,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_prescriptions,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_prescriptions,
            AVG((SELECT SUM(price) FROM prescription_items WHERE prescription_id = prescriptions.id)) as average_prescription_value
        FROM prescriptions
    """)
    result = cursor.fetchone()

    stdscr.clear()
    stdscr.addstr(0, 0, "Prescription Statistics:")
    stdscr.addstr(2, 0, f"Total prescriptions: {result[0]}")
    stdscr.addstr(3, 0, f"Pending prescriptions: {result[1]}")
    stdscr.addstr(4, 0, f"Confirmed prescriptions: {result[2]}")
    stdscr.addstr(5, 0, f"Average prescription value: ${result[3]:.2f}")
    stdscr.getch()


def advanced_analytics(stdscr, cursor):
    while True:
        choice = menu_loop(stdscr, "Advanced Analytics", [
            "Top 5 most prescribed items",
            "Monthly prescription trends",
            "Patient prescription frequency",
            "Average processing time",
            "Prescription value distribution",
            "Back to Admin Menu"
        ])

        if choice == 0:
            top_prescribed_items(stdscr, cursor)
        elif choice == 1:
            monthly_prescription_trends(stdscr, cursor)
        elif choice == 2:
            patient_prescription_frequency(stdscr, cursor)
        elif choice == 3:
            average_processing_time(stdscr, cursor)
        elif choice == 4:
            prescription_value_distribution(stdscr, cursor)
        elif choice == 5:
            break


def top_prescribed_items(stdscr, cursor):
    cursor.execute("""
        SELECT item_name, COUNT(*) as count
        FROM prescription_items
        GROUP BY item_name
        ORDER BY count DESC
        LIMIT 5
    """)
    items = cursor.fetchall()

    stdscr.clear()
    stdscr.addstr(0, 0, "Top 5 Most Prescribed Items:")
    for i, (item, count) in enumerate(items, 1):
        stdscr.addstr(i + 1, 0, f"{i}. {item}: {count}")
    stdscr.getch()


def monthly_prescription_trends(stdscr, cursor):
    cursor.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as count
        FROM prescriptions
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)
    trends = cursor.fetchall()

    draw_bar_chart(stdscr, trends, "Monthly Prescription Trends")


def patient_prescription_frequency(stdscr, cursor):
    cursor.execute("""
        SELECT p.patient_id, COUNT(*) as prescription_count
        FROM prescriptions p
        GROUP BY p.patient_id
        ORDER BY prescription_count DESC
        LIMIT 10
    """)
    frequencies = cursor.fetchall()

    stdscr.clear()
    stdscr.addstr(0, 0, "Top 10 Patients by Prescription Frequency:")
    for i, (patient_id, count) in enumerate(frequencies, 1):
        stdscr.addstr(i + 1, 0, f"Patient ID {patient_id}: {count} prescriptions")
    stdscr.getch()


def average_processing_time(stdscr, cursor):
    cursor.execute("""
        SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, 
            (SELECT MAX(created_at) FROM prescriptions p2 WHERE p2.id = p1.id AND p2.status = 'confirmed')))
        AS avg_processing_time
        FROM prescriptions p1
        WHERE status = 'confirmed'
    """)
    result = cursor.fetchone()

    stdscr.clear()
    if result[0] is not None:
        avg_time = result[0]
        days = int(avg_time // 24)
        hours = int(avg_time % 24)
        stdscr.addstr(0, 0, f"Average Processing Time: {days} days and {hours} hours")
    else:
        stdscr.addstr(0, 0, "No data available for average processing time")
    stdscr.getch()


# Add this function to generate a simple ASCII chart
def draw_bar_chart(stdscr, data, title, max_width=50):
    stdscr.clear()
    stdscr.addstr(0, 0, title)
    max_value = max(count for _, count in data)
    for i, (label, count) in enumerate(data, 2):
        bar_length = int((count / max_value) * max_width)
        stdscr.addstr(i, 0, f"{label}: {'#' * bar_length} ({count})")
    stdscr.getch()


# Update the monthly_prescription_trends function to use the bar chart
def monthly_prescription_trends(stdscr, cursor):
    cursor.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as count
        FROM prescriptions
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)
    trends = cursor.fetchall()

    draw_bar_chart(stdscr, trends, "Monthly Prescription Trends")


# Add a new function for prescription value distribution
def prescription_value_distribution(stdscr, cursor):
    cursor.execute("""
        SELECT 
            CASE 
                WHEN total_price < 50 THEN '0-50'
                WHEN total_price BETWEEN 50 AND 100 THEN '50-100'
                WHEN total_price BETWEEN 100 AND 200 THEN '100-200'
                WHEN total_price BETWEEN 200 AND 500 THEN '200-500'
                ELSE '500+'
            END AS price_range,
            COUNT(*) as count
        FROM (
            SELECT p.id, SUM(pi.price) as total_price
            FROM prescriptions p
            JOIN prescription_items pi ON p.id = pi.prescription_id
            WHERE p.status = 'confirmed'
            GROUP BY p.id
        ) AS prescription_totals
        GROUP BY price_range
        ORDER BY 
            CASE price_range
                WHEN '0-50' THEN 1
                WHEN '50-100' THEN 2
                WHEN '100-200' THEN 3
                WHEN '200-500' THEN 4
                ELSE 5
            END
    """)
    distribution = cursor.fetchall()

    draw_bar_chart(stdscr, distribution, "Prescription Value Distribution")


# Update the advanced_analytics function to include the new feature
def advanced_analytics(stdscr, cursor):
    while True:
        choice = menu_loop(stdscr, "Advanced Analytics", [
            "Top 5 most prescribed items",
            "Monthly prescription trends",
            "Patient prescription frequency",
            "Average processing time",
            "Prescription value distribution",
            "Back to Admin Menu"
        ])

        if choice == 0:
            top_prescribed_items(stdscr, cursor)
        elif choice == 1:
            monthly_prescription_trends(stdscr, cursor)
        elif choice == 2:
            patient_prescription_frequency(stdscr, cursor)
        elif choice == 3:
            average_processing_time(stdscr, cursor)
        elif choice == 4:
            prescription_value_distribution(stdscr, cursor)
        elif choice == 5:
            break
