import requests
import json
import csv
import html


def get_store_id(zipcode):
    with open("grocery_scrape/wf_store_ids.csv", mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["updated_address"].split(" ")[-1] == zipcode:
                return row["store_id"].split("|")[0], row["updated_address"]
            if row["updated_address"].split(" ")[-1][:4] == zipcode[:4]:
                return row["store_id"].split("|")[0], row["updated_address"]

    return None, None


def whole_foods_api(query, zipcode, limit=3):
    store_id, address = get_store_id(zipcode)
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.7",
        "Connection": "keep-alive",
        # 'Cookie': 'session-id=136-5467116-5911857; session-id-time=2082787201l; ubid-main=135-7881168-4712846; csm-sid=042-9637554-9119277; wfm_store_d8=eyJpZCI6IjEwMjAzIiwibmFtZSI6IkhhbHN0ZWQgYW5kIFdhdmVsYW5kIiwidGxjIjoiSEFMIiwicGF0aCI6Im5vcnRoYWxzdGVkIiwic3RhdGUiOiJJTCIsInN0b3JlX25pZCI6IiIsInN0YXJ0X2RhdGUiOiIyMDIzLTEwLTA3VDE1OjE1OjAxLjgwNFoiLCJ1cGRhdGVkX2RhdGUiOiIyMDIzLTEwLTA3VDE1OjE1OjAxLjgwNFoiLCJnZW9tZXRyeSI6eyJjb29yZGluYXRlcyI6Wy04Ny42NDk3MzQsNDEuOTQ4MzQ5XSwidHlwZSI6IlBvaW50In19; wfm_store_weak=eyJ2ZXJzaW9uIjoxLCJzdG9yZUlkIjoxMDIwMywiZ2VvQ29vcmRpbmF0ZSI6eyJsYXRpdHVkZSI6NDEuOTQ4MzQ5LCJsb25naXR1ZGUiOi04Ny42NDk3MzQsImFsdGl0dWRlTWV0ZXJzIjowLjB9fQ; session-token=KuQl/Qx9ePWnp9ifSer54V2Hf657aCsB805mdNG8dvmygszPpVkg1cEAUIWb6a6FOBGHGURRhnX+D3ncTI6u4C6JhEUem4liTQjEGm+9qNDQd5uA9LmuLtYPniC1Qfe1SamduwfT5Pp8LqyTODJ/CijXdtTZESARVrxKOlV1Q0b3a5kTKHfM+qbJlxPf4UyKLC+LvprC9+KYmtWDH0MiT+yMa4j35NmfougQbtTAwmZ/XoqVm3t+JIv0X4JB7bmCyNszkY/2biANXZpM0e8zW92V/z1jY0h2kMf5RMcoByI09AbDo2mVOY46g1kavsjzGXB+PrOPA2/AWPp6aIfLKQ==',
        "DNT": "1",
        "Referer": "https://www.wholefoodsmarket.com/stores",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }
    params = {
        "text": f"{query}",
        "store": f"{store_id}",
        "limit": "60",
        "offset": "0",
    }

    response = requests.get(
        "https://www.wholefoodsmarket.com/api/search",
        params=params,
        headers=headers,
    )
    output_dict = {}

    # Extract and organize data from the response
    for i in range(min(limit, len(response.json()["results"]))):
        item = response.json()["results"][i]
        key = f"item_{i + 1}"
        item_info = {
            "name": html.unescape(item["name"]),
            "price": item["regularPrice"],
            "picture": item["imageThumbnail"],
        }
        output_dict[key] = item_info

    # Sort the dictionary by the price
    sorted_dict = {k: v for k, v in sorted(output_dict.items(), key=lambda item: item[1]["price"])}

    return json.dumps(sorted_dict), address


# print(store_id, address)
# example usage
# wf_dict, address = whole_foods_api("apple", zipcode="28806")
# print(wf_dict, address)
