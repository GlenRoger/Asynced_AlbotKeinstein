import sqlite3
import socket
import sys
import os

class DatabaseController():

    def __init__(self, test_run=False):
        #Bruker hostname til å bestemme navnet på db
        self.hostname = socket.gethostname()
        self.db_path = f"./databases/{self.hostname}.db"

        if test_run:
            self.db_path = f"../databases/{self.hostname}.db"



        if not os.path.exists(self.db_path):
            print("\n\nCouldn't fint the folder './databases' - please check it exists!")


        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.tables_and_columns_dict = {}

        self.create_error_register_table()
        self.create_info_register_table()
        self.create_tokens_register_table()
        self.create_dashboard_cmd_register_table()
        self.create_status_register_table()


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

            elif value.upper() in [k.upper() for k in values_dict.keys()]:
                # find the actual key
                actual_key = [k for k in values_dict.keys() if k.upper() == value.upper()][0]
                values_to_send.append(values_dict[actual_key])

            # elif value.upper() in values_dict.keys():
            #     values_to_send.append(values_dict[value])
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


    def create_error_register_table(self):
        #Columns
        #timestamp, hostname, error_message, component, error_type, severity, bot_version, function_name
        self.create_table("Errors_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "hostname NVARCHAR(255)", "error_message TEXT", "component  NVARCHAR(100)", "error_type NVARCHAR(50)", "severity NVARCHAR(20)", "bot_version NVARCHAR(20)", "function_name NVARCHAR(100)"])

    def create_tokens_register_table(self):
        #Columns:
        #timestamp, token_for, expiration_date, last_updated
        self.create_table("Tokens_register", ["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "token_for NVARCHAR(100)", "expiration_date datetime2", "last_updated datetime2"])

    def create_info_register_table(self):
        #Columns:
        #timestamp, action, invoked_by, function_name, parameters, bot_version
        self.create_table("Info_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "action NVARCHAR(255)", "invoked_by NVARCHAR(100)", "function_name NVARCHAR(100)", "parameters NVARCHAR(255)", "bot_version NVARCHAR(20)"])

    def create_dashboard_cmd_register_table(self):
        #Columns:
        #timestamp, invoked_by, action, parameters, bot_version
        self.create_table("Dashboard_cmd_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "invoked_by NVARCHAR(100)", "action NVARCHAR(255)", "parameters NVARCHAR(255)", "bot_version NVARCHAR(20)"])

    def create_status_register_table(self):
        #Columns:
        #name, value, last_updated - én rad per innstilling, f.eks. HALLOWEEN_MODE = ON
        self.create_table("Status_register", ["name NVARCHAR(100)", "value NVARCHAR(255)", "last_updated DATETIME DEFAULT CURRENT_TIMESTAMP"])

    def set_status(self, name, value):
        #Oppdaterer raden hvis den finnes, ellers lages den
        self.cursor.execute("UPDATE Status_register SET value = ?, last_updated = CURRENT_TIMESTAMP WHERE name = ?", (value, name))
        if self.cursor.rowcount == 0:
            self.cursor.execute("INSERT INTO Status_register (name, value) VALUES (?, ?)", (name, value))
        self.conn.commit()

    def get_last_dashboard_cmd_id(self):
        self.cursor.execute("SELECT MAX(id) FROM Dashboard_cmd_register")
        return self.cursor.fetchone()[0] or 0

    def get_dashboard_cmds_after(self, last_id):
        #Returnerer (id, action, parameters) for kommandoer nyere enn last_id
        self.cursor.execute("SELECT id, action, parameters FROM Dashboard_cmd_register WHERE id > ? ORDER BY id ASC", (last_id,))
        return self.cursor.fetchall()

    def __delete__(self):
        self.ro_conn.close()



if __name__ == "__main__":


    #Script starting
    database_controller = DatabaseController(True)
    database_controller.show_db_content()


    #Error_register
    # if True:
        # database_controller.create_table("Errors_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "hostname NVARCHAR(255)", "error_message TEXT", "component  NVARCHAR(100)", "error_type NVARCHAR(50)", "severity NVARCHAR(20)", "bot_version NVARCHAR(20)", "function_name NVARCHAR(100)"])
        # database_controller.show_table("Errors_register")
        # database_controller.easy_select_from("Errors_register", "select count(*)")

        # values_dict_1 = {"ERROR_MESSAGE": "Sick streamer..", "COMPONENT": "Cold Virus", "ERROR_TYPE": "Cough", "severity":"low"}
        # database_controller.insert_into("Errors_register", values_dict_1)

        # values_dict_2 = {"ERROR_MESSAGE": "Disconnected", "COMPONENT": "Twitch/Network"}
        # database_controller.insert_into("Errors_register", values_dict_2)

        # values_dict_3 = {"ERROR_MESSAGE": "Gif not shown", "COMPONENT": "gif-controller"}
        # database_controller.insert_into("Errors_register", values_dict_3)

        # database_controller.drop_table("Errors_register", 333)

    database_controller.select_from("select * from Errors_register")



    #Token_register
    # if True:
        # database_controller.create_table("Tokens_register", ["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "token_for NVARCHAR(100)", "expiration_date datetime2", "last_updated datetime2"])
        # database_controller.show_table("Tokens_register")
        # database_controller.easy_select_from("Tokens_register", "select count(*)")

        # values_dict_1 = {"token_for": "Albotkeinstein", "expiration_date": "2025-11-11 12:00:01"}
        # database_controller.insert_into("Tokens_register", values_dict_1)

        # values_dict_2 = {"token_for": "Albotkeinstein", "expiration_date": "2025-11-11 12:00:01"}
        # database_controller.insert_into("Tokens_register", values_dict_2)

        # database_controller.drop_table("Tokens_register", 333)

    database_controller.select_from("select * from Tokens_register")


    # if True:
        # database_controller.create_table("Info_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "action NVARCHAR(255)", "invoked_by NVARCHAR(100)", "function_name NVARCHAR(100)", "parameters NVARCHAR(255)", "bot_version NVARCHAR(20)"])
        # database_controller.show_table("Info_register")
        # database_controller.easy_select_from("Info_register", "select count(*)")

        # values_dict = {"action": "Welcome message", "invoked_by": "Albert autofunction"}
        # database_controller.insert_into("Info_register", values_dict)

        # values_dict = {"action": "Thank you for support!", "invoked_by": "Albert autofunction"}
        # database_controller.insert_into("Info_register", values_dict)

        # values_dict = {"action": "Shout out", "invoked_by": "Albert autofunction"}
        # database_controller.insert_into("Info_register", values_dict)

        # database_controller.drop_table("Info_register", 333)

    database_controller.select_from("select * from Info_register")


    # if True:
        # database_controller.create_table("Dashboard_cmd_register" ,["timestamp DATETIME DEFAULT CURRENT_TIMESTAMP", "invoked_by NVARCHAR(100)", "action NVARCHAR(255)", "parameters NVARCHAR(255)", "bot_version NVARCHAR(20)"])
        # database_controller.show_table("Dashboard_cmd_register")
        # database_controller.easy_select_from("Dashboard_cmd_register", "select count(*)")

        # values_dict_1 = {"ACTION": "REFRESH", "INVOKED_BY": "DASHBOARD", "PARAMETERS": "GIFS"}
        # database_controller.insert_into("Dashboard_cmd_register", values_dict_1)

        # values_dict_2 = {"ACTION": "REFRESH", "INVOKED_BY": "DASHBOARD", "PARAMETERS": "GREETINGS"}
        # database_controller.insert_into("Dashboard_cmd_register", values_dict_2)

        # values_dict = {"action": "Shout out", "invoked_by": "Albert autofunction"}
        # database_controller.insert_into("Dashboard_cmd_register", values_dict)

        # database_controller.drop_table("Dashboard_cmd_register", 333)

    database_controller.select_from("select * from Dashboard_cmd_register")


