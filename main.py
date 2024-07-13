import mysql.connector
from getpass import getpass
from patient
import admin


def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="toor",
        database="pharmacy_management"
    )


def main():
    db = connect_to_database()
    cursor = db.cursor()

    while True:
        print("\nPharmacy Management System")
        print("1. Login as Patient")
        print("2. Login as Admin")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username:")
            password = getpass("Enter password:")
            patient_id = patient.login(cursor, username, password)
            if patient_id:
                patient.patient_menu(db, cursor, patient_id)
        elif choice == "2":
            username = input("Enter username:")
            password = getpass("Enter password:")
            admin_id = admin.login(cursor, username, password)
            if admin_id:
                admin.admin_menu(db, cursor)
        elif choice == "3":
            print("Thank you for using the pharmacy management system.")
            break

        else:
            print("Invalid choice. Please try again.")

    db.close()


if __name__ == "__main__":
    main()
