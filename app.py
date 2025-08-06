from flask import Flask, render_template, request

import requests
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
import logging
from urllib.parse import quote_plus




def pretty_print_specs(specs_dict):
    for group, specs in specs_dict.items():
        print(f"\n{group}:")
        for key, value in specs.items():
            print(f"  {key}: {value}")

# Assuming your specs dictionary is named 'specs'

def extract_all_specifications_with_groups(html_soup, group_div_class='GNDEQ-', group_name_class='_4BJ2V+', table_class='_0ZhAN9', tr_class='WJdYP6 row'):
    specs = {}
    # Find all group section divs
    for group_div in html_soup.find_all('div', class_=lambda x: x and group_div_class in x):
        # Group name
        group_name_div = group_div.find('div', class_=lambda x: x and group_name_class in x)
        group_name = group_name_div.get_text(strip=True) if group_name_div else "Unknown"

        # Find the table in this group
        table = group_div.find('table', class_=lambda x: x and table_class in x)
        if not table:
            continue

        group_specs = {}
        # Each row in the table
        for row in table.find_all('tr', class_=lambda x: x and tr_class in x):
            cols = row.find_all('td')
            if len(cols) == 2:
                label = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                group_specs[label] = value
        if group_specs:
            specs[group_name] = group_specs
    return specs


app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template("index.html", title="Hello")


@app.route("/", methods = ['GET','POST'])
def devPage() :
    return render_template("web_scrap_input.html", title = "Calculator Page")

# @app.route("/calc", methods = ['GET','POST'])
# def calculate() :
#     if(request.method == 'POST') :
#         ops = request.form['operation']
#         num1 = request.form['num1']
#         num2 = request.form['num2']

#         num1 = float(num1)
#         num2 = float(num2)

#         if(ops == 'add') :
#             result = num1 + num2
#         elif(ops == 'sub') :
#             result = num1 - num2
#         elif(ops == 'mul') :
#             result = num1 * num2
#         else :
#             result = num1 / num2    

#     return render_template("result.html", value=result)






@app.route('/web-scrap-input', methods=['POST'])
def getSpecs():
    if request.method == "POST":  # The route only accepts POST, but good to check
        var = request.form.get('query')
        varToSearch= quote_plus(var)
        noOfProducts = 1  # You hardcoded 1, could be extended to accept form input

        flipkartUrl = "https://www.flipkart.com"
        url = f"{flipkartUrl}/search?q={varToSearch}"

        print('url', url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
        }

        req = Request(url, headers=headers)

        try:
            response = urlopen(req)
            flipkartPage = response.read()
            print("Page fetched successfully!")
        except Exception as e:
            # If failure fetching search page, immediately render error result
            print(f"Error fetching Flipkart search page: {e}")
            result = {
                'name': 'Error',
                'price': '',
                'specs': {},
                'error': f"Error fetching or parsing product page: {e}"
            }
            return render_template("web_scrap_output.html", result=result)

        flipkartFormattedHtml = bs(flipkartPage, 'html.parser')

        # Find all product containers on the search results page
        listOfAllItems = flipkartFormattedHtml.find_all("div", {"class": "cPHDOP col-12-12"})
        count = 0       # Tracks how many product links have been processed
        skipped = 0     # Tracks how many product links skipped initially (you skip first 2)

        # Initialize variables to later pass to the template (in case of failure)
        nameOfItem = None
        priceOfItem = None
        specs = {}

        for phone in listOfAllItems:
            a_tag = phone.find('a', href=True)
            if a_tag:
                if skipped < 2:
                    skipped += 1
                    continue  # Skip first 2 links as per your logic

                individualProduct = flipkartUrl + a_tag['href']
                count += 1

                res = Request(individualProduct, headers=headers)
                try:
                    response = urlopen(res)
                    flipkartPage = response.read()
                    flipkartFormattedHtmlOfItem = bs(flipkartPage, 'html.parser')

                    nameOfItem = flipkartFormattedHtmlOfItem.find("span", {"class": "VU-ZEz"})
                    priceOfItem = flipkartFormattedHtmlOfItem.find("div", {"class": "yRaY8j"})

                    # Extract the specifications dictionary using your helper function
                    specs = extract_all_specifications_with_groups(flipkartFormattedHtmlOfItem)

                    # Stop loop after processing the required number of products
                    if count == noOfProducts:
                        break

                except Exception as e:
                    # On exception during individual product fetch/parse,
                    # record error specs and break, so the user is informed
                    print(f"Error fetching or parsing product page: {e}")
                    nameOfItem = None
                    priceOfItem = None
                    specs = {'Error': {'Message': str(e)}}
                    break
            else:
                print("No <a> tag found in div")
                continue  # Just continue to next if <a> not found

        # Prepare the result dictionary to send to template
        # Use safe fallback empty strings or empty dicts if data is missing
        result = {
            'name': nameOfItem.text.strip() if nameOfItem else "Product name not found",
            'price': priceOfItem.text.strip() if priceOfItem else "Price not found",
            'specs': specs
        }

        # Render the HTML page with scraped results
        return render_template("web_scrap_output.html", result=result)

    # Although this route accepts only POST, it's good practice to handle other methods gracefully
    return render_template("web_scrap_output.html", result=None)

