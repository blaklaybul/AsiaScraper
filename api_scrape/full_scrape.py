import pickle
import requests

import api_vars

# USE JSON EN/DECODER!

def main():

    current = 1
    end = 239
    while current < end:

        # get the pickle
        try:
            with open("search_results.tia") as f:
                company_dir = pickle.load(f)
        except:
            company_dir = []

        print("ON ITERATION " + str(current) + " OF " + str(end))

        data = search_results(current)

        print(len(company_dir))

        for company in data:
            company_dir.append(company)

        with open ("search_results.tia", "wb") as f:
            pickle.dump(company_dir,f, protocol = 2)

        current+=1

def search_results(page):
    '''taking 100 per page'''
    r = requests.get(api_vars.search_startups(page,100))
    data = r.json()["data"]
    return data

if __name__ == '__main__':
    main()
