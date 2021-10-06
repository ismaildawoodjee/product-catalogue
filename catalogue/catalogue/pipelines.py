# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from w3lib.html import remove_tags
from unidecode import unidecode

import pandas as pd
import html
import re


class CataloguePipeline:

    data = pd.DataFrame()

    def clean_string(self, string):
        string = remove_tags(string)
        string = re.sub(r"[\r\n\t]", "", string)
        string = unidecode(string)
        return html.unescape(string)

    def process_table(self, html_table):
        table = pd.read_html(html_table)[0]
        return table

    def process_item(self, item, spider):
        df = self._process_item(item, spider)
        self.data = pd.concat([self.data, df], axis=1, ignore_index=False)
        self.data.to_csv("../data/raw_equipment_specifications.csv", index=False)

    def _process_item(self, item, spider):
        equipment_type = item["equipment_url"][4]
        equipment_id = item["equipment_url"][-1]
        specifications = item["specifications"]

        df = pd.DataFrame()

        for html_table in specifications.css("li.spec__list-item table").getall():
            table = self.process_table(html_table, item)
            df = pd.concat([df, table], axis=0, ignore_index=True)

        try:
            col_names = []
            for idx in range(len(df.columns)):
                if idx == 0:
                    col_names.append(f"{equipment_type}_{equipment_id}")
                else:
                    col_names.append(f"{equipment_type}_{equipment_id}_specs-{idx}")
            df.columns = col_names

        except Exception as ex:
            print(f"ERROR - {ex} on {equipment_type}_{equipment_id}")

        return df
