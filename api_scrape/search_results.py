import requests
import psycopg2
import datetime

# imports set variables in separate file
import api_vars

def main():

    r = requests.get(api_vars.search_startups(1,100))
    data = r.json()["data"]
    print("received " + str(len(data))+ " companies")
    slugs = []
    companies = []
    investors = []
    stages = []
    investorfunds = []
    industries = []

    # construct company objects for database insertion
    for company in data:
        search_results = {}
        search_results["CompanyName"] = company["company"]["name"]
        search_results["tiaCompanyID"] = company["company"]["id"]
        search_results["tiaURL"] = "companies/" + company["entity"]["slug"]
        search_results["Country"] = company["country"]["name"]
        search_results["LatestFundingDate"] = datetime.datetime.strptime(company["funding_round"]["date"],"%Y-%m-%d")
        search_results["LatestFundingAmount"] = int(company["funding_round"]["amount"])
        search_results["FundingStage"] = company["stage"]["name"]

        slugs.append(search_results)

    # now we get use tiaURLS to get funding data for each startup
    for company in slugs:
        company_profile = {}

        print("......processing " + company["CompanyName"])

        r = requests.get(api_vars.startup + company["tiaURL"])
        company_data = r.json()

        company_profile["CompanyName"] = company_data["name"]
        company_profile["tiaCompanyID"] = company_data["id"]
        company_profile["Country"] = company["Country"]
        company_profile["tiaURL"] = "companies/" + company_data["entity"]["slug"]
        company_profile["LatestFundingAmount"] = int(company["LatestFundingAmount"])
        company_profile["LatestFundingDate"] = company["LatestFundingDate"]
        company_profile["FundingStage"] = company["FundingStage"]
        company_profile["FoundedDate"] = datetime.datetime.strptime(company_data["date_founded"],"%Y-%m-%d")
        companies.append(company_profile)

        # build out funding stages
        for stage in company_data["funding_stages"]:
            funding_stage = {}

            for fround in stage["rounds"]:

                funding_stage["amount"] = fround["amount"]
                funding_stage["tiaFundingStageID"] = stage["id"]
                funding_stage["tiaFundingRoundID"] = fround["id"]
                funding_stage["tiaCompanyID"] = stage["company_id"]
                funding_stage["stageName"] = stage["stage"]["name"]
                funding_stage["dateClosed"] = datetime.datetime.strptime(fround["date_ended"],"%Y-%m-%d")

                stages.append(funding_stage)

                for investor in fround["participants"]:
                    investor_fund_data = {}

                    investor_fund_data["tiaInvestorID"] = investor["investor"]["id"]
                    investor_fund_data["tiaFundingStageID"] = stage["id"]
                    investor_fund_data["tiaURL"] = "companies/" + investor["investor"]["slug"]

                    investorfunds.append(investor_fund_data)

        for industry in company_data["entity"]["industries"]:
            industry_data = {}

            industry_data["tiaCompanyID"] = company_data["id"]
            industry_data["industryName"] = industry["name"]
            industry_data["industryID"] = industry["id"]

            industries.append(industry_data)

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

        print("......processing " + investor_response["name"])

        investor_data["InvestorName"] = investor_response["name"]
        investor_data["tiaInvestorID"] = investor_response["entity"]["id"]
        investor_data["InvestorType"] = investor_response["entity"]["taxonomies"][0]["name"] if investor_response["entity"]["taxonomies"] else ''
        investor_data["InvestorLocation"] = location

        investors.append(investor_data)

    ## Here to the end we run our database work
    try:
        conn = psycopg2.connect("dbname = dev_techinasia user = michaelhi host = localhost")
        print("Successfully connected to techinasia database")
    except:
        print("FAILBLOG: connection to database failed")

    createTables(conn)

    print("Inserting Data")

    InsertStartupData(conn, companies)
    InsertInvestorsToFundingStages(conn, investorfunds)
    InsertFundingStages(conn, stages)
    InsertInvestors(conn,investors)
    InsertIndustries(conn, industries)

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
        DROP TABLE IF EXISTS Industries;
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
        ,CompanyName TEXT NULL
        ,Country TEXT NULL
        ,tiaURL TEXT  NULL
        ,LatestFundingDate DATE NULL
        ,LatestFundingAmount INT NULL
        ,FundingStage TEXT NULL
        ,FoundedDate DATE NULL
        );
    """)

    conn.commit()
    print("    -> Startup Table Created in Postgres")

    cur.execute("""
        CREATE TABLE Investors
        (
            tiaInvestorID TEXT PRIMARY KEY NOT NULL
            ,InvestorName TEXT NULL
            ,InvestorType TEXT NULL
            ,InvestorLocation TEXT NULL
        )
    """)

    conn.commit()
    print("    -> Investor Table Created in Postgres")

    cur.execute("""
        CREATE TABLE FundingStages
        (
            tiaFundingStageID TEXT NOT NULL
            ,tiaFundingRoundID TEXT NOT NULL
            ,amount INT NULL
            ,tiaCompanyID TEXT NULL
            ,stageName TEXT NULL
            ,dateClosed DATE NULL
            ,PRIMARY KEY(tiaFundingStageID, tiaFundingRoundID)
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

    cur.execute("""
        CREATE TABLE Industries
        (
            tiaCompanyID TEXT NOT NULL
            ,industryID TEXT NOT NULL
            ,industryName TEXT NULL
            ,PRIMARY KEY(tiaCompanyID, industryID)
        )
    """)

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
        ,FoundedDate
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
        ,%(FoundedDate)s
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
        ,tiaFundingRoundID
    )
    VALUES
    (
        %(tiaFundingStageID)s
        ,%(amount)s
        ,%(tiaCompanyID)s
        ,%(stageName)s
        ,%(dateClosed)s
        ,%(tiaFundingRoundID)s
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
        investor["tiaFundingStageID"] + "' AND tiaInvestorID = """ + "'" + investor["tiaInvestorID"]
        + "');"
        )

    conn.commit()
    print("    -> inserted InvestorsToFundingStages data")


def InsertInvestors(conn, investors):

    cur = conn.cursor()
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

def InsertIndustries(conn, industries):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO Industries
    (
        tiaCompanyID
        ,industryID
        ,industryName
    )
    VALUES
    (
        %(tiaCompanyID)s
        ,%(industryID)s
        ,%(industryName)s
    );
    """, industries)

    conn.commit()
    print("    -> inserted Industry data")

if __name__ == '__main__':
    main()
