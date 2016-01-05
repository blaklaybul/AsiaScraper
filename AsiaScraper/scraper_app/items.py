from scrapy.item import Item, Field

class Startup(Item):
    name = Field()
    headquarters = Field()
    industry = Field()
    description = Field()
    website = Field()

class Investments(Item):
    amount = Field()
    kind = Field()
    date = Field()
    stage = Field()
    investors = Field()

class Investors(Item):
    name = Field()
    kind = Field()
    headquarters = Field()
    description = Field()
    website = Field()

class SearchResults(Item):
    url = Field()
