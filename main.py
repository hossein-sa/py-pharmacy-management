# main.py
import curses
import mysql.connector
import patient
import admin
import sys
from utils import menu_loop, get_string_input


def connect_to_database():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="toor",
            database="pharmacy_management"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        sys.exit(1)


def main(stdscr):
    db = connect_to_database()
    cursor = db.cursor()

    while True:
        choice = menu_loop(stdscr, "Pharmacy Management System", [
            "Login as Patient",
            "Login as Admin",
            "Register as Patient",
            "Exit"
        ])

        if choice == 0:  # Login as Patient
            username = get_string_input(stdscr, "Enter username: ")
            password = get_string_input(stdscr, "Enter password: ")
            patient_id = patient.login(cursor, username, password)
            if patient_id:
                patient.patient_menu(stdscr, db, cursor, patient_id)
        elif choice == 1:  # Login as Admin
            username = get_string_input(stdscr, "Enter username: ")
            password = get_string_input(stdscr, "Enter password: ")
            admin_id = admin.login(cursor, username, password)
            if admin_id:
                admin.admin_menu(stdscr, db, cursor)
        elif choice == 2:  # Register as Patient
            patient.register(stdscr, db, cursor)
        elif choice == 3:  # Exit
            break

    db.close()


if __name__ == "__main__":
    curses.wrapper(main)
