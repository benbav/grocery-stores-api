import requests
import csv
import time
from playwright.sync_api import sync_playwright

# run this file maybe once a year to update the whole foods store list


def get_all_wf_store_ids():
    """
    Get most recent list of Whole Foods store IDs in the US
    """

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    response = requests.get("https://www.wholefoodsmarket.com/customer-service/contact-us", headers=headers)

    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(response.text, "html.parser")

    data_list = []

    # Define a regular expression pattern to match 'option' and 'value' pairs
    pattern = re.compile(r'"option":"([^"]+)","value":"([^"]+)"')

    # Find elements that contain the pattern
    matches = re.finditer(pattern, str(soup))

    for match in matches:
        option = match.group(1)
        value = match.group(2)
        data_list.append({"option": option, "value": value})

    for item in data_list:
        item["updated_address"] = ""

    # Specify the CSV file name
    csv_file = "wf_store_ids.csv"

    # Define the fieldnames for the CSV file
    fieldnames = ["address", "store_id", "updated_address"]

    # can add logic - if not in csv, add to csv

    # Write the data to the CSV file
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        for item in data_list:
            # Split the 'value' field to extract store_id
            store_id = item["value"].split("|")[0]
            writer.writerow(
                {
                    "address": item["option"],
                    "store_id": item["value"],
                    "updated_address": item["updated_address"],
                }
            )

    print(f"Data has been saved to {csv_file}")


# Function to scrape the ZIP code from Google Maps
def scrape_zipcode(address):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com/maps")

        # Input the address and press Enterc
        page.fill("input[aria-label='Search Google Maps']", address)
        page.press("input[aria-label='Search Google Maps']", "Enter")

        # Wait for the result to load (you might need to adjust the selector)
        page.wait_for_selector(".widget-zoom-slider")

        # Extract the ZIP code (you might need to adjust the selector)
        zipcode = page.locator(".widget-reveal-card").text()

        browser.close()
        return zipcode


# Replace 'your_file.csv' with the path to your CSV file
with open("your_file.csv", "r") as csv_file:
    lines = csv_file.readlines()
    for line in lines:
        address = line.strip()  # Assuming each line in the CSV is an address
        zipcode = scrape_zipcode(address)
        print(f"Address: {address}, ZIP code: {zipcode}")
