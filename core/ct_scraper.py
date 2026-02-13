import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.energizect.com/rate-board/compare-energy-supplier-rates"

def fetch_ct_offers_selenium():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(3)

    # STEP 1 — Switch into the iframe
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    time.sleep(2)

    # STEP 2 — Click Utility dropdown
    driver.find_element(By.XPATH, "//div[contains(., 'Utility') and @role='button']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//li[contains(., 'Eversource')]").click()

    # STEP 3 — Click Customer Type dropdown
    driver.find_element(By.XPATH, "//div[contains(., 'Customer Type') and @role='button']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//li[contains(., 'Business')]").click()

    # STEP 4 — Click Fuel Type dropdown
    driver.find_element(By.XPATH, "//div[contains(., 'Fuel Type') and @role='button']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//li[contains(., 'Electric')]").click()

    # STEP 5 — Wait for offers to load
    time.sleep(5)

    # STEP 6 — Scrape offer cards
    cards = driver.find_elements(By.XPATH, "//*[contains(@class, 'offer')]")

    if not cards:
        driver.quit()
        raise RuntimeError("No offers found — iframe interaction may need updated selectors.")

    offers = []
    for card in cards:
        offers.append({"raw": card.text})

    driver.quit()

    return pd.DataFrame(offers)