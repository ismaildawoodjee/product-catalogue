# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CatalogueItem(scrapy.Item):
    # define the fields for your item here like:
    equipment_type = scrapy.Field()
    equipment_id = scrapy.Field()
    