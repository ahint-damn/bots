import math
import time
from selenium.webdriver.common.by import By

class Bot:
    def __init__(self, name, browser):
        self.name = name
        self.browser = browser
        self.alive = True
        self.position = (0, 0)
        self.length = 0
        self.iconPosition = (0, 0)

    def start_game(self):
        """Start the game by clicking the start button."""
        print(f'Starting bot for {self.name}...')
        try:
            # Updated to use find_element with By.CLASS_NAME
            start_button = self.browser.find_element(By.CLASS_NAME, "sadg1")
            start_button.click()
            print(f"[{self.name}] Game started.")
        except Exception as e:
            print(f"[{self.name}] Failed to start the game: {e}")

    def calculate_angle_to_user(self, user_position):
        """Calculate the angle from the bot's position to the user's position."""
        bot_x, bot_y = self.position
        user_x, user_y = user_position
        delta_x = user_x - bot_x
        delta_y = user_y - bot_y
        # Calculate angle using atan2 (gives angle in radians)
        angle = math.atan2(delta_y, delta_x)
        return angle

    def move_towards_user(self, angle):
        """Move the bot towards the calculated angle."""
        # Calculate target canvas coordinates for the bot based on the angle
        canvas = self.browser.find_element(By.TAG_NAME, "canvas")
        canvas_width = canvas.size['width'] / 2  # Center of the canvas
        canvas_height = canvas.size['height'] / 2  # Center of the canvas

        # Move the bot towards the target direction by simulating mouse movement
        target_x = canvas_width + 100 * math.cos(angle)
        target_y = canvas_height + 100 * math.sin(angle)
        print(f"[{self.name}] Target position: x = {target_x}, y = {target_y}")
        print(f"[{self.name}] Moving bot towards user...")

        self.browser.execute_script(f"window.xm = {target_x}; window.ym = {target_y};")

    def run(self, user_position):
        """Run the bot to simulate the game and follow the user's snake."""
        try:
            while True:
                snake = self.browser.execute_script("return window.slither;")
                if snake is None:
                    # If there's a start button, click it
                    start_button = self.browser.find_element(By.CLASS_NAME, "sadg1")
                    try:
                        if start_button.size["height"] > 0 and start_button.size["width"] > 0 and start_button.is_displayed():
                            start_button.click()
                            print(f"[{self.name}] Game restarted.")
                    except Exception:
                        pass
                    time.sleep(0.5)
                else:
                    try:
                        # Get bot position
                        self.position = (math.floor(snake["xx"]), math.floor(snake["yy"]))
                        self.length = self.browser.execute_script(
                            "return Math.floor(15 * window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1) - 5"
                        )

                        # get body > div:nth-child(20) > img:nth-child(4)
                        mapPin = self.browser.find_element(By.CSS_SELECTOR, "body > div:nth-child(20) > img:nth-child(4)")
                        mapPinStyles = mapPin.get_attribute("style")
                        print(mapPinStyles)
                        # get left: {value}px; top: {value}px;
                        # get the x and y values
                        x = float(mapPinStyles.split("left: ")[1].split("px")[0])
                        y = float(mapPinStyles.split("top: ")[1].split("px")[0])
                        self.iconPosition = (x, y)
                        print(f"[{self.name}] Bot icon position: x = {x}, y = {y}")

                        # Calculate the angle towards the user
                        angle_to_user = self.calculate_angle_to_user(user_position)

                        # Move the bot towards the user based on the angle
                        self.move_towards_user(angle_to_user)

                        print(f"[{self.name}] Bot position: x = {self.position[0]}, y = {self.position[1]}, length = {self.length}, angle = {math.degrees(angle_to_user)}°")
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
