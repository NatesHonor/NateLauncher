# logging_handler.py
import os
from datetime import datetime

log_file_path = None

def generate_log_file():
    global log_file_path
    logs_dir = "logs"
    today_date = datetime.now().strftime("%Y-%m-%d")
    date_dir = os.path.join(logs_dir, today_date)

    # Ensure the main logs directory and the date-based subdirectory exist
    os.makedirs(date_dir, exist_ok=True)

    # Generate the base filename and check for existing logs
    base_filename = "MissionchiefBot.log"
    counter = 1
    while os.path.exists(os.path.join(date_dir, f"MissionchiefBot_{counter}.log")):
        counter += 1

    # Final log filename
    log_file_path = os.path.join(date_dir, f"MissionchiefBot_{counter}.log")

    # Create the log file
    with open(log_file_path, "w") as log_file:
        log_file.write("Log initialized\n")

    return log_file_path

def log_to_latest_file(message):
    if log_file_path is None:
        generate_log_file()

    with open(log_file_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {message}\n")
