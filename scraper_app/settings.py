BOT_NAME = "techinasia"
SPIDER_MODULES = ['scraper_app.spiders']
DATABASE = {
    "drivername" : "postgres",
    "host": "localhost",
    "port" : "5432",
    "username" : "michaelhi",
    "password" : "",
    "database" : "techinasia"
}
ITEM_PIPELINES = ['scraper_app.pipelines.TechInAsiaPipeline']
