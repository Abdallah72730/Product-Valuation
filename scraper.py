import requests


def construct_ebay_url(item_name: str) -> str:
    searchquery = item_name.replace(" ", "+")

    url = f"https://www.ebay.ca/sch/i.html?_nkw={searchquery}&LH_Sold=1&LH_Complete=1"

    return url


def fetch_html_scraperapi (item_name: str) -> str:
    target_url = construct_ebay_url(item_name)

    encoded_target_url = requests.utils.quote(target_url, safe='')

    api_url = f"http://api.scraperapi.com/?api_key={API_KEYS}&url={encoded_target_url}&render=true"

    # params = {
    #     "api-key": API_KEYS,
    #     "url": target_url,
    #     "render": "true",
    #     "country_code": "ca"
    # }

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed. {e} ")
        return ""

if __name__ == "__main__":
    # print(construct_ebay_url("iphone 13"))

    html = fetch_html_scraperapi("python programming book")

    print(f"Got {len(html)} characters of Html")