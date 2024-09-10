import signal
import sys
from bot_manager import BotManager
from user_window import open_user_window

def signal_handler(sig, frame):
    print("\nInterrupt received, shutting down...")
    bot_manager.close_instances()
    sys.exit(0)

def main():
    global bot_manager
    user_browser = open_user_window()

    bot_manager = BotManager(browser_count=3, user_browser=user_browser)
    print("Creating instances asynchronously...")
    bot_manager.create_instances()
    print("Instances created.")
    print("Starting bots...")
    bot_manager.start_bots()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        pass

    user_browser.quit()
    bot_manager.close_instances()

if __name__ == "__main__":
    main()
