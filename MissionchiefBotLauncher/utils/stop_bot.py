from handlers.console import send_messages
from utils import state

def stop_bot():
    state.stop_requested = True

    proc = state.current_process
    if proc is not None and proc.poll() is None:
        pid = proc.pid
        send_messages(f"Attempting to stop bot with PID: {pid}...")
        try:
            proc.kill()
            send_messages(f"Bot process with PID {pid} terminated successfully.")
        except Exception as ex:
            send_messages(f"Error during bot termination: {str(ex)}")
        finally:
            send_messages("Bot has been stopped.")
        state.current_process = None
    else:
        send_messages("No bot process is currently running.")
