import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="SF@C1981MainCampus",  # change if needed
        database="attendance_db"
    )