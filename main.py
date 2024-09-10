import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import math
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


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
                    print(f"[{self.name}] Loading...")
                    time.sleep(0.5)
                else:
                    xx = snake["xx"]
                    yy = snake["yy"]
                    ang = snake["ang"]
                    length = math.floor(
                        15 * self.browser.execute_script("return window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1") - 5
                    )
                    print(f"[{self.name}] Bot position: xx = {xx}, yy = {yy}, ang = {ang}, length = {length}")
                    time.sleep(0.1)
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
    def __init__(self, browser_count=4):
        self.browser_count = browser_count
        self.browsers = {}  # Store bots with names as keys
        self.browsers_lock = Lock()

    def load_bot_instance(self):
        """Load a bot instance asynchronously."""
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")  # Suppress logs

        # Use Service to suppress driver logs
        service = Service(executable_path='chromedriver.exe', log_path=os.devnull)
        browser = webdriver.Chrome(service=service, options=options)
        browser.set_window_position(0, 0)
        browser.set_window_size(500, 500)
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

    def create_instances(self):
        """Create browser instances asynchronously."""
        with ThreadPoolExecutor(max_workers=self.browser_count) as executor:
            for _ in range(self.browser_count):
                executor.submit(self.load_bot_instance)

    def start_bots(self):
        """Start the bots by running them in parallel."""
        with ThreadPoolExecutor(max_workers=self.browser_count) as executor:
            with self.browsers_lock:
                for bot in self.browsers.values():
                    bot.start_game()
                    executor.submit(bot.run)

    def close_instances(self):
        """Close all browser instances."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.close()


def main():
    bot_manager = BotManager(browser_count=4)
    print("Creating instances asynchronously...")
    bot_manager.create_instances()
    print("Instances created.")
    print("Starting bots...")
    bot_manager.start_bots()

    input("Press Enter to exit...")
    bot_manager.close_instances()


if __name__ == "__main__":
    main()
