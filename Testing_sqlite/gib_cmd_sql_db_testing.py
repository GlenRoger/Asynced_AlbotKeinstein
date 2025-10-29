import sqlite3
import socket
import sys

class DatabaseController():

    def __init__(self):
        #Bruker hostname til å bestemme navnet på db
        self.hostname = socket.gethostname()
        self.db_path = f"./test_db/{self.hostname}_cmd.db"

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.tables_and_columns_dict = {}


    def create_table(self, table_name, columns_list):

        self.add_table_and_columns_to_dict_upper_case_only(table_name, columns_list)

        columns_and_types = ", ".join(columns_list)

        print(columns_and_types)

        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {columns_and_types}
            )
        ''')

    def add_table_and_columns_to_dict_upper_case_only(self, table_name, columns_list):

        upper_col_name_list = []

        for col in columns_list:
            upper_col_name_list.append(col.upper())


        self.tables_and_columns_dict[table_name.upper()] = upper_col_name_list



    def show_db_content(self):
        print("Showing tables in db:")
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = self.cursor.fetchall()
        print(result)

    def show_table(self, table_name, do_show = True):

        if do_show:
            print(f"Showing table column info for table '{table_name}':")

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()


        if do_show:
            print("Columns:")

        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else "NULL"
            primary_key = " [PRIMARY KEY]" if col[5] else ""

            if do_show:
                print(f"  - {col_name} ({col_type}) {not_null}{primary_key}")

        return columns

    def easy_select_from(self, table_name, select_command):
        print(f"select_from table column for table '{table_name}':")
        self.cursor.execute(f"{select_command} FROM {table_name}")
        result = self.cursor.fetchall()
        self.print_result(table_name, result)
#        print(result)


    def select_from(self, select_command):

        table_name = select_command.split(" ")[-1]

        print(f"select to run: {select_command}")
        self.cursor.execute(f"{select_command} ")
        result = self.cursor.fetchall()
        self.print_result(table_name, result)
#        print(result)
#        print(result)

    def insert_into(self, table_name, values_dict):

        values_list = ""
        values_to_send = []

        if table_name.upper() in self.tables_and_columns_dict.keys():
            print(f"Yes, the table {table_name} exists!")
            print(f"These are the columns: {self.tables_and_columns_dict[table_name.upper()]}")
            values_list = self.tables_and_columns_dict[table_name.upper()].copy()
        else:
            print(f"Couldn't copy - no such table registered: {table_name}")
            return

        #OBS! ID is not in this list for any tables! Må ha ekstra null for den:

        column_names = []

        for value in values_list:

            #Bruker default verdi, som tidstempel
            if 'DEFAULT' in value:
                continue

            value = value.split(" ")[0]

            column_names.append(value)

            if value.upper().startswith('HOSTNAME'):
                values_to_send.append(self.hostname)
            elif value.upper() in values_dict.keys():
                values_to_send.append(values_dict[value])
            else:
                values_to_send.append("NULL")

        insert_values = f"{values_to_send}"
        
        column_names_string = ", ".join(column_names)

        print(f"Trying to insert columns: {column_names_string}")
        print(f"Trying to insert value: {insert_values}")

        question_marks = "?" + (len(column_names) -1 )*", ?"

        insert_statement = f"INSERT INTO {table_name} ({column_names_string}) VALUES ({question_marks})"

        print(f"Final insert statment: {insert_statement}")

        self.cursor.execute(insert_statement, values_to_send)
#        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({question_marks_for_values})", insert_values)
        self.conn.commit()


    def print_result(self, table_name, result):

        cols = self.show_table(table_name, do_show = False)

        col_names = ""

        for col in cols:
            col_names += f"| {col[1]}"

        print(col_names)

        for row in result:
            for col_row in row:
                print(f"| {col_row} ", end='')
            print()

        print()


    #Implementeres senere ved behov
    def update_table(self, table_name, update_command):
        #self.conn.commit()
        pass

    def delete_from(self, table_name, delete_command):
        #self.conn.commit()
        pass

    def drop_table(self, table_name, pass_nr = 0):

        if pass_nr != 333:
            print("Couldn't delete table! Safety on!")
            return

        print(f"Dropping table '{table_name}':")
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()
        print("Table dropped!")

    def __delete__(self):
        self.ro_conn.close()


#Script starting
database_controller = DatabaseController()
database_controller.show_db_content()


#Error_register
if True:
#    database_controller.create_table("Commands_to_albot" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "hostname NVARCHAR(255)", "command NVARCHAR(255)", "parameters NVARCHAR(255)", "task_done NOT NULL CHECK (is_active IN (0, 1))"])
    database_controller.create_table("Commands_to_albot" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "hostname NVARCHAR(255)", "command NVARCHAR(255)", "parameters NVARCHAR(255)", "task_done INTEGER"])

    database_controller.show_table("Commands_to_albot")
    database_controller.easy_select_from("Commands_to_albot", "select count(*)")

    values_dict_1 = {"command": "Showgif", "task_done": 1}
    database_controller.insert_into("Commands_to_albot", values_dict_1)

    values_dict_2 = {"command": "Showgif again", "task_done": 1}
    database_controller.insert_into("Commands_to_albot", values_dict_2)

    values_dict_3 = {"command": "Repeat last gif", "task_done": 0}
    database_controller.insert_into("Commands_to_albot", values_dict_3)

    database_controller.drop_table("Commands_to_albot")

database_controller.select_from("select * from Commands_to_albot")

