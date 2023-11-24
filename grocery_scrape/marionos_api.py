import requests
import json
import re
import html


# get store id - helper function
def get_store_id(zipcode):
    headers = {
        "authority": "www.marianos.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://www.marianos.com",
        "sec-ch-ua": '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    }

    json_data = {
        "address": {
            "postalCode": zipcode,
        },
    }

    response = requests.post(
        "https://www.marianos.com/atlas/v1/modality/options", headers=headers, json=json_data
    )

    r = response.json()
    address = r["data"]["modalityOptions"]["storeDetails"][0]["address"]["address"]["addressLines"][0]
    locationId = r["data"]["modalityOptions"]["storeDetails"][0]["locationId"]
    storeNumber = r["data"]["modalityOptions"]["storeDetails"][0]["storeNumber"]
    return locationId, storeNumber, address


# get product upc codes for store - helper function
def get_product_codes(query, zipcode, limit):
    locationId, storeNumber, address = get_store_id(zipcode)

    x_laf = [
        {
            "modality": {
                "type": "PICKUP",
                "handoffLocation": {"storeId": locationId, "facilityId": storeNumber},
                "handoffAddress": {
                    "address": {
                        "addressLines": ["2021 W Chicago Ave"],
                        "cityTown": "CHICAGO",
                        "name": "Marianos Ukrainian Village",
                        "postalCode": "60622",
                        "stateProvince": "IL",
                        "residential": False,
                        "countryCode": "US",
                    },
                    "location": {"lat": 41.8955273, "lng": -87.6783442},
                },
            },
            "sources": [
                {"storeId": locationId, "facilityId": storeNumber},
                {"storeId": "540FC006", "facilityId": "90721"},
                {"storeId": "540DA006", "facilityId": "00000"},
            ],
        },
        {
            "modality": {
                "type": "SHIP",
                "handoffAddress": {
                    "address": {"postalCode": "60622"},
                    "location": {"lat": 41.90315247, "lng": -87.68141937},
                },
            },
            "sources": [
                {"storeId": "491DC001", "facilityId": "91"},
                {"storeId": "309DC309", "facilityId": "90618"},
                {"storeId": "310DC310", "facilityId": "90632"},
                {"storeId": "DSV00001", "facilityId": "00000"},
                {"storeId": "MKTPLACE", "facilityId": "00000"},
            ],
        },
    ]

    headers = {
        "authority": "www.marianos.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.6",
        "dnt": "1",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "x-laf-object": json.dumps(x_laf),
    }

    params = {
        "filter.query": query,
        "filter.fulfillmentMethods": [
            "IN_STORE",
        ],
    }

    response = requests.get(
        "https://www.marianos.com/atlas/v1/search/v1/products-search",
        params=params,
        headers=headers,
    )

    r = response.json()

    lst = []

    for i in range(min(limit, len(r["data"]["productsSearch"]))):
        lst.append(r["data"]["productsSearch"][i]["upc"])

    return lst


# main api function for marionos
def marianos_api(query, zipcode, limit=3):
    locationId, storeNumber, address = get_store_id(zipcode)

    prod_id_lst = get_product_codes(query, zipcode, limit)

    headers = {
        "authority": "www.marianos.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.6",
        "dnt": "1",
        "referer": "https://www.marianos.com/p/kroger-2-reduced-fat-milk/0001111041600?fulfillment=PICKUP&searchType=trending",
        "sec-ch-ua": '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "x-laf-object": '[{"modality":{"type":"PICKUP","handoffLocation":{"storeId":"53100503","facilityId":"00527"},"handoffAddress":{"address":{"addressLines":["333 E Benton Pl"],"cityTown":"CHICAGO","name":"Marianos Lakeshore East","postalCode":"60601","stateProvince":"IL","residential":false,"countryCode":"US"},"location":{"lat":41.8853187,"lng":-87.6182262}}},"sources":[{"storeId":"53100503","facilityId":"15096"}]},{"modality":{"type":"SHIP","handoffAddress":{"address":{"postalCode":"60601"},"location":{"lat":41.88581467,"lng":-87.62528992}}},"sources":[{"storeId":"491DC001","facilityId":"91"},{"storeId":"309DC309","facilityId":"90618"},{"storeId":"310DC310","facilityId":"90632"},{"storeId":"DSV00001","facilityId":"00000"},{"storeId":"MKTPLACE","facilityId":"00000"}]}]',
    }

    output_dict = {}

    i = 0
    for product in prod_id_lst:
        params = {
            "filter.gtin13s": product,
            "filter.verified": "true",
            "projections": "items.full,offers.compact,variantGroupings.compact",
        }

        response = requests.get(
            "https://www.marianos.com/atlas/v1/product/v2/products", params=params, headers=headers
        )
        r = response.json()

        item = r["data"]["products"][0]
        key = f"item_{i + 1}"

        item_info = {
            "name": html.unescape(item["item"]["description"]),
            "price": item["price"]["storePrices"]["regular"]["price"].replace("USD", "").strip(),
            "picture": item["item"]["images"][0]["url"],
        }
        output_dict[key] = item_info
        i += 1

    return json.dumps(output_dict), address


# example usage

# marionos_dict, address = marianos_api("fig strawberry", "60622", limit=1)
# print(marionos_dict, address)
