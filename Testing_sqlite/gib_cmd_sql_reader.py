#DONE!
import sqlite3
import socket
import os

class Database_Reader():

    def __init__(self):

        #Bruker hostname til å bestemme navnet på db
        self.hostname = socket.gethostname()
        self.db_path = f"./test_db/{self.hostname}_cmd.db"

        #Denne skal ikke opprette databasen, så må sjekke fila finnes før den prøver 
        #å koble til. Koble til = lage db-fil hvis den ikke finnes.
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database {self.db_path} does not exist")


        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()


    def get_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()
        return columns

    def get_latest_error(self):
        self.cursor.execute("SELECT * FROM Commands_to_albot ORDER BY ID DESC LIMIT 1")
        result = self.cursor.fetchone()

        self.pretty_print("Commands_to_albot", result)
        # self.print_result("Commands_to_albot", result)

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


    def 


        # for res in result:
        #     print(res)

        

    # def show_table(self, table_name, do_show = True):

    #     if do_show:
    #         print(f"Showing table column info for table '{table_name}':")

    #     self.cursor.execute(f"PRAGMA table_info({table_name})")
    #     columns = self.cursor.fetchall()


    #     if do_show:
    #         print("Columns:")

    #     for col in columns:
    #         col_name = col[1]
    #         col_type = col[2]
    #         not_null = "NOT NULL" if col[3] else "NULL"
    #         primary_key = " [PRIMARY KEY]" if col[5] else ""

    #         if do_show:
    #             print(f"  - {col_name} ({col_type}) {not_null}{primary_key}")

    #     return columns


    # def print_result(self, table_name, result):

    #     cols = self.show_table(table_name, do_show = False)

    #     col_names = ""

    #     for col in cols:
    #         col_names += f"| {col[1]}"

    #     print(col_names)

    #     for row in result:
    #         for col_row in row:
    #             print(f"| {col_row} ", end='')
    #         print()

    #     print()



db_reader = Database_Reader()


db_reader.get_latest_error()