# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CatalogueItem(scrapy.Item):
    # define the fields for your item here like:
    equipment_url = scrapy.Field()
    specifications = scrapy.Field()
