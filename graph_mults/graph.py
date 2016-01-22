import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import networkx

try:
    conn = psycopg2.connect("dbname = dev_techinasia user = michaelhi host = localhost")
    print "successful db connection!"
except:
    print "database connection failed, quitting program"
    sys.exit(0)


def main(industry):

    nodes = getNodes(industry)
    node_lookup = {
        v["name"]:{
            "name" : v["name"],
            "index" :  i
        }
        for i, v in enumerate(nodes)
    }

    old_links = getLinks(industry)
    links = [ {
    "source": node_lookup[link["source"]]["index"],
    "target": node_lookup[link["target"]]["index"],
    "value": link["value"]
    }
    for link in old_links]

    for_export = {
        "nodes" : nodes,
        "links" : links,
        "meta": {
            "industry" : industry
        }
    }

    with open("force_" + industry + ".json", "wb") as j:
        json.dump(for_export, j)

def getLinks(industry):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        select
            array_to_json(array_agg(row_to_json(j)))
        from(
            select
                tiacompanyid as target
                ,tiainvestorid as source
                ,count(*) as value
            from fundingstages f
            join investortofundingstage i
                on f.tiafundingstageid = i.tiafundingstageid
            where f.tiacompanyid in (
                select
                    tiacompanyid
                from industries
                where industryname = '"""
                + industry +
                """') group by tiacompanyid, tiainvestorid)j;
        """)
    links = cur.fetchall()[0]["array_to_json"]
    return links



def getNodes(industry):
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            select
                array_to_json(array_agg(row_to_json(j)))
            from(
                select distinct
                    f.tiacompanyid as name
                    , 1 as group
                    , s.country as location
                from fundingstages f
                join investortofundingstage i
                    on f.tiafundingstageid = i.tiafundingstageid
                left join startups s
                    on f.tiacompanyid = s.tiacompanyid
                where f.tiacompanyid in (
                    select
                        tiacompanyid
                    from industries
                    where industryname = '"""
                + industry +
                """')
                UNION ALL
                select distinct
                    i.tiainvestorid as name
                    , 2 as group
                    , ii.investorlocation as location
                from fundingstages f
                join investortofundingstage i
                    on f.tiafundingstageid = i.tiafundingstageid
                left join investors ii
                    on i.tiainvestorid = ii.tiainvestorid
                where f.tiacompanyid in (
                    select
                        tiacompanyid
                    from industries
                    where industryname = '"""
                + industry +
                """')
                )j;
            """)
        nodes = cur.fetchall()[0]["array_to_json"]
        return nodes

if __name__ == '__main__':
    industry = sys.argv[1]
    main(industry)
