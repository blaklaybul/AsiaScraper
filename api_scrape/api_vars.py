def search_startups(page,count):
    url = "https://www.techinasia.com/api/2.0/startups/?page=" + str(page) + "&per_page="+ str(count)
    return url

def search_investors(page,count):
    url = "https://www.techinasia.com/api/2.0/investors/?page=" + str(page) + "&per_page="+ str(count)
    return url

startup = "https://www.techinasia.com/api/2.0/companies/"

def investor_portfolios_url(slug):
    url = "https://www.techinasia.com/api/2.0/investors/" + slug + "/portfolio/?per_page=999&sort=company_name"
    return url

def investor_coinvestor_url(slug):
    url = "https://www.techinasia.com/api/2.0/investors/" + slug + "/co-investors/?per_page=999&sort=company_name"
    return url
