import psycopg2
import datetime
import json


def main():
    data_dir = "/Users/tableau/Documents/techInAsia/data/"

    try:
        conn = psycopg2.connect("dbname = dev_techinasia user = tableau host = localhost")
        print("Successfully connected to techinasia database")
    except:
        print("FAILBLOG: connection to database failed")

    ProcessStartups(conn, data_dir)

def ProcessStartups(conn, data_dir):

    # load up startups
    with open(data_dir + "company_pages.json","rb") as f:
        startup_json = json.load(f)

    with open(data_dir + "investor_pages.json", "rb") as f:
        investor_json = json.load(f)

    print ("Processing Startup Information for " + str(len(startup_json)) + " companies")

    company_inserts = []
    stage_inserts = []
    investorfunds = []
    investor_insert = []
    industries = []
    all_stages = []

    for company in [i for i in startup_json if i]:
        profile = {}

        profile["CompanyName"] = company["name"]
        profile["tiaCompanyID"] = company["id"]
        profile["tiaURL"] = company["entity"]["slug"]
        profile["Country"] = [loc["country"]["name"] for loc in company["entity"]["locations"] if loc["type"] == "hq"][0] if [loc["country"] for loc in company["entity"]["locations"] if loc["type"] == "hq"] else ""
        profile["FoundedDate"] = datetime.datetime.strptime(company["date_founded"],"%Y-%m-%d") if company["date_founded"] and company["date_founded"] != "0000-00-00" else None

        company_inserts.append(profile)

        # build out funding stages
        for stage in company["funding_stages"]:
            full_stage = {}

            full_stage["tiaFundingStageID"] = stage["id"]
            full_stage["tiaCompanyID"] = stage["company_id"]
            full_stage["stageName"] = stage["stage"]["name"]
            full_stage["amount"] = stage["amount"]

            all_stages.append(full_stage)

            for fround in stage["rounds"]:
                funding_stage = {}
                funding_stage["amount"] = fround["amount"]
                funding_stage["tiaFundingStageID"] = fround["stage_id"]
                funding_stage["tiaFundingRoundID"] = fround["id"]
                funding_stage["tiaCompanyID"] = stage["company_id"]
                funding_stage["stageName"] = stage["stage"]["name"]
                funding_stage["dateClosed"] = datetime.datetime.strptime(fround["date_ended"],"%Y-%m-%d") if fround["date_ended"] and fround["date_ended"] != "0000-00-00" else None

                stage_inserts.append(funding_stage)

                for investor in fround["participants"]:
                    investor_fund_data = {}

                    investor_fund_data["tiaInvestorID"] = investor["investor"]["id"]
                    investor_fund_data["tiaFundingStageID"] = fround["stage_id"]
                    investor_fund_data["tiaFundingRoundID"] = fround["id"]
                    investor_fund_data["tiaURL"] = "companies/" + investor["investor"]["slug"]

                    investorfunds.append(investor_fund_data)

        for industry in company["entity"]["industries"]:
            industry_data = {}

            industry_data["tiaCompanyID"] = company["id"]
            industry_data["industryName"] = industry["name"]
            industry_data["industryID"] = industry["id"]

            industries.append(industry_data)

    for investor in investor_json:

        investor_profile = {}

        investor_profile["InvestorName"] = investor["name"]
        investor_profile["tiaInvestorID"] = investor["entity"]["id"]
        investor_profile["InvestorType"] = investor["entity"]["taxonomies"][0]["name"] if investor["entity"]["taxonomies"] else ''
        investor_profile["InvestorLocation"] = [loc["country"]["name"] for loc in investor["entity"]["locations"] if loc["type"] == "hq"][0] if [loc["country"] for loc in investor["entity"]["locations"] if loc["type"] == "hq"] else ""

        investor_insert.append(investor_profile)

    print("Inserting Data")

    print("THERE ARE THIS MANY FUNDING STAGES")

    CreateTables(conn)
    InsertStartupData(conn, company_inserts)
    InsertInvestorsToFundingStages(conn, investorfunds)
    InsertFundingStages(conn, all_stages)
    InsertFundingRounds(conn, stage_inserts)
    InsertInvestors(conn,investor_insert)
    InsertIndustries(conn, industries)

    print("Done With Inserts, Closing Connection")

    conn.close()

