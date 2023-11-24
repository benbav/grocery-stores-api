import requests
import json
import html


def get_store_id(zipcode):
    json_data = {
        "request": {
            "appkey": "8BC3433A-60FC-11E3-991D-B2EE0C70A832",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "limit": 2,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": zipcode,
                            "country": "US",
                            "latitude": "",
                            "longitude": "",
                        },
                    ],
                },
                "searchradius": "500",
                "where": {
                    "warehouse": {
                        "distinctfrom": "1",
                    },
                },
                "false": "0",
            },
        },
    }

    response = requests.post("https://alphaapi.brandify.com/rest/locatorsearch", json=json_data)

    store_id = response.json()["response"]["collection"][0]["clientkey"]
    address = response.json()["response"]["collection"][0]["address1"]
    return store_id, address


def trader_joes_api(query, zipcode, limit=3):
    store_id, address = get_store_id(zipcode)

    headers = {
        "authority": "www.traderjoes.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://www.traderjoes.com",
        "referer": "https://www.traderjoes.com/home/search?q=fig+bars&global=yes",
        "sec-ch-ua": '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    }

    graph_query = 'query SearchProducts($search: String, $pageSize: Int, $currentPage: Int, $storeCode: String = "701", $availability: String = "1", $published: String = "1") {\n  products(\n    search: $search\n    filter: {store_code: {eq: $storeCode}, published: {eq: $published}, availability: {match: $availability}}\n    pageSize: $pageSize\n    currentPage: $currentPage\n  ) {\n    items {\n      category_hierarchy {\n        id\n        url_key\n        description\n        name\n        position\n        level\n        created_at\n        updated_at\n        product_count\n        __typename\n      }\n      item_story_marketing\n      product_label\n      fun_tags\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      other_images\n      other_images_meta {\n        url\n        metadata\n        __typename\n      }\n      context_image\n      context_image_meta {\n        url\n        metadata\n        __typename\n      }\n      published\n      sku\n      url_key\n      name\n      item_description\n      item_title\n      item_characteristics\n      item_story_qil\n      use_and_demo\n      sales_size\n      sales_uom_code\n      sales_uom_description\n      country_of_origin\n      availability\n      new_product\n      promotion\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      nutrition {\n        display_sequence\n        panel_id\n        panel_title\n        serving_size\n        calories_per_serving\n        servings_per_container\n        details {\n          display_seq\n          nutritional_item\n          amount\n          percent_dv\n          __typename\n        }\n        __typename\n      }\n      ingredients {\n        display_sequence\n        ingredient\n        __typename\n      }\n      allergens {\n        display_sequence\n        ingredient\n        __typename\n      }\n      created_at\n      first_published_date\n      last_published_date\n      updated_at\n      related_products {\n        sku\n        item_title\n        primary_image\n        primary_image_meta {\n          url\n          metadata\n          __typename\n        }\n        price_range {\n          minimum_price {\n            final_price {\n              currency\n              value\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        retail_price\n        sales_size\n        sales_uom_description\n        category_hierarchy {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    total_count\n    page_info {\n      current_page\n      page_size\n      total_pages\n      __typename\n    }\n    __typename\n  }\n}\n'
    graph_query = graph_query.replace("701", store_id)

    json_data = {
        f"operationName": "SearchProducts",
        "variables": {
            "storeCode": f"{store_id}",
            "availability": "1",
            "published": "1",
            "search": f"{query}",
            "currentPage": 1,
            "pageSize": 15,
        },
        "query": graph_query,
    }

    response = requests.post("https://www.traderjoes.com/api/graphql", headers=headers, json=json_data)

    item_list = []
    for i in range(min(limit, len(response.json()["data"]["products"]["items"]))):
        item = response.json()["data"]["products"]["items"][i]
        item_info = {
            "name": html.unescape(item["name"]),
            "price": item["price_range"]["minimum_price"]["final_price"]["value"],
            "picture": "https://www.traderjoes.com" + str(item["context_image"])
            if item["context_image"]
            else None,
        }
        item_list.append(item_info)

    # Sort the items by price
    sorted_items = sorted(item_list, key=lambda x: x["price"])

    # Organize the sorted items into a dictionary
    output_dict = {}
    for i, item in enumerate(sorted_items):
        key = f"item_{i + 1}"
        output_dict[key] = item

    return json.dumps(output_dict), address

    # need to get the actual address and replace missing pictures with missing.png


# tj_dict, address = trader_joes_api("apple", zipcode="60613")
# print(tj_dict, address)
