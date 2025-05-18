import time
import select
from tkinter import N
import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .models import Advertisement

BASE_URL = "https://auto.ria.com/car/used/"


def get_element_text(soup, selector, default=None):
    element = soup.select_one(selector)
    return element.text.strip() if element else default


def get_phone_number(driver: webdriver):
    try:
        show_phone_link = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "a.phone_show_link"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", show_phone_link)
        show_phone_link.click()
        print("Phone show link clicked successfully.")
    except TimeoutException:
        print("Phone show link not found within the timeout period.")
        return None

    try:
        phone_number_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, "popup-successful-call-desk")
            )
        )
        phone_number = phone_number_element.text

    except TimeoutException:
        print("Phone number not found within the timeout period.")
        return None

    phone_number = phone_number.replace(" ", "").replace("(", "").replace(")", "")
    return int("38" + phone_number)


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
        title=soup.select_one("h1.head").get("title"),
        price_usd=float(
            get_element_text(soup, "div.price_value strong", default="0")
            .replace(" ", "")
            .replace("$", "")
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
        image_url=soup.select_one("img.outline.m-auto").get("src"),
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


def get_all_advertisments() -> None:
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (optional)
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    driver.get(BASE_URL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    links = get_single_page_adverts_links(soup)
    advertisements = []
    for link in links[:5]:
        advert = parse_advertisement_page(driver, link)
        if advert:
            advertisements.append(advert)

    driver.quit()
    
    return advertisements

if __name__ == "__main__":
    advertisements = get_all_advertisments()
    