def CreateTables(conn):

    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS StartUps;
        DROP TABLE IF EXISTS Investors;
        DROP TABLE IF EXISTS FundingStages;
        DROP TABLE IF EXISTS FundingRounds;
        DROP TABLE IF EXISTS InvestorToFundingStage;
        DROP TABLE IF EXISTS Industries;
    """)
    conn.commit()

    cur.execute("""
        CREATE TABLE StartUps
        (
        RGAStartupID SERIAL PRIMARY KEY NOT NULL
        ,tiaCompanyID TEXT NOT NULL
        ,CompanyName TEXT NULL
        ,Country TEXT NULL
        ,tiaURL TEXT  NULL
        ,FoundedDate DATE NULL
        );
    """)

    conn.commit()

    cur.execute("""
        CREATE TABLE FundingRounds
        (
            RGAFundingRoundID SERIAL PRIMARY KEY NOT NULL
            ,tiaFundingStageID TEXT NOT NULL
            ,tiaFundingRoundID TEXT NOT NULL
            ,amount BIGINT NULL
            ,tiaCompanyID TEXT NULL
            ,stageName TEXT NULL
            ,dateClosed DATE NULL
        )
    """)

    conn.commit()

    cur.execute("""
        CREATE TABLE FundingStages
        (
            RGAFundingStageID SERIAL PRIMARY KEY NOT NULL
            ,tiaFundingStageID TEXT NOT NULL
            ,tiaCompanyID TEXT NOT NULL
            ,amount BIGINT NULL
            ,stageName TEXT NULL
        )
    """)

    conn.commit()

    cur.execute("""
        CREATE TABLE Investors
        (
            RGAInvestorID SERIAL PRIMARY KEY NOT NULL
            ,tiaInvestorID TEXT NOT NULL
            ,InvestorName TEXT NULL
            ,InvestorType TEXT NULL
            ,InvestorLocation TEXT NULL
        )
    """)

    conn.commit()


    cur.execute("""
        CREATE TABLE InvestorToFundingStage
        (
            RGAInvestorToFundingStageID SERIAL PRIMARY KEY NOT NULL
            ,tiaInvestorId TEXT NOT NULL
            ,tiaFundingStageID TEXT NOT NULL
            ,tiaFundingRoundID TEXT NOT NULL
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

    conn.commit()

def InsertStartupData(conn,company_inserts):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO StartUps
    (
        tiaCompanyID
        ,CompanyName
        ,Country
        ,tiaURL
        ,FoundedDate
    )
    VALUES
    (
        %(tiaCompanyID)s
        ,%(CompanyName)s
        ,%(Country)s
        ,%(tiaURL)s
        ,%(FoundedDate)s
    );
    """, company_inserts)

    conn.commit()

def InsertFundingRounds(conn, stage_inserts):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO FundingRounds
    (
        tiaFundingStageID
        ,amount
        ,tiaCompanyID
        ,stageName
        ,dateClosed
        ,tiaFundingRoundID
    )
    SELECT
        %(tiaFundingStageID)s
        ,%(amount)s
        ,%(tiaCompanyID)s
        ,%(stageName)s
        ,%(dateClosed)s
        ,%(tiaFundingRoundID)s
    WHERE NOT EXISTS
        (SELECT 1 FROM FundingRounds
        WHERE tiaFundingStageID = %(tiaFundingStageID)s
        AND tiaFundingRoundID = %(tiaFundingRoundID)s)

    """, stage_inserts)


    conn.commit()
    print("    -> inserted FundingStages data")

def InsertFundingStages(conn, stage_inserts):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO FundingStages
    (
        tiaFundingStageID
        ,amount
        ,tiaCompanyID
        ,stageName
    )
    SELECT
        %(tiaFundingStageID)s
        ,%(amount)s
        ,%(tiaCompanyID)s
        ,%(stageName)s
        WHERE NOT EXISTS
        (SELECT 1 FROM FundingStages
        WHERE tiaFundingStageID = %(tiaFundingStageID)s
        )

    """, stage_inserts)


    conn.commit()
    print("    -> inserted FundingStages data")


def InsertInvestorsToFundingStages(conn, investorfunds):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO InvestorToFundingStage
    (
        tiaFundingStageID
        ,tiaInvestorID
        ,tiaFundingRoundID
    )
    SELECT
        %(tiaFundingStageID)s
        ,%(tiaInvestorID)s
        ,%(tiaFundingRoundID)s
    WHERE NOT EXISTS
        (SELECT 1 FROM InvestorToFundingStage
        WHERE tiaInvestorID = %(tiaInvestorID)s
        AND tiaFundingRoundID = %(tiaFundingRoundID)s)

    """, investorfunds)

    conn.commit()
    print("    -> inserted InvestorsToFundingStages data")

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

def InsertInvestors(conn, investor_insert):

    cur = conn.cursor()

    cur.executemany("""
    INSERT INTO Investors
    (
        tiaInvestorID
        ,InvestorName
        ,InvestorType
        ,InvestorLocation
    )
    SELECT
        %(tiaInvestorID)s
        ,%(InvestorName)s
        ,%(InvestorType)s
        ,%(InvestorLocation)s
    WHERE NOT EXISTS
        (SELECT 1 FROM Investors
        WHERE tiaInvestorID = %(tiaInvestorID)s
        )
    """, investor_insert)

    conn.commit()
    print("    -> inserted Investors data")


if __name__ == '__main__':
    main()
