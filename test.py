from flask import Flask, send_from_directory, request
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Route to serve the HTML file from the root directory
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Route to serve the CSS file
@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")

# Function to open video in multiple browser instances
def open_keep_active(driver, video_url):
    try:
        driver.get(video_url)
        time.sleep(2)

        try:
            play_button = driver.find_element(By.CSS_SELECTOR, "button.play-button-selector")
            play_button.click()
        except Exception as e:
            print("Error playing video:", e)
            return

        while True:
            time.sleep(5)
            ActionChains(driver).move_by_offset(0, 0).perform()
            driver.execute_script("window.scrollBy(0, 1);")
            driver.execute_script("window.scrollBy(0, -1);")
    finally:
        driver.quit()

# Route to handle form submission and trigger Selenium instances
@app.route("/play_videos", methods=["POST"])
def play_videos():
    video_url = request.form.get("link")
    video_numbers = int(request.form.get("instances"))

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    drivers = [webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) for _ in range(video_numbers)]
    threads = [threading.Thread(target=open_keep_active, args=(driver, video_url)) for driver in drivers]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return "Videos are playing in the background!"

if __name__ == "__main__":
    app.run(debug=True)
