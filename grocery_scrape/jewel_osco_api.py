import requests
import json
import random
import html


def get_request_id():
    data = {
        "checksum": "1640249083",
        "_rand": "lrvnwar",
        "rid": "r310947",
        "d": '{"INQ":{"siteID":10006484,"custID":"-6153494727971827858","scheduleTZs":{}}}',
    }

    response = requests.post("https://albertsons.inq.com/tagserver/init/initFramework", data=data)

    r = response.json()["INQ"]["serverTime"][0:7]

    first_chunk = random.randint(100, 999)
    second_chunk = r
    third_chunk = random.randint(100000000, 999999999)

    request_id = int(str(first_chunk) + str(second_chunk) + str(third_chunk))

    return request_id


def get_store_id(zipcode):
    headers = {
        "authority": "local.jewelosco.com",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.6",
        "dnt": "1",
        "referer": "https://local.jewelosco.com/search.html?q=60613&qp=60613&storetype=5655&storetype=5655&l=en",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    params = {
        "q": f"{zipcode}",
        "qp": f"{zipcode}",
        "storetype": [
            "5655",
            "5655",
        ],
        "l": "en",
    }

    response = requests.get("https://local.jewelosco.com/locator", params=params, headers=headers)

    distance = response.json()["response"]["entities"][0]["distance"]["distanceMiles"]
    closest_store_id = response.json()["response"]["entities"][0]["distance"]["id"]
    store_address = response.json()["response"]["entities"][0]["profile"]["address"]["line1"]
    return closest_store_id, store_address


def jewel_osco_api(query, zipcode, limit=3):
    # format query with % for spaces
    formatted_query = "%20".join(query.split())

    store_id, store_address = get_store_id(zipcode=zipcode)
    request_id = get_request_id()

    headers = {
        f"authority": "www.jewelosco.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "dnt": "1",
        "ocp-apim-subscription-key": "5e790236c84e46338f4290aa1050cdd4",  # lol its a constant
        "referer": "https://www.jewelosco.com/shop/search-results.html?q={formatted_query}",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    response = requests.get(
        f"https://www.jewelosco.com/abs/pub/xapi/pgmsearch/v1/search/products?request-id={request_id}&url=https://www.jewelosco.com&pageurl=https://www.jewelosco.com&pagename=search&rows=30&start=0&search-type=keyword&storeid={store_id}&featured=true&search-uid=uid%253D6696364499362%253Av%253D12.0%253Ats%253D1696961074175%253Ahc%253D11&q={formatted_query}&sort=&featuredsessionid=&screenwidth=149&dvid=web-4.1search&channel=pickup&banner=jewelosco",
        headers=headers,
    )

    output_dict = {}

    # Extract and organize data from the response
    for i in range(min(limit, len(response.json()["primaryProducts"]["response"]["docs"]))):
        item = response.json()["primaryProducts"]["response"]["docs"][i]
        key = f"item_{i + 1}"
        item_info = {
            "status": item["status"],
            "name": html.unescape(item["name"]),
            "price": item["price"],
            "picture": item["imageUrl"],
        }
        output_dict[key] = item_info

    # Sort the dictionary by the price
    sorted_dict = {k: v for k, v in sorted(output_dict.items(), key=lambda item: item[1]["price"])}

    return json.dumps(sorted_dict), store_address


# example usage
# dict, address = jewel_osco_api("banana", 60657)
# print(dict)
