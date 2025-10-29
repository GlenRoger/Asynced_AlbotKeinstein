import tkinter as tk
from datetime import datetime

from sql_reader import Database_Reader


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

label_albot_token = tk.Label(window, text="Wait for albot's token age...", font=("Arial", 14), justify="left")
label_albot_token.pack()

label_TSTWT_token = tk.Label(window, text="Wait for albot's TSTWT token age...", font=("Arial", 14), justify="left")
label_TSTWT_token.pack()



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


    if error_message[0] != "":
        if current_text != error_message:
            error_title_label.config(text = error_message[0])
            error_label.config(text = error_message[1])
    else:
        error_title_label.config(text = "No recent erors found..")
        error_label.config(text = "...")


    # Schedule next change in 5 seconds (5000 milliseconds)
    window.after(2000, change_text)

# Start the timer (first change after 5 seconds)
window.after(2000, change_text)


# Run the application
window.mainloop()