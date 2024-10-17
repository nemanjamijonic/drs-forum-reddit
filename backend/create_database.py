import sqlite3
from sqlite3 import Error

# connection = sqlite3.connect("forum3.db")

# connection.close()


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path,check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
