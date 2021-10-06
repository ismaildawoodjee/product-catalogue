import pandas as pd


def sort_by_colnames():

    df = pd.read_csv("./data/raw_equipment_specifications.csv")
    df = df.sort_index(axis=1, ascending=True)

    df.to_csv("./data/raw_equipment_specifications.csv", index=False)


if __name__ == "__main__":
    sort_by_colnames()
