import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import signal
import sys
from selenium.webdriver.chrome.options import Options


class Bot:
    def __init__(self, name, browser):
        self.name = name
        self.browser = browser

    def start_game(self):
        """Start the game by clicking the start button."""
        print(f'Starting bot for {self.name}...')
        try:
            start_button = self.browser.find_element(By.CLASS_NAME, "sadg1")
            start_button.click()
            print(f"[{self.name}] Game started.")
        except Exception as e:
            print(f"[{self.name}] Failed to start the game: {e}")

    def run(self):
        """Run the bot to simulate the game and interact with the browser console."""
        try:
            while True:
                snake = self.browser.execute_script("return window.slither;")
                if snake is None:
                    # if there is start button, click it
                    start_button = self.browser.find_element(By.CLASS_NAME, "sadg1")
                    try:
                        if start_button.size["height"] > 0 and start_button.size["width"] > 0 and start_button.is_displayed():
                            start_button.click()
                            print(f"[{self.name}] Game restarted.")
                    except Exception as e:
                        nothing = 0
                    time.sleep(0.5)
                else:
                    try:
                        xx = snake["xx"]
                        yy = snake["yy"]
                        ang = snake["ang"]
                        length = self.browser.execute_script(
                            "return Math.floor(15 * window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1) - 5"
                        )
                        print(f"[{self.name}] Bot position: x = {xx}, y = {yy}, ang = {ang}, length = {length}")
                    except Exception as e:
                        print(f"[{self.name}] Failed to retrieve bot info: {e}")
                    time.sleep(0.5)
        except Exception as e:
            print(f"[{self.name}] Failed to retrieve bot info: {e}")

    def close(self):
        """Close the browser instance."""
        try:
            self.browser.close()
            self.browser.quit()
            print(f"[{self.name}] Browser closed.")
        except Exception as e:
            print(f"Failed to close browser for {self.name}: {e}")


class BotManager:
    def __init__(self, browser_count=1):
        self.browser_count = browser_count
        self.browsers = {}  # Store bots with names as keys
        self.browsers_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=self.browser_count)

    def load_bot_instance(self):
        """Load a bot instance asynchronously."""
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--log-level=3")  # Suppress logs

        # Set a screen resolution that works for most websites
        options.add_argument("window-size=1920x1080")

        # Set a common user agent for better simulation of a real browser
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

        service = Service(executable_path='chromedriver.exe', log_path=os.devnull)
        browser = webdriver.Chrome(service=service, options=options)
        browser.get("http://slither.io")
        time.sleep(0.1)

        # Pick random name from names.txt
        with open('names.txt') as f:
            names = f.readlines()
        name = random.choice(names).strip()

        # Create bot instance
        bot = Bot(name, browser)

        # Store the bot in a thread-safe way
        with self.browsers_lock:
            self.browsers[name] = bot

        try:
            quality_button = browser.find_element(By.ID, "grqh")
            quality_button.click()
            print(f"[{name}] Quality toggled.")
        except Exception as e:
            print(f"[{name}] Failed to find the quality button: {e}")

        try:
            input_field = browser.find_element(By.TAG_NAME, "input")
            input_field.send_keys(name)
            print(f"[{name}] Name set.")
        except Exception as e:
            print(f"[{name}] Failed to set name: {e}")

        return bot

    def create_instances(self):
        """Create browser instances asynchronously and wait for all to complete."""
        futures = [self.executor.submit(self.load_bot_instance) for _ in range(self.browser_count)]
        
        print("Waiting for all bots to initialize...")
        start_time = time.time()

        # Wait for all bots to initialize and log the time
        for future in as_completed(futures):
            future.result()  # Ensure exceptions are raised if any

        end_time = time.time()
        print(f"All bots initialized in {end_time - start_time:.2f} seconds.")

    def start_bots(self):
        """Start the bots by running them in parallel."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.start_game()
                self.executor.submit(bot.run)

    def close_instances(self):
        """Close all browser instances."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.close()

        # Shutdown the executor and cancel all running tasks
        self.executor.shutdown(wait=False)


def signal_handler(sig, frame):
    print("\nInterrupt received, shutting down...")
    bot_manager.close_instances()  # Ensure all browsers are closed
    sys.exit(0)


def main():
    global bot_manager
    bot_manager = BotManager(browser_count=1)  # Specify the number of bots you want to run
    print("Creating instances asynchronously...")
    bot_manager.create_instances()
    print("Instances created.")
    print("Starting bots...")
    bot_manager.start_bots()

    signal.signal(signal.SIGINT, signal_handler)  # Capture Ctrl+C signal

    try:
        input("Press Enter to exit...")  # Keep the program running
    except KeyboardInterrupt:
        pass  # Handle additional Ctrl+C if needed

    bot_manager.close_instances()


if __name__ == "__main__":
    main()
