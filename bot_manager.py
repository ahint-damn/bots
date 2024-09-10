import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from bot import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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
            quality_button = browser.find_element_by_id("grqh")
            quality_button.click()
            print(f"[{name}] Quality toggled.")
        except Exception as e:
            print(f"[{name}] Failed to find the quality button: {e}")

        try:
            input_field = browser.find_element_by_tag_name("input")
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
        """Continuously update the user window with bot information."""
        while True:
            bot_info = f"Bots Alive: {sum(bot.alive for bot in self.browsers.values())}<br>"
            for bot in self.browsers.values():
                bot_info += f"Bot {bot.name}: x={bot.position[0]}, y={bot.position[1]}, length={bot.length}<br>"

            script = f"""
            if (!document.getElementById('bot-overlay')) {{
                var div = document.createElement('div');
                div.id = 'bot-overlay';
                div.style.position = 'fixed';
                div.style.bottom = '50px';
                div.style.left = '10px';
                div.style.fontSize = '12px';
                div.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                div.style.color = 'white';
                div.style.fontFamily = 'Arial';
                div.style.borderRadius = '5px';
                div.style.padding = '10px';
                div.style.zIndex = '10000';
                document.body.appendChild(div);
            }}
            document.getElementById('bot-overlay').innerHTML = `{bot_info}`;
            """
            self.user_browser.execute_script(script)
            time.sleep(1)

    def close_instances(self):
        """Close all browser instances."""
        with self.browsers_lock:
            for bot in self.browsers.values():
                bot.close()

        self.executor.shutdown(wait=False)
