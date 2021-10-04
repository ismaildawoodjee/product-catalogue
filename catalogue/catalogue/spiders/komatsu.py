import scrapy
import requests

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
            resp = requests.get(url)
            print(f"\nCode: {resp.status_code} for equipment type {equipment}\n")

            yield scrapy.Request(url)

    def parse(self, response):
        print("Accessed the page")
