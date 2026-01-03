from handlers.console import send_messages
from utils import state

def stop_bot():
    send_messages("Stopping all processes...")
    state.stop_all()
    send_messages("All processes terminated.")
