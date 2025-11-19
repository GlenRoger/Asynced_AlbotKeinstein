import tkinter as tk
from datetime import datetime

from Testing_sqlite.sql_reader_halloween import Database_Reader


def refresh_button_command():
    print(f"Refresh {selected_option.get()}")


def calculate_message_age(message_timestamp):

    dt = datetime.strptime(message_timestamp, "%Y-%m-%d %H:%M:%S")

    # Get current time
    now = datetime.now()

    # Calculate the difference
    age = now - dt

    # Extract hours, minutes, seconds
    hours = int(age.total_seconds() // 3600)
    minutes = int((age.total_seconds() % 3600) // 60)
    seconds = int(age.total_seconds() % 60)

    if hours < 0:
        return "EXPIRED!"
    if minutes < 10:
        return f"{minutes}min {seconds}s"
    else:
        return f"(OLD) {minutes}min {seconds}s"


def update_info():
    latest_info = db_reader.get_latest_info_as_touple()


    id              = ""
    timestamp       = ""
    action          = ""
    invoked_by      = ""
    function_name   = ""
    parameters      = ""
    bot_version     = ""

    print("\n\nLatest info:")
    print(latest_info)


    if not latest_info:
        return ""


    return_string = ""

    print(f"len(latest_info): {len(latest_info)}")

    if len(latest_info) == 1:
        print("\n\n\nONLY ONE ROW\n\n\n")
        latest_info = [latest_info]


    print("\n\nLatest info:")
    print(latest_info)


    for l_i in latest_info:
    
        msg_age = calculate_message_age(l_i[1])
    
        if msg_age != 'EXPIRED!':
            return_string += f"Tid siden utført:{msg_age}, handling: {l_i[2]}, function: {l_i[3]}\n"


    return return_string


def update_error_info():

    latest_error = db_reader.get_latest_error_as_touple()

    id              = ""
    timestamp       = ""
    hostname        = ""
    error_message   = ""
    component       = ""
    error_type      = ""
    severity        = ""
    bot_version     = ""

    if latest_error:
        id              = latest_error[0]
        timestamp       = latest_error[1]
        hostname        = latest_error[2]
        error_message   = latest_error[3]

        if error_message == 'NULL':
            error_message = "Not specified.."


        component       = latest_error[4]
        error_type      = latest_error[5]

        if error_type == 'NULL':
            error_type = "Unknown"


        severity        = latest_error[6]

        if severity == 'NULL':
            severity = "Unknown"

        bot_version     = latest_error[7]


        msg_age = calculate_message_age(timestamp)

        if msg_age != 'EXPIRED!':
            error_message = [f"Error occurred {msg_age} ago." , f"Type of error {error_type}, severity {severity}: {error_message}"]
        else:
            error_message = ["", ""]

        return error_message


# Function to change text
def change_text():

    #ERROR
    current_text = error_label.cget("text")
    
    error_message = update_error_info()

    if not error_message:
        return

    if error_message[0] != "":
        if current_text != error_message:
            error_title_label.config(text = error_message[0])
            error_label.config(text = error_message[1])
    else:
        error_title_label.config(text = "No recent erors found..")
        error_label.config(text = "...")


    #INFO
    current_info_text = info_label.cget("text")

    info_message = update_info()

    if info_message != "":
        if current_text != info_message:
            info_title_label.config(text = "Recent info..")
            info_label.config(text = info_message)
    else:
        info_title_label.config(text = "No recent info found..")
        info_label.config(text = "...")

    # Schedule next change in 5 seconds (5000 milliseconds)
    window.after(5000, change_text)


#db-connection
db_reader = Database_Reader()

# Create the main window
window = tk.Tk()
window.title("Albot Keinstein Dashboard")
window.geometry("600x300")

# Add a label to show some data
error_title_label = tk.Label(window, text="Last error message:", font=("Arial", 14), justify="left")
error_title_label.pack()

error_label = tk.Label(window, text="No new errors found!", font=("Arial", 12), justify="left")
error_label.pack()

info_title_label = tk.Label(window, text="Recent info messages:", font=("Arial", 14), justify="left")
info_title_label.pack()

info_label = tk.Label(window, text="No new info found!", font=("Arial", 12), justify="left")
info_label.pack()


label_albot_token = tk.Label(window, text="Wait for albot's token age...", font=("Arial", 14), justify="left")
label_albot_token.pack()

label_TSTWT_token = tk.Label(window, text="Wait for albot's TSTWT token age...", font=("Arial", 14), justify="left")
label_TSTWT_token.pack()

selected_option = tk.StringVar()
selected_option.set("Apple")

menu = tk.OptionMenu(window, selected_option, "Apple", "Banana", "Orange")
menu.pack(pady=20)


#REFRESH BUTTON
go_button = tk.Button(window, text="Refresh", command=refresh_button_command, 
                      font=("Arial", 14), bg="green", fg="white")
go_button.pack()





# Start the timer (first change after 5 seconds)
window.after(5000, change_text)


# Run the application
window.mainloop()