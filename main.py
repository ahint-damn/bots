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

browsers = {}  # Dictionary to store browser instances with names
browser_count = 4
browsers_lock = Lock()  # Lock to ensure thread-safe access to browsers

# Main function
def main():
    performChecks()

# Function to handle user input for number of bots
def performChecks():
    print("Loading...")
    global browser_count
    print("Creating instances asynchronously...")
    createInstances()
    print("Instances created.")
    print("Starting bots...")
    startBots()

# Function to create browser instances asynchronously
def createInstances():
    with ThreadPoolExecutor(max_workers=browser_count) as executor:
        for _ in range(browser_count):
            executor.submit(loadBotInstance)

# Function to load a single bot instance asynchronously
def loadBotInstance():
    # Suppress Selenium logs
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")  # Suppress logs

    # Use Service to suppress driver logs
    service = Service(executable_path='chromedriver.exe', log_path=os.devnull)

    # Create browser instance
    browser = webdriver.Chrome(service=service, options=options)
    browser.set_window_position(0, 0)
    browser.set_window_size(500, 500)
    browser.get("http://slither.io")
    time.sleep(0.1)

    # Pick random name from names.txt
    with open('names.txt') as f:
        names = f.readlines()
    name = random.choice(names).strip()

    # Store the browser instance with the name as the key in a thread-safe way
    with browsers_lock:
        browsers[name] = browser

    try:
        qualityButton = browser.find_element(By.ID, "grqh")
        qualityButton.click()
        print(f"[{name}] Quality toggled.")
    except Exception as e:
        print(f"[{name}] Failed to find the quality button: {e}")

    try:
        input_field = browser.find_element(By.TAG_NAME, "input")
        input_field.send_keys(name)
        print(f"[{name}] Name set.")
    except Exception as e:
        print(f"[{name}] Failed to set name: {e}")

# Function to close all browser instances
def closeInstances():
    with browsers_lock:
        for name, browser in browsers.items():
            browser.close()
            browser.quit()

# Function to start the bots
def startBots():
    with ThreadPoolExecutor(max_workers=browser_count) as executor:
        with browsers_lock:
            for name, browser in browsers.items():
                executor.submit(bot, name, browser)

# Bot function to simulate the game and interact with the browser console
def bot(name, browser):
    print(f'Starting bot for {name}...')
    try:
        startButton = browser.find_element(By.CLASS_NAME, "sadg1")
        startButton.click() 
        print(f"[{name}] Game started.")
    except Exception as e:
        print(f"[{name}] Failed to start the game: {e}")

    try:
        while True:
            snake = browser.execute_script("return window.slither;")
            if snake is None:
                print(f"[{name}] Loading...")
                time.sleep(0.5)
            else:
                xx = snake["xx"]
                yy = snake["yy"]
                ang = snake["ang"]
                length = math.floor(15 * browser.execute_script("return window.fpsls[window.slither.sct] + window.slither.fam / window.fmlts[window.slither.sct] - 1")-5)
                print(f"[{name}] Bot position: xx = {xx}, yy = {yy}, ang = {ang}, length = {length}")
                time.sleep(0.1)
    except Exception as e:
        print(f"[{name}] Failed to retrieve bot info: {e}")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")
    closeInstances()
