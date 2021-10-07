import pandas as pd
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


def sort_by_colnames(df):
    return df.sort_index(axis=1, ascending=True)


def split_equipment_types(df):
    for col in df.columns:
        for equipment_type in EQUIPMENT_COLS.keys():
            if re.match(f"{equipment_type}", col):
                EQUIPMENT_COLS[equipment_type].append(col)

    for equipment_type, equipment_cols in EQUIPMENT_COLS.items():
        equipment_df = df.loc[:, equipment_cols]
        equipment_df.dropna(axis=0, how="all", inplace=True)
        equipment_df.to_csv(f"../data/{equipment_type}.csv", index=False)


def union_specification_keys():
    df = pd.read_csv("../data/motor-graders.csv")

    no_specs = [list(df.columns).index(col) for col in df.columns if "SPECS" not in col]

    for start, end in zip(no_specs[:-1], no_specs[1:]):
        item_df = df.iloc[:, start:end]
        item_df.dropna(axis=0, how="all", inplace=True)
        # df.reindex()

        print(item_df)
        # i += 1

    # print(i)
    # print(start, end)

    # for  in no_specs:
    #     for idx in no_specs:
    #         print(idx, idx)
    # print(df.iloc[:,idx:])

    # print(df.iloc[:,no_specs])

    # for col in df.columns:
    #     if "SPECS" not in


if __name__ == "__main__":
    sorted_df = sort_by_colnames(df=df)
    split_equipment_types(sorted_df)
    # union_specification_keys()
