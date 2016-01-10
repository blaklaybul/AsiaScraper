import json
import requests

import api_vars

def main():
    r = requests.get(api_vars.search_investors(page=1, count=1))
    how_many = r.json()["total"]

    r = requests.get(api_vars.search_investors(page=1, count=how_many))
    data = r.json()["data"]

    for investor in data:
        investor["scraped"] = 0

    print("received " + str(len(data))+ " investors")
    print("...saving to JSON File in data/ ")

    with open("data/investor_results.json","wb") as f:
        json.dump(data,f)

if __name__ == '__main__':
    main()
