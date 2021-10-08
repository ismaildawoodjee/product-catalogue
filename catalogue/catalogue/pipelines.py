# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pandas as pd
import requests


class CataloguePipeline:

    data = pd.DataFrame()

    def process_item(self, item, spider):
        df = self._process_item(item, spider)
        self.data = pd.concat([self.data, df], axis=1, ignore_index=False)
        self.data.to_csv("../data/equipment_specifications_raw.csv", index=False)

        # download image from each equipment's page
        image_binary = requests.get(item["image_link"])
        equipment_type = item["equipment_url"][4]
        equipment_id = item["equipment_url"][-1]

        with open(f"../images/{equipment_type}_{equipment_id}.jpg", "wb") as file:
            file.write(image_binary.content)

    def process_table(self, header, detail):
        # check if there is actually a table; if not, just get the <p>'s text
        if detail.css("table").get() is not None:
            html_table = detail.css("table").get()
            df = pd.read_html(html_table)[0]
        else:
            text = detail.css("p::text").get()
            df = pd.DataFrame([text])

        # check if all elements in each row are identical; if so make them empty except the first
        for row_idx in range(df.shape[0]):
            # convert to list with `.values`
            row = df.iloc[row_idx, :].values
            if len(set(row)) == 1:
                df.iloc[row_idx, 1:] = None

        df.iloc[:, 0] = [f"{header} | {item}" for item in df.iloc[:, 0]]
        return df

    def _process_item(self, item, spider):
        equipment_type = item["equipment_url"][4]
        equipment_id = item["equipment_url"][-1]
        specifications = item["specifications"]

        df = pd.DataFrame()
        header_css = "li.spec__list-item > div.spec__head h4::text"
        detail_css = "li.spec__list-item > div.spec__detail"

        for header, detail in zip(
            specifications.css(header_css).getall(), specifications.css(detail_css)
        ):
            table = self.process_table(header, detail)
            df = pd.concat([df, table], axis=0, ignore_index=True)

        try:
            col_names = []
            for idx in range(len(df.columns)):
                if idx == 0:
                    col_names.append(f"{equipment_type}_{equipment_id}")
                else:
                    col_names.append(f"{equipment_type}_{equipment_id}_SPECS-{idx}")
            df.columns = col_names

        except Exception as ex:
            print(f"ERROR - {ex} on {equipment_type}_{equipment_id}")

        return df
