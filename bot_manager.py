import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from bot import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import random

class BotManager:
    def __init__(self, browser_count=1, user_browser=None):
        self.browser_count = browser_count
        self.browsers = {}  # Store bots with names as keys
        self.browsers_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=self.browser_count)
        self.user_browser = user_browser  # The main user window for showing bot info

    def load_bot_instance(self):
        """Load a bot instance asynchronously."""
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-notifications")
        options.add_argument("--headless")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--log-level=3")
        options.add_argument("window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

        service = Service(executable_path='chromedriver.exe', log_path=os.devnull)
        browser = webdriver.Chrome(service=service, options=options)
        browser.get("http://slither.io")
        time.sleep(0.1)

        with open('names.txt') as f:
            names = f.readlines()
        name = random.choice(names).strip()

        bot = Bot(name, browser)

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

        for future in as_completed(futures):
            future.result()

        end_time = time.time()
        print(f"All bots initialized in {end_time - start_time:.2f} seconds.")

    def start_bots(self):
        """Start the bots by running them in parallel."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.start_game()
                self.executor.submit(bot.run)

        self.update_overlay()

    def update_overlay(self):
        """Continuously update the user window with bot and user information."""
        while True:
            # Update bot information
            bot_info = f"Bots Alive: {sum(bot.alive for bot in self.browsers.values())}<br>"
            for bot in self.browsers.values():
                bot_info += f"Bot {bot.name}: x={bot.position[0]}, y={bot.position[1]}, length={bot.length}<br>"

            # Update user information
            user_info = self.get_user_info()

            script = f"""
            // Create bot info overlay if not exists
            if (!document.getElementById('bot-overlay')) {{
                var botDiv = document.createElement('div');
                botDiv.id = 'bot-overlay';
                botDiv.style.position = 'fixed';
                botDiv.style.top = '10px';
                botDiv.style.left = '10px';
                botDiv.style.fontSize = '12px';
                botDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                botDiv.style.color = 'white';
                botDiv.style.fontFamily = 'Arial';
                botDiv.style.borderRadius = '5px';
                botDiv.style.padding = '10px';
                botDiv.style.zIndex = '10000';
                document.body.appendChild(botDiv);
            }}
            document.getElementById('bot-overlay').innerHTML = `{bot_info}`;

            // Create user info overlay if not exists
            if (!document.getElementById('user-overlay')) {{
                var userDiv = document.createElement('div');
                userDiv.id = 'user-overlay';
                userDiv.style.position = 'fixed';
                userDiv.style.bottom = '60px';
                userDiv.style.left = '10px';
                userDiv.style.fontSize = '12px';
                userDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                userDiv.style.border = '1px solid firebrick';
                userDiv.style.color = 'white';
                userDiv.style.fontFamily = 'Arial';
                userDiv.style.borderRadius = '5px';
                userDiv.style.padding = '10px';
                userDiv.style.zIndex = '10000';
                document.body.appendChild(userDiv);
            }}
            document.getElementById('user-overlay').innerHTML = `{user_info}`;
            """
            self.user_browser.execute_script(script)
            time.sleep(1)

    def get_user_info(self):
        """Retrieve the user snake's position and length."""
        try:
            snake = self.user_browser.execute_script("return window.slither;")
            if snake:
                user_x = snake['xx']
                user_y = snake['yy']
                user_length = self.user_browser.execute_script(
                    "return Math.floor(15 * window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1) - 5"
                )
                return f"User Position: x={math.floor(user_x)}, y={math.floor(user_y)}, length={user_length}<br>"
            else:
                return "User not in game<br>"
        except Exception as e:
            return f"Error retrieving user info: {e}<br>"

    def close_instances(self):
        """Close all browser instances."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.close()

        self.executor.shutdown(wait=False)
