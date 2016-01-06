from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose

from scraper_app.items import SearchResults

class TechInAsiaSpider(BaseSpider):
    name = "techinasia"
    allowed_domains = ["techinasia.com"]
    long_url = ("https://www.techinasia.com/startups?sort=-funding_round_"
        "amount&country_name[]=India&country_name[]=China&country_name[]=Samoa"
        "&country_name[]=Australia&country_name[]=Brunei%20Darussalam&country_"
        "name[]=Bangladesh&country_name[]=Cambodia&country_name[]=Hong%20Kong&"
        "country_name[]=Indonesia&country_name[]=Pakistan&country_name[]=Japan"
        "&country_name[]=Korea,%20Republic%20of&country_name[]=Korea,%20Democr"
        "atic%20People%27s%20Republic%20Of&country_name[]=Lao%20People%27s%20D"
        "emocratic%20Republic&country_name[]=Macao&country_name[]=Malaysia&cou"
        "ntry_name[]=Mongolia&country_name[]=Myanmar&country_name[]=New%20Zeal"
        "and&country_name[]=Papua%20New%20Guinea&country_name[]=Philippines&co"
        "untry_name[]=Singapore&country_name[]=Taiwan,%20Republic%20Of%20China"
        "&country_name[]=Thailand&country_name[]=Timor-Leste&country_name[]=Vi"
        "etnam&page="
    )

    start_urls = [long_url + str(page) for page in xrange(1,21)]

    startup_results_xpath = '//td/a[@class="datatable__link"]'
    item_fields = {
        "url": './/@href',
    }

    def parse(self, response):

        selector = HtmlXPathSelector(response)

        for startup in selector.select(self.startup_results_xpath):
            loader = XPathItemLoader(SearchResults(), selector = startup)

            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            for field, xpath in self.item_fields.iteritems():
                loader.add_xpath(field, xpath)
            yield loader.load_item()
