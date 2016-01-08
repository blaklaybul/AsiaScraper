import json
import requests

import api_vars

def main():
    ''' to speed up execution, we will only dump json every 1000 companies, this
    can be changed'''

    period = 500
    counter = 0

    try:
        with open("company_pages.json", "rb") as ff:
            company_page_array = json.load(ff)
    except:
        company_page_array = []

    print len(company_page_array)

    # load the search_results to get company slugs
    with open("search_results.json", "rb") as f:
        driver = json.load(f)

    to_scrape = [i for i in driver if i and i["scraped"] == 0]
    number_of_companies = len(to_scrape)

    for i, company in enumerate(to_scrape):
        print("#" + str(i) + " of " + str(number_of_companies) + " " + company["entity"]["slug"])

        r = requests.get(api_vars.startup + company["entity"]["slug"])
        company_data = r.json()
        company_page_array.append(company_data)

        company["scraped"] = 1

        if counter == 500:
            with open("company_pages.json", "wb") as f:
                json.dump(company_page_array,f)
            counter = 0
            with open("search_results.json", "wb") as g:
                json.dump(driver, g)
        counter += 1

if __name__ == '__main__':
    main()
