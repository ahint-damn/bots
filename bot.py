import math
import time

class Bot:
    def __init__(self, name, browser):
        self.name = name
        self.browser = browser
        self.alive = True
        self.position = (0, 0)
        self.length = 0

    def start_game(self):
        """Start the game by clicking the start button."""
        print(f'Starting bot for {self.name}...')
        try:
            start_button = self.browser.find_element_by_class_name("sadg1")
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
                    start_button = self.browser.find_element_by_class_name("sadg1")
                    try:
                        if start_button.size["height"] > 0 and start_button.size["width"] > 0 and start_button.is_displayed():
                            start_button.click()
                            print(f"[{self.name}] Game restarted.")
                    except Exception:
                        pass
                    time.sleep(0.5)
                else:
                    try:
                        self.position = (math.floor(snake["xx"]), math.floor(snake["yy"]))
                        self.length = self.browser.execute_script(
                            "return Math.floor(15 * window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1) - 5"
                        )
                        print(f"[{self.name}] Bot position: x = {self.position[0]}, y = {self.position[1]}, length = {self.length}")
                    except Exception as e:
                        print(f"[{self.name}] Failed to retrieve bot info: {e}")
                    time.sleep(0.5)
        except Exception as e:
            print(f"[{self.name}] Failed to retrieve bot info: {e}")
        self.alive = False

    def close(self):
        """Close the browser instance."""
        try:
            self.browser.close()
            self.browser.quit()
            print(f"[{self.name}] Browser closed.")
        except Exception as e:
            print(f"Failed to close browser for {self.name}: {e}")
