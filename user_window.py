from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

def open_user_window():
    """Open a user-playable window and wait for the game to start."""
    options = Options()
    options.add_argument("window-size=1920x1080")
    service = Service(executable_path='chromedriver.exe', log_path=os.devnull)

    browser = webdriver.Chrome(service=service, options=options)
    browser.get("http://slither.io")

    # Print window position and URL
    print(f"User playable window opened at URL: {browser.current_url}")

    while True:
        try:
            snake = browser.execute_script("return window.slither;")
            if snake is not None:
                print("User has started the game. Starting bot initialization...")
                break
        except:
            pass
        time.sleep(1)

    return browser
