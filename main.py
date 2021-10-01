import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re

base_url = "https://www.komatsu.com.au/equipment"
filter_url = "?page"


def get_container(page_no):
    """"""
    main_url = base_url + filter_url + f"={page_no}"

    response = requests.get(url=main_url)
    soup = BeautifulSoup(markup=response.text, features="html.parser")
    container = soup.find_all("div", attrs={"class": "list__item"})  # matches pattern

    return container


def assemble_df(page_no):
    """"""
    equipment_container = get_container(page_no)

    equipment_type = []
    equipment_id = []
    image_link = []
    features = []
    for equipment in equipment_container:
        # equipment type
        try:
            tag = equipment.find("a")["href"]
            equipment_type.append(tag.split("/")[2])  # extract the type of equipment
        except:
            equipment_type.append(np.NaN)
        # equipment ID
        try:
            equipment_id.append(equipment.find("h3").get_text())
        except:
            equipment_id.append(np.NaN)
        # image link
        try:
            image_link.append(equipment.find("a").find("img")["src"])
        except:
            image_link.append(np.NaN)
        # features
        try:
            features_dict = {}
            all_features = equipment.find_all("li")
            
            try:
                first_key = re.findall(r"/>\D+\s\D+<", str(all_features[0]))[0][2:-1]
                first_value = all_features[0].find("strong").get_text()
                features_dict[first_key] = first_value
            except:
                features_dict[None] = None
            
            second_key = 'two'
            second_value = all_features[1].find("strong").get_text()
            features_dict[second_key] = second_value
            
            third_key = 'three'
            third_value = all_features[2].find("strong").get_text()
            features_dict[third_key] = third_value
            
            features.append(features_dict)
            # features.append(re.findall(r"/>\D+\s\D+<", str(all_features)))
            # features.append(re.findall((r">"), str(all_features)))
            # features.append(type(str(all_features)))
        except Exception as ex:
            features.append(np.NaN)
            print(ex)

    # image_link = []
    # for equipment in equipment_container:
    #     tag

    print(equipment_type)
    print(equipment_id)
    print(features)
    # print(image_link)
    print("\n", equipment_container[0])
    # print(len(image_link))


# equipment_id


assemble_df(1)
