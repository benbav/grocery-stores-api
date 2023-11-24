import requests
import re
import json
import html


def target_api(query, zipcode, limit=3):
    def get_store_id(zipcode):
        params = {
            "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
            "zipcode": zipcode,
        }

        response = requests.get(
            "https://api.target.com/location_fulfillment_aggregations/v1/preferred_stores",
            params=params,
        )

        address = response.json()["preferred_stores"][0]["location_names"][0]["name"]
        store_id = response.json()["preferred_stores"][0]["location_id"]
        return store_id, address

    def get_visitor_id():
        r = requests.get("https://www.target.com/s").text
        pattern = r'visitor_id\\":\\"([A-F0-9]+)'

        # Use re.search to find the match
        match = re.search(pattern, r)

        # Check if a match was found
        if match:
            visitor_id = match.group(1)  # Get the ID from the first capturing group
            return visitor_id

    store_id, address = get_store_id(zipcode)
    visitor_id = get_visitor_id()

    headers = {
        "authority": "redsky.target.com",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.7",
        "dnt": "1",
        "origin": "https://www.target.com",
        "referer": "https://www.target.com/",
        "sec-ch-ua": '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    }

    params = {
        "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
        "channel": "WEB",
        "count": "24",
        "default_purchasability_filter": "true",
        "include_sponsored": "true",
        "keyword": f"{query}",
        "new_search": "true",
        "offset": "0",
        "page": f"/s/{query}",
        "platform": "desktop",
        "pricing_store_id": f"{store_id}",
        "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "visitor_id": f"{visitor_id}",
        "zip": f"{zipcode}",
    }

    response = requests.get(
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2",
        params=params,
        headers=headers,
    )

    # print(response.json())
    output_dict = {}

    # Extract and organize data from the response
    for i in range(min(limit, len(response.json()["data"]["search"]["products"]))):
        item = response.json()["data"]["search"]["products"][i]
        key = f"item_{i + 1}"
        item_info = {
            "name": html.unescape(item["item"]["product_description"]["title"]),
            "price": item["price"]["reg_retail"],
            "picture": item["item"]["enrichment"]["images"]["primary_image_url"],
        }
        output_dict[key] = item_info

    # Sort the dictionary by the price
    sorted_dict = {k: v for k, v in sorted(output_dict.items(), key=lambda item: item[1]["price"])}

    # simulate error for testing
    # return None, address
    return json.dumps(sorted_dict), address


# target_dict, address = target_api("fig bars", "60613", limit=3)
# print(target_dict, address)

# target_api("fig bars", "60613", limit=3)

# maybe ip got blocked?
