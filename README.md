# Pharmacy Management System

## Overview
This Pharmacy Management System is a console-based application built with Python and MySQL. It provides separate interfaces for patients and administrators to manage prescriptions efficiently.

## Features
- **Patient Interface:**
  - Add prescriptions
  - View confirmed prescriptions
  - Edit pending prescriptions
  - Delete pending prescriptions
  - View pending prescriptions
- **Admin Interface:**
  - View all prescriptions
  - Confirm prescriptions
  - View prescription statistics
  - Advanced analytics (e.g., top prescribed items, monthly trends)

## Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/pharmacy-management-system.git
   cd pharmacy-management-system

2. Install required Python packages:
   ```sh
   pip install mysql-connector-python
   pip install windows-curses  # For Windows
   On Linux and macOS, curses is included in the standard library

3. Set up the MySQL database:
- Create a new database named `pharmacy_management`
- Run the SQL script provided in `database_setup.sql` to create the necessary tables

4. Configure the database connection:
- Open `main.py`
- Update the database connection details in the `connect_to_database()` function:
  ```python
  return mysql.connector.connect(
      host="localhost",
      user="your_username",
      password="your_password",
      database="pharmacy_management"
  )
  ```

## Usage
Run the application from the command line:
```sh
python main.py
```
Follow the on-screen prompts to navigate through the system.


### For Patients:
```
- Register a new account or log in with existing credentials
- Add new prescriptions
- View and manage your prescriptions
```
### For Admins:
```
- Log in with admin credentials
- View and confirm pending prescriptions
- Access analytics and statistics
```
## File Structure
- `main.py`: Main application entry point
- `patient.py`: Patient-related functionalities
- `admin.py`: Admin-related functionalities
- `utils.py`: Utility functions for the user interface
- `database_setup.sql`: SQL script for setting up the database

## Contributing
Contributions to improve the Pharmacy Management System are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` file for more information.

## Contact
Email : [Hossein Sadeghi](mailto:sadeghi.ho@hotmail.com)

Project Link: [Pharmacy Management](https://github.com/hossein-sa/py-pharmacy-management)
 
