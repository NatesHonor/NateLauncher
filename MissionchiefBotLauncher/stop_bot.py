from PyQt6.QtCore import QProcess
from start_bot import send_messages

def stop_bot(process):
    if process is None or process.state() == QProcess.ProcessState.NotRunning:
        send_messages("No bot process is currently running.")
        return None
    pid = process.processId()
    send_messages(f"Attempting to stop bot with PID: {pid}...")
    try:
        process.kill()
        send_messages(f"Bot process with PID {pid} terminated successfully.")
    except Exception as ex:
        send_messages(f"Error during bot termination: {str(ex)}")
    finally:
        send_messages("Bot has been stopped.")
        return None
