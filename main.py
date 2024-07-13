import mysql.connector
from getpass import getpass
import patient
import admin
import sys


def connect_to_database():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="toor",
            database="pharmacy_management"
        )
    except mysql.connector.Error as error:
        print("Error connecting to MySQL database:", error)
        sys.exit(1)


def get_valid_choice(min_value, max_value):
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if min_value <= choice <= max_value:
                return choice
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    db = connect_to_database()
    cursor = db.cursor()

    while True:
        print("\nPharmacy Management System")
        print("1. Login as Patient")
        print("2. Login as Admin")
        print("3. Register as Patient")
        print("4. Exit")
        choice = get_valid_choice(1, 4)

        if choice == 1:
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            patient_id = patient.login(cursor, username, password)
            if patient_id:
                patient.patient_menu(db, cursor, patient_id)
        elif choice == 2:
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            admin_id = admin.login(cursor, username, password)
            if admin_id:
                admin.admin_menu(db, cursor)
        elif choice == 3:
            patient.register(db, cursor)
        elif choice == 4:
            print("Thank you for using the Pharmacy Management System.")
            break

    db.close()


if __name__ == "__main__":
    main()
