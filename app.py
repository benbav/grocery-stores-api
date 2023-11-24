from flask import Flask, render_template, request, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from grocery_scrape.api import *
import json

app = Flask(__name__, static_url_path="/static")
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per day", "10 per hour"],
    storage_uri="memory://",
)


def safe_json_loads(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


@limiter.limit("5 per minute")
@app.route("/", methods=["GET", "POST"])
def index():
    grocery_stores = {
        "Whole Foods": whole_foods_api,  # works
        "Jewel-Osco": jewel_osco_api,  # works
        "Trader Joes ": trader_joes_api,  # works
        "Marionos": marianos_api,  # works
        "Target": target_api,  # ERROR
    }

    if request.method == "POST":
        zipcode = request.form["zipcode"]
        query = request.form["query"]
        selected_stores = request.form.getlist("selected_stores")  # make sure to limit to 4 on the html

        limit = 4
        results = {}
        error_results = {}

        for store_name in selected_stores:
            if store_name in grocery_stores:
                store_api = grocery_stores[store_name]
                try:
                    store_results, store_addr = store_api(query, zipcode, limit=limit)
                    key = f"{store_name}<br>{store_addr}"
                    results[key] = safe_json_loads(store_results)
                except Exception as e:
                    print(e)
                    # Handle the exception and add an error response to the error_results dictionary
                    error_key = f"{store_name}<br>{store_addr}"
                    error_results[error_key] = {
                        "item_1": {"name": "ERROR", "price": "ERROR", "picture": "ERROR"},
                        "item_2": {"name": "ERROR", "price": "ERROR", "picture": "ERROR"},
                        "item_3": {"name": "ERROR", "price": "ERROR", "picture": "ERROR"},
                    }

        results.update(error_results)
        # this redirects to the results page
        return redirect(url_for("results", zipcode=zipcode, results=json.dumps(results), query=query))

    # this loads the initial page
    return render_template("index.html", grocery_stores=grocery_stores)


@app.route("/results", methods=["GET"])
def results():
    zipcode = request.args.get("zipcode")
    query = request.args.get("query")
    results = json.loads(request.args.get("results"))

    print(results)

    return render_template(
        "results.html",
        zipcode=zipcode,
        query=query,
        results=results,
    )


# commentasdfdasfsdaf
x = 3

# draw a box around the store with the lowest price and item - yeah ill do that but just fucking format them first
# check box to limit up to 4 grocery stores DONE
# maybe add aldi api (later)
# then make it look super nice add noahs artwork and deploy
# noah wants to make a mock up of the landing page and the results page and then impliment DONE
# get it lined up on the grid FORMATTING
# get target api fixed DONE
# get the missing images fixed DONE

if __name__ == "__main__":
    app.run()
