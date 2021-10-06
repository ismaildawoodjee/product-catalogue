import scrapy
from catalogue.items import CatalogueItem

BASE_URL = "https://www.komatsu.com.au/equipment"
EQUIPMENTS = [
    "excavators",
    "wheel-loaders",
    "backhoe",
    "skidsteer",
    "dump-trucks",
    "dozers",
    "motor-graders",
    "crushers",
]


class KomatsuSpider(scrapy.Spider):
    name = "komatsu"

    def start_requests(self):
        for equipment in EQUIPMENTS:
            url = BASE_URL + f"/{equipment}"
            yield scrapy.Request(url)

    def parse(self, response):
        # go to each item's page and get its specifications
        for product in response.css("div.list__item"):
            product_url = product.css("h3 > a::attr(href)").get()

            if product_url is not None:
                product_url = response.urljoin(product_url)
                yield scrapy.Request(product_url, callback=self.get_specifications)

        # after crawling through all items, navigate to the next page
        next_page = response.css("li.pager__next > a::attr(href)").get()
        next_page_url = response.urljoin(next_page)

        if next_page_url is not None and next_page_url != response.url:
            yield scrapy.Request(next_page_url, callback=self.parse)

    def get_specifications(self, response):
        item = CatalogueItem()

        # send these items to the pipeline, where they can be processed
        item["equipment_url"] = response.url.split("/")
        item["specifications"] = response.css("ul.spec__list")
        item["image_link"] = response.css("div.detail__img img::attr(src)").get()

        yield item
