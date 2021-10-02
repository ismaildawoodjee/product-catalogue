import requests
import pandas as pd
import re
import time

from bs4 import BeautifulSoup

start = time.time()

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
    feature = []
    for equipment in equipment_container:
        # equipment type
        try:
            tag = equipment.find("a")["href"]
            e_type_text = tag.split("/")[2]
            equipment_type.append(e_type_text)  # extract the type of equipment
        except Exception as ex:
            equipment_type.append(None)

        # equipment ID
        try:
            e_id_text = equipment.find("h3").get_text()
            equipment_id.append(e_id_text)
        except Exception as ex:
            equipment_id.append(None)

        # download images and save them to the images folder
        try:
            print(f"Downloading {e_type_text}_{e_id_text} image...", end="")

            image_link = equipment.find("a").find("img")["src"]
            # replace backslash with a '-' so that Python won't think its a directory
            e_id_text = e_id_text.replace("/", "-")

            image_binary = requests.get(image_link)
            with open(f"./images/{e_type_text}_{e_id_text}.jpg", "wb") as f:
                f.write(image_binary.content)

        except Exception as ex:
            print(f"ERROR - {ex}")
        finally:
            print("Done")

        # features
        try:
            all_features = equipment.find_all("li")
            features_dict = {}

            # using a loop here doesn't work (cannot append dictionary to a list if using a loop)
            # first feature of the equipment, all_features[0]
            try:
                first_key = re.findall(r"/>\D+\s\D+<", str(all_features[0]))[0][2:-1]
                # take out the first element and select only the characters from 2 to -1
                first_key = first_key.lower().replace(" ", "_")
            except Exception as ex:
                first_key = None
            try:
                first_value = all_features[0].find("strong").get_text()
            except Exception as ex:
                first_value = None
            features_dict[first_key] = first_value

            # second feature of the equipment, all_features[1]
            try:
                second_key = re.findall(r"/>\D+\s\D+<", str(all_features[1]))[0][2:-1]
                second_key = second_key.lower().replace(" ", "_")
            except Exception as ex:
                second_key = None
            try:
                second_value = all_features[1].find("strong").get_text()
            except Exception as ex:
                second_value = None
            features_dict[second_key] = second_value

            # third feature of the equipment, all_features[2]
            try:
                third_key = re.findall(r"/>\D+\s\D+<", str(all_features[2]))[0][2:-1]
                third_key = third_key.lower().replace(" ", "_")
            except Exception as ex:
                third_key = None
            try:
                third_value = all_features[2].find("strong").get_text()
            except Exception as ex:
                third_value = None
            features_dict[third_key] = third_value

            feature.append(features_dict)

        except Exception as ex:
            feature.append({})
            # print(ex)

    feature = pd.json_normalize(feature, sep="_")

    df_dict = {
        "equipment_type": equipment_type,
        "equipment_id": equipment_id,
    }
    df = pd.DataFrame(df_dict)
    df = pd.concat([df, feature], axis=1)

    return df


if __name__ == "__main__":
    i = 1
    data = pd.DataFrame()

    try:
        while i < 8:
            df = assemble_df(i)
            data = pd.concat([data, df], ignore_index=True)
            print(f"Page {i} extraction is done")
            i += 1

    except KeyboardInterrupt:
        print(f"Extraction at Page {i} stopped")

    except Exception as ex:
        print(f"ERROR: {ex}")

    finally:
        data.to_csv("./data/equipment_data_raw.csv", index=False)

    end = time.time()
    time_taken = (end - start) / 3600
    print(f"The time taken was {time_taken} hours.")
