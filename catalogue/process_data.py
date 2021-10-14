import pandas as pd
from pprint import pprint
from unidecode import unidecode
import re

EQUIPMENT_COLS = {
    "excavators": [],
    "wheel-loaders": [],
    "backhoe": [],
    "skidsteer": [],
    "dump-trucks": [],
    "dozers": [],
    "motor-graders": [],
    "crushers": [],
}

df = pd.read_csv("../data/equipment_specifications_raw.csv")


def split_equipment_types(df):
    df = df.sort_index(axis=1, ascending=True)

    for col in df.columns:
        for equipment_type in EQUIPMENT_COLS.keys():
            if re.match(f"{equipment_type}", col):
                EQUIPMENT_COLS[equipment_type].append(col)

    for equipment_type, equipment_cols in EQUIPMENT_COLS.items():
        equipment_df = df.loc[:, equipment_cols]
        equipment_df.dropna(axis=0, how="all", inplace=True)
        equipment_df.to_csv(f"../data/{equipment_type}.csv", index=False)


def union_specification_keys(etype):
    """Try out combining all keys on one small dataset first"""

    df = pd.read_csv(f"../data/{etype}.csv")
    cols = df.columns
    no_specs = [list(cols).index(col) for col in cols if "SPECS" not in col]

    # deal with the last item in the equipment CSV file - set index to be the spec keys
    item_df = df.iloc[:, no_specs[-1] :].copy()
    item_df.dropna(axis=0, how="all", inplace=True)
    item_df.rename(
        columns={item_df.columns[0]: "spec_header", item_df.columns[1]: "spec_key"},
        inplace=True,
    )

    # deal with the remaining items, setting their indices, and joining them to the last item
    for start, end in zip(no_specs[:-1], no_specs[1:]):
        item = df.iloc[:, start:end].copy()
        item.dropna(axis=0, how="all", inplace=True)
        item.rename(
            columns={item.columns[0]: "spec_header", item.columns[1]: "spec_key"},
            inplace=True,
        )

        item_df = item_df.merge(
            item.reset_index(), how="outer", on=["spec_header", "spec_key"], sort=False
        ).sort_index()

        item_df.drop("index", axis=1, inplace=True)
        item_df.drop_duplicates()

    return item_df


def reshape_dataframe(df, etype):
    """Reshape dataframe to make it flat, suitable for loading into a SQL database"""

    # unidecode for dealing with stuff like \xa0
    df["spec_header"] = [unidecode(str(header)).lower() for header in df["spec_header"]]
    df["spec_key"] = [unidecode(str(key)).lower() for key in df["spec_key"]]

    df["spec_key"] = [
        f"{header}_{key}" if (key != "nan") and (header != key) else f"{header}"
        for header, key in zip(df["spec_header"], df["spec_key"])
    ]
    df.drop("spec_header", axis=1, inplace=True)

    # some slashes can denote "per" so better to keep them; other slashes denote "or"
    spec_key = []
    for key in df["spec_key"]:
        key = re.sub(r"-|,|\(|\)|:", "", key.replace(" ", "_"))
        key = key.replace("__", "_").replace("&", "and").replace("@", "at")
        spec_key.append(key)
    df["spec_key"] = spec_key

    df.drop_duplicates(subset=["spec_key"], inplace=True)

    new_cols = ["spec_key"]
    for col in df.columns:
        col_split = col.split("_")

        # dont get extra columns for the equipment
        if len(col_split) > 2 and col_split[2] == "SPECS-2":
            new_cols.append(col)

    df = df[new_cols]
    df = df.transpose()

    # drop over 50% nulls
    thresh = round(0.5 * df.shape[0])
    df.dropna(axis=0, thresh=thresh, inplace=True)

    # reindex columns and add additional ones
    df = df.reset_index()
    df.columns = df.iloc[0]
    df = df.iloc[1:, :]

    equipment_type = [key.split("_")[0] for key in df["spec_key"]]
    equipment_id = [key.split("_")[1] for key in df["spec_key"]]
    df.insert(loc=0, column="equipment_type", value=equipment_type)
    df.insert(loc=1, column="equipment_id", value=equipment_id)
    df.drop("spec_key", axis=1, inplace=True)

    # these are places where subheadings occur under the main heading - requires further processing
    all_null = (df.isnull().sum() / df.shape[0]) == 1
    null_columns = df.columns[all_null]
    df.drop(null_columns, axis=1, inplace=True)

    print(df.shape)
    # pprint(list(df.columns))
    df.to_csv(f"../data/processed/{etype}.csv", index=False)


if __name__ == "__main__":
    # split_equipment_types(df=df)
    exc_df = union_specification_keys(etype="skidsteer")
    reshape_dataframe(df=exc_df, etype="skidsteer")

    # need to handle edge cases: motor-graders, dump-trucks, dozers, wheel-loaders
