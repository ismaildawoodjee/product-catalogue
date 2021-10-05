# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from w3lib.html import remove_tags
from unidecode import unidecode
import html
import json
import re
import os

current_dir = os.getcwd()


class CataloguePipeline:

    data = {}
    data["records"] = []

    def clean_string(self, string):
        string = remove_tags(string)
        string = re.sub(r"[\r\n\t]", "", string)
        string = unidecode(string)
        final_string = html.unescape(string)

        return final_string

    def process_item(self, item, spider):
        record = self._process_item(item, spider)

        with open(
            os.path.join(current_dir, "..", "data/raw_equipment_specifications.json"),
            mode="w",
            encoding="utf-8",
        ) as file:
            self.data["records"].append(record)
            json.dump(self.data, file)

    def _process_item(self, item, spider):
        data_keys = []
        data_keys.append("equipment_type")
        data_keys.append("equipment_id")

        data_values = []
        equipment_type = item["equipment_url"][2]
        equipment_id = item["equipment_url"][-1]

        data_values.append(equipment_type)
        data_values.append(equipment_id)

        specifications = item["specifications"]

        for html_table in specifications.css("div.spec__detail tbody"):
            table_row = html_table.css("tr")

            for row in table_row:
                spec = row.css("td").getall()

                try:
                    data_keys.append(self.clean_string(spec[0]))
                except Exception as ex:
                    data_keys.append(self.clean_string("NA"))
                try:
                    data_values.append(self.clean_string(spec[1]))
                except Exception as ex:
                    data_keys.append(self.clean_string("NA"))

        return dict(zip(data_keys, data_values))
