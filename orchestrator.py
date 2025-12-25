import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
#importing from all three modules

from scraper import fetch_html_scraperapi
from parser import extract_prices_from_html
from analyzer import generate_report


def run_phase1_pipeline(item_name: str) -> dict:
    

    html_content = fetch_html_scraperapi(item_name)

    if not html_content:
        return {"Error": "failed to fetrch data from eBay"}
    print(f"Got {len(html_content)} html characters")


    price_list = extract_prices_from_html(html_content)

    if not price_list:
        return {"Error": "could not extract from the page"}
    print(f"extracted {len(price_list)} prices")


    valuation_report = generate_report(price_list)

    return valuation_report


if __name__ == "__main__":

    test_items = ["iPhone 15", "Playstation 5", "RTX 3090"]

    for item in test_items:
        result = run_phase1_pipeline(item)

        print(f"Valuation report for {item}")

        if "error" in result:
            print(f"{result["error"]}")
        else:

            print(f" Listings Analyzed: {result["data_points"]}")
            print(f" Median sold price: ${result["median"]}")
            print(f" Price range = minimum: ${result["minimum"]} --- maximum: ${result["maximum"]}")
            print(f" Range spread: ${result["range"]}")


