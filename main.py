import requests
import pandas as pd
import re
import time

from bs4 import BeautifulSoup

start = time.time()

BASE_URL = "https://www.komatsu.com.au/equipment"
FILTER_URL = "?page"


def get_container(page_no):
    """Gets the container holding all the item information in the page 'page_no'.
    The BeautifulSoup function parses the text response from the website URL and then
    collects all the 'div' elements that have a 'class' attribute matching the
    pattern 'list__item'.

    Args:
        page_no (int): specific page number in the BASE_URL's list of equipments.

    Returns:
        container (ResultSet): a BeautifulSoup object that contains the HTML
        elements of all 15 equipments in the page 'page_no'.
    """
    main_url = BASE_URL + FILTER_URL + f"={page_no}"

    response = requests.get(url=main_url)
    soup = BeautifulSoup(markup=response.text, features="html.parser")
    container = soup.find_all("div", attrs={"class": "list__item"})

    return container


def assemble_df(page_no):
    """Picks out the specific data from each item (equipment_type, equipment_id,
    the three features and their values along with the units, and an image link).
    Equipment type, ID, and image link can be extracted directly, whereas the
    three features require regex pattern matching and a bit of processing to get
    the correct words and characters.

    The textual data are assembled into a Pandas DataFrame, and the images are
    downloaded from the image links.

    Args:
        page_no (int): specific page number in the BASE_URL's list of equipments.

    Returns:
        df (DataFrame): a Pandas DataFrame assembled after extracting, processing
        and combining the scraped data.

    Downloaded images are also written out as 'jpg' files into the 'images' folder.
    """
    equipment_container = get_container(page_no)

    equipment_type = []
    equipment_id = []
    feature = []
    for equipment in equipment_container:
        # equipment type
        try:
            tag = equipment.find("a")["href"]
            e_type_text = tag.split("/")[2]
            equipment_type.append(e_type_text)
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
            # replace '/' with a '-' so that Python won't think its a directory
            e_id_text = e_id_text.replace("/", "-")

            image_binary = requests.get(image_link)
            with open(f"./images/{e_type_text}_{e_id_text}.jpg", "wb") as file:
                file.write(image_binary.content)

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
                # take out the first element and select only the characters from 2 to -1
                first_key = re.findall(r"/>\D+\s\D+<", str(all_features[0]))[0][2:-1]
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

    feature = pd.json_normalize(feature, sep="_")

    df_dict = {
        "equipment_type": equipment_type,
        "equipment_id": equipment_id,
    }
    df = pd.DataFrame(df_dict)
    df = pd.concat([df, feature], axis=1)

    return df


if __name__ == "__main__":
    """Loops through all 7 pages from the BASE_URL, starting from the first page,
    and after initializing an empty DataFrame. Each dataframe extracted from each
    page is concatenated to the previous one and the final output is written as
    a CSV file into the 'data' folder.

    If the process is interrupted for some reason (Ctrl + C) or due to some error,
    the dataframe held in memory is still saved to the 'data' folder. For very large
    loops (e.g. 1000s to 10,000s of pages) this makes it ideal to resume from where
    you left off when you encounter an exception, and all the data that was scraped
    before does not get lost.
    """
    i = 1
    data = pd.DataFrame()

    try:
        while i < 8:
            df = assemble_df(page_no=i)
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
