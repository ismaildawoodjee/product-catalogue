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
        # check if there are actually tables; if not, just get the <p>'s text
        if detail.css("table").getall():
            for table in detail.css("table").getall():
                df = pd.read_html(table)[0]
                yield self.process_dataframe(df=df, header=header)
        elif detail.css("p::text").getall():
            for text in detail.css("p::text").getall():
                df = pd.DataFrame(["", text])
                yield self.process_dataframe(df=df, header=header)
        else:
            yield self.process_dataframe(df=pd.DataFrame([""]), header=header)

    def process_dataframe(self, df, header):
        # check if all elements in each row are identical; if so make them empty except the first
        for row_idx in range(df.shape[0]):
            # convert to list with `.values`
            row = df.iloc[row_idx, :].values
            if len(set(row)) == 1:
                df.iloc[row_idx, 1:] = None

        # remove NaN in the second pass, cannot remove in the first pass
        df.insert(loc=0, column="header", value=header)
        # df.iloc[:, 0] = [f"{header} | {item}" for item in df.iloc[:, 0]]
        # df.iloc[:, 0] = [
        #     f"{header} | " if item[-1:-4:-1] == "nan" else item
        #     for item in df.iloc[:, 0]
        # ]
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
            # generator object - turn this into a list and iterate over it
            gen_table = self.process_table(header, detail)
            for table in list(gen_table):
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
