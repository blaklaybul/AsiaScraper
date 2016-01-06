import json
import requests
import psycopg2
import sys
import datetime

# imports set variables in separate file
import api_vars

def main():

    r = requests.get(api_vars.search_startups)
    data = r.json()["data"]
    print("received " + str(len(data))+ " companies")
    companies = []
    investors = []
    stages = []

    # construct company objects for database insertion
    for company in data:
        search_results = {}
        search_results["CompanyName"] = company["company"]["name"]
        search_results["tiaID"] = company["company"]["id"]
        search_results["Country"] = company["country"]["name"]
        search_results["tiaURL"] = "companies/" + company["entity"]["slug"]
        search_results["LatestFundingDate"] = datetime.datetime.strptime(company["funding_round"]["date"],"%Y-%m-%d")
        search_results["LatestFundingAmount"] = int(company["funding_round"]["amount"])
        search_results["FundingStage"] = company["stage"]["name"]
        companies.append(search_results)

    # now we get use tiaURLS to get funding data for each startup
    for company in companies:
        funding_info = {}
        investor_info = {}

        r = requests.get(api_vars.startup + company["tiaURL"])
        company_data = r.json()

        # build out funding stages
        for stage in company["funding_stages"]:
            funding_stage = {}
            investor_data = {}

            funding_stage["amount"] = stage["amount"]
            funding_stage["fundingstageID"] = stage["id"]
            funding_stage["tiaID"] = stage["company_id"]
            funding_stage["stageName"] = stage["stage"]["name"]
            funding_stage["dateEnded"] = stage["rounds"][0]["date_ended"]

            stages.append(funding_stage)

            investor_data

        # build out investors

        # build out fundingstagestoinvestors
        # build out fundingstagestostartups


    ## Here to the end we run our database work
    try:
        conn = psycopg2.connect("dbname = 'techinasia' user = 'michaelhi' host = 'localhost'")
        print("Successfully connected to techinasia database")
    except:
        print("FAILBLOG: connection to database failed")

    createTables(conn)
    InsertStartupData(conn, companies)


    conn.close()


def createTables(conn):

    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS StartUps;
        DROP TABLE IF EXISTS Investors;
        DROP TABLE IF EXISTS Stage;
        DROP TABLE IF EXISTS StartUpToStage;
        DROP TABLE IF EXISTS InvestorToStage
    """
    )

    conn.commit()

    cur.execute("""
    CREATE TABLE StartUps
    (
    tiaID TEXT PRIMARY KEY NOT NULL
    ,CompanyName TEXT NOT NULL
    ,Country TEXT NULL
    ,tiaURL TEXT NOT NULL
    ,LatestFundingDate DATE NULL
    ,LatestFundingAmount INT NULL
    ,FundingStage TEXT NULL
    ,DateFounded DATE NULL
    );
    """)

    curr.execute("""
    CREATE TABLE Investors
    (

    )
    """)

    conn.commit()
    print("Startup Table Created in Postgres")

def InsertStartupData(conn, companies):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO StartUps
    (
        tiaID
        ,CompanyName
        ,Country
        ,tiaURL
        ,LatestFundingDate
        ,LatestFundingAmount
        ,FundingStage
    )
    VALUES
    (
        %(tiaID)s
        ,%(CompanyName)s
        ,%(Country)s
        ,%(tiaURL)s
        ,%(LatestFundingDate)s
        ,%(LatestFundingAmount)s
        ,%(FundingStage)s
    );
    """, companies)

    conn.commit()

    print("inserted startup data")

if __name__ == '__main__':
    main()
