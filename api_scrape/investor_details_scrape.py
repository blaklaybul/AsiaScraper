import json
import requests

import api_vars

def main():
    ''' to speed up execution, we will only dump json every 1000 companies, this
    can be changed'''

    period = 500
    counter = 0

    try:
        with open("data/investor_portfolios.json", "rb") as ff:
            investor_portfolio_array = json.load(ff)
    except:
        investor_portfolio_array = []

    try:
        with open("data/investor_coinv.json", "rb") as ff:
            investor_coinv_array = json.load(ff)
    except:
        investor_coinv_array = []

    # load the search_results to get investor slugs
    with open("data/investor_results.json", "rb") as f:
        driver = json.load(f)

    to_scrape = driver # change this to only get unscraped ones
    number_of_companies = len(to_scrape)

    for i, investor in enumerate(to_scrape):
        print("#" + str(i) + " of " + str(number_of_companies) + " " + investor["entity"]["slug"])

        r = requests.get(api_vars.investor_portfolios_url(investor["entity"]["slug"]))
        rr = requests.get(api_vars.investor_coinvestor_url(investor["entity"]["slug"]))

        investor_portfolio_data = r.json()
        investor_portfolio_array.append(investor_portfolio_data)

        investor_coinv_data = rr.json()
        investor_coinv_array.append(investor_coinv_data)


        # investor["scraped"] = 1

        #need to write the file when we hit the end
        if counter == period or i == len(to_scrape)-1:
            with open("data/investor_portfolios.json", "wb") as f:
                json.dump(investor_portfolio_array,f)

            with open("data/investor_coinv.json", "wb") as g:
                json.dump(investor_coinv_array, g)

            counter = 0

        counter += 1

if __name__ == '__main__':
    main()
