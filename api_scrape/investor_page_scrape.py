import json
import requests

import api_vars

def main():
    ''' to speed up execution, we will only dump json every 1000 companies, this
    can be changed'''

    period = 500
    counter = 0

    try:
        with open("data/investor_pages.json", "rb") as ff:
            investor_page_array = json.load(ff)
    except:
        investor_page_array = []

    print len(investor_page_array)

    # load the search_results to get investor slugs
    with open("data/investor_results.json", "rb") as f:
        driver = json.load(f)

    to_scrape = [i for i in driver if i and i["scraped"] == 0]
    number_of_companies = len(to_scrape)

    for i, investor in enumerate(to_scrape):
        print("#" + str(i) + " of " + str(number_of_companies) + " " + investor["entity"]["slug"])

        r = requests.get(api_vars.startup + investor["entity"]["slug"])
        investor_data = r.json()
        investor_page_array.append(investor_data)

        investor["scraped"] = 1

        #need to write the file when we hit the end
        if counter == 500 or i == len(to_scrape)-1:
            with open("data/investor_pages.json", "wb") as f:
                json.dump(investor_page_array,f)
            counter = 0
            with open("data/investor_results.json", "wb") as g:
                json.dump(driver, g)
        counter += 1

if __name__ == '__main__':
    main()
