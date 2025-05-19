import time
import select
import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .models import Advertisement

BASE_URL = "https://auto.ria.com/car/used/"


def get_element_text(soup, selector, default=None):
    element = soup.select_one(selector)
    return element.text.strip() if element and element.text.strip() != "" else default


def get_phone_number(driver: webdriver):
    try:
        show_phone_link = WebDriverWait(driver, 2).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "a.phone_show_link"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", show_phone_link)
        show_phone_link.click()
        print("Phone show link clicked successfully.")
    except TimeoutException:
        print("Phone show link not found within the timeout period.")
        return None

    try:
        phone_number_element = WebDriverWait(driver, 2).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, "popup-successful-call-desk")
            )
        )
        phone_number = phone_number_element.text

    except TimeoutException:
        print("Phone number not found within the timeout period.")
        return None

    phone_number = phone_number.replace(" ", "").replace("(", "").replace(")", "")
    return "+38" + phone_number


def parse_advertisement_page(driver, advert_link: str) -> None:
    try:
        driver.get(advert_link)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
    except TimeoutException:
        print("Failed to retrieve page.")
        return None

    advert = Advertisement(
        url=advert_link,
        title=get_element_text(soup, "h1.head", default="Unknown"),
        price_usd=float(
            get_element_text(soup, "div.price_value strong", default="0")
            .replace(" ", "")
            .replace("$", "")
            .replace("€", "")
        ),
        odometer=int(
            get_element_text(
                soup, "div.base-information span.size18", default="0"
            ).replace(" ", "")
            + "000"
        ),
        username=get_element_text(
            soup, "div.seller_info_name a.sellerPro", default="Unknown"
        ),
        image_url=(
            soup.select_one("img.outline.m-auto").get("src")
            if soup.select_one("img.outline.m-auto")
            else None
        ),
        images_count=int(
            get_element_text(soup, "span.dhide", default="0").replace("з ", "")
        ),
        car_number=get_element_text(soup, "span.state-num", default="Unknown")[:10],
        car_vin=get_element_text(soup, "span.label-vin", default="Unknown"),
        phone_number=get_phone_number(driver),
    )
    return advert


def get_single_page_adverts_links(page_soup: BeautifulSoup) -> list[str]:
    results = page_soup.select(".m-link-ticket")
    links_list = [link.get("href") for link in results if link.get("href")]
    return links_list


def get_all_advertisments(saved_links: list[str] = None) -> list[Advertisement]:
    if saved_links is None:
        saved_links = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (optional)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    print("Starting Chrome driver...")
    # driver = webdriver.Chrome(options=options)
    # service = Service("/usr/bin/chromedriver", service_args=["--verbose"])
    # service.start_timeout = 300 
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options,
        # desired_capabilities=DesiredCapabilities.CHROME,
    )
    print("Chrome driver started.")
    print("Connected to Selenium Remote WebDriver.")  
    page_number = 1
    advertisements_list = []

    while True:
        driver.get(BASE_URL + f"?page={page_number}")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        links = get_single_page_adverts_links(soup)

        for link in links[:2]:
            if saved_links and link in saved_links:
                print(f"Link already exists: {link}")
                continue
            advert = parse_advertisement_page(driver, link)
            if advert:
                print(advert.__dict__)
                advertisements_list.append(advert)

        page_number += 1
        next_page_link = soup.select_one("a.page-link.js-next")
        if not next_page_link or page_number > 2:
            break

    driver.quit()

    return advertisements_list


if __name__ == "__main__":
    start_time = time.time()  # Record the start time
    advertisements = get_all_advertisments()
    end_time = time.time()  # Record the end time

    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Total advertisements fetched: {len(advertisements)}")
    print(f"Execution time: {execution_time:.2f} seconds")
