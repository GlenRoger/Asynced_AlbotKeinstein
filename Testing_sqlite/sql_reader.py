#DONE!
import sqlite3
import socket
import os

class Database_Reader():

    def __init__(self):

        #Bruker hostname til å bestemme navnet på db
        self.hostname = socket.gethostname()
        self.db_path = f"./test_db/{self.hostname}.db"

        #Denne skal ikke opprette databasen, så må sjekke fila finnes før den prøver 
        #å koble til. Koble til = lage db-fil hvis den ikke finnes.
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database {self.db_path} does not exist")

        # Read-only connection using URI - URI gjør at vi kan sende med parameter som "?mode=ro"
        #Dermed blir det read only
        self.ro_conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.cursor = self.ro_conn.cursor()


    def get_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()
        return columns

    def get_latest_error(self):

        print(f"Cursor: {cursor}")
        self.cursor.execute("SELECT * FROM Errors_register ORDER BY ID DESC LIMIT 1")
        result = self.cursor.fetchone()

        self.pretty_print("Errors_register", result)


    def get_latest_error_as_touple(self):
        self.cursor.execute("SELECT * FROM Errors_register ORDER BY ID DESC LIMIT 1")
        result = self.cursor.fetchone()

        return result

#        self.pretty_print("Errors_register", result)


    def pretty_print(self, table_name, result):
        print("In pretty_print:")
        cols = self.get_columns(table_name)

        col_list = []

        for col in cols:
            col_list.append(col[1])

        print(result.__class__)

        print_cols = ", ".join(col_list)
        print_result = result

        print(f"({print_cols})\n{print_result}")



if __name__ == "__main__":
    db_reader = Database_Reader()


    db_reader.get_latest_error()