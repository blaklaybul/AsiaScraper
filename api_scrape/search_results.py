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
    investorfunds = []

    # construct company objects for database insertion
    for company in data:
        search_results = {}
        search_results["CompanyName"] = company["company"]["name"]
        search_results["tiaCompanyID"] = company["company"]["id"]
        search_results["Country"] = company["country"]["name"]
        search_results["tiaURL"] = "companies/" + company["entity"]["slug"]
        search_results["LatestFundingDate"] = datetime.datetime.strptime(company["funding_round"]["date"],"%Y-%m-%d")
        search_results["LatestFundingAmount"] = int(company["funding_round"]["amount"])
        search_results["FundingStage"] = company["stage"]["name"]
        companies.append(search_results)

        ## !!! ADD INDUSTRIES

    # now we get use tiaURLS to get funding data for each startup
    for company in companies:
        funding_info = {}
        investor_to_fundingstage = {}

        print(company["CompanyName"])

        r = requests.get(api_vars.startup + company["tiaURL"])
        company_data = r.json()

        # build out funding stages
        for stage in company_data["funding_stages"]:
            funding_stage = {}

            funding_stage["amount"] = stage["rounds"][0]["amount"]
            funding_stage["tiaFundingStageID"] = stage["id"]
            funding_stage["tiaCompanyID"] = stage["company_id"]
            funding_stage["stageName"] = stage["stage"]["name"]
            funding_stage["dateClosed"] = stage["rounds"][0]["date_ended"]

            stages.append(funding_stage)

            for fround in stage["rounds"]:
                for investor in fround["participants"]:
                    investor_fund_data = {}

                    investor_fund_data["tiaInvestorID"] = investor["investor"]["id"]
                    investor_fund_data["tiaFundingStageID"] = stage["id"]
                    investor_fund_data["tiaURL"] = "companies/" + investor["investor"]["slug"]

                    investorfunds.append(investor_fund_data)

    # build out investors
    for investor in investorfunds:
        investor_data = {}
        location = ''

        r = requests.get(api_vars.startup + investor["tiaURL"])
        investor_response = r.json()

        if r.status_code != requests.codes.ok:
            continue

        for loc in investor_response["entity"]["locations"]:
            if loc["type"].lower() == "hq":
                location = loc["country"]["name"]

        print(investor_response["name"])

        investor_data["InvestorName"] = investor_response["name"]
        investor_data["tiaInvestorID"] = investor_response["id"]
        investor_data["InvestorType"] = investor_response["entity"]["taxonomies"][0]["name"] if investor_response["entity"]["taxonomies"] else ''
        investor_data["InvestorLocation"] = location

        investors.append(investor_data)
    ## Here to the end we run our database work
    try:
        conn = psycopg2.connect("dbname = 'techinasia' user = 'michaelhi' host = 'localhost'")
        print("Successfully connected to techinasia database")
    except:
        print("FAILBLOG: connection to database failed")


    createTables(conn)

    print("Inserting Data")

    InsertStartupData(conn, companies)
    InsertInvestorsToFundingStages(conn, investorfunds)
    InsertFundingStages(conn, stages)
    InsertInvestors(conn,investors)

    print("Done With Inserts, Closing Connection")

    conn.close()


def createTables(conn):

    print("Dropping tables if they exist")

    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS StartUps;
        DROP TABLE IF EXISTS Investors;
        DROP TABLE IF EXISTS FundingStages;
        DROP TABLE IF EXISTS InvestorToFundingStage;
    """
    )

    conn.commit()

    print("Tables Dropped")
    print("")
    print("Creating Tables")

    cur.execute("""
        CREATE TABLE StartUps
        (
        tiaCompanyID TEXT PRIMARY KEY NOT NULL
        ,CompanyName TEXT NOT NULL
        ,Country TEXT NULL
        ,tiaURL TEXT NOT NULL
        ,LatestFundingDate DATE NULL
        ,LatestFundingAmount INT NULL
        ,FundingStage TEXT NULL
        );
    """)

    conn.commit()
    print("    -> Startup Table Created in Postgres")

    cur.execute("""
        CREATE TABLE Investors
        (
            tiaInvestorID TEXT PRIMARY KEY NOT NULL
            ,InvestorName TEXT NOT NULL
            ,InvestorType TEXT NOT NULL
            ,InvestorLocation TEXT NOT NULL
        )
    """)

    conn.commit()
    print("    -> Investor Table Created in Postgres")

    cur.execute("""
        CREATE TABLE FundingStages
        (
            tiaFundingStageID TEXT PRIMARY KEY NOT NULL
            ,amount INT NOT NULL
            ,tiaCompanyID TEXT NOT NULL
            ,stageName TEXT NULL
            ,dateClosed DATE NULL
        )
    """)

    conn.commit()
    print("    -> FundingStages Table Created in Postgres")

    cur.execute("""
        CREATE TABLE InvestorToFundingStage
        (
            tiaInvestorId TEXT NOT NULL
            ,tiaFundingStageID TEXT NOT NULL
            ,PRIMARY KEY(tiaInvestorId, tiaFundingStageID)
        )
    """)

    conn.commit()
    print("    -> InvestorToFundingStage Table Created in Postgres")

def InsertStartupData(conn, companies):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO StartUps
    (
        tiaCompanyID
        ,CompanyName
        ,Country
        ,tiaURL
        ,LatestFundingDate
        ,LatestFundingAmount
        ,FundingStage
    )
    VALUES
    (
        %(tiaCompanyID)s
        ,%(CompanyName)s
        ,%(Country)s
        ,%(tiaURL)s
        ,%(LatestFundingDate)s
        ,%(LatestFundingAmount)s
        ,%(FundingStage)s
    );
    """, companies)

    conn.commit()

    print("    -> inserted startup data")

def InsertFundingStages(conn, stages):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO FundingStages
    (
        tiaFundingStageID
        ,amount
        ,tiaCompanyID
        ,stageName
        ,dateClosed
    )
    VALUES
    (
        %(tiaFundingStageID)s
        ,%(amount)s
        ,%(tiaCompanyID)s
        ,%(stageName)s
        ,%(dateClosed)s
    );
    """, stages)

    conn.commit()

    print("    -> inserted FundingStages data")

def InsertInvestorsToFundingStages(conn, investorfunds):

    cur = conn.cursor()

    for investor in investorfunds:

        cur.execute("""
        INSERT INTO InvestorToFundingStage
        (
            tiaFundingStageID
            ,tiaInvestorID
        )
        SELECT """ +
        "'" + investor["tiaFundingStageID"] + "'" +
        ",'" + investor["tiaInvestorID"] + "'" +
        """WHERE NOT EXISTS
        (SELECT 1 FROM InvestorToFundingStage WHERE tiaFundingStageID = """ + "'" +
        investor["tiaFundingStageID"] + "' AND tiaInvestorID = + """ + "'" + investor["tiaInvestorID"]
        + "');"
        )

    conn.commit()

    print("    -> inserted InvestorsToFundingStages data")


def InsertInvestors(conn, investors):

    cur = conn.cursor()

    print(investors)

    for investor in investors:

        cur.execute("""
        INSERT INTO Investors
        (
            tiaInvestorID
            ,InvestorName
            ,InvestorType
            ,InvestorLocation
        )
        SELECT """ +
            "'" + investor["tiaInvestorID"] + "'" +
            "," + "'" + investor["InvestorName"] + "'" +
            "," + "'" + investor["InvestorType"] + "'" +
            "," + "'" + investor["InvestorLocation"] + "'" +
        """WHERE NOT EXISTS
        (SELECT 1 FROM Investors WHERE tiaInvestorId = """ + "'" + investor["tiaInvestorID"] + "');"
        )

    conn.commit()

    print("    -> inserted Investors data")


if __name__ == '__main__':
    main()
