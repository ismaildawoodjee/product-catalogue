import pandas as pd
import warnings

warnings.filterwarnings("ignore")

df = pd.read_csv("./data/equipment_data_raw.csv")


def data_exploration():
    """Quick exploration to see how the data looks like."""

    print(f"Columns:\n{df.columns}")
    print(f"Proportion of Nulls:\n{df.isnull().sum() / df.shape[0]}")
    print(f"Type of Columns:\n{df.dtypes}")


def common_preprocessing():
    """Perform preprocessing tasks that are common across all equipment types.
        -
        -
        -

    Returns:
        DataFrame: dataframe with `engine_power` and `operating_weight` columns
        that are processed and renamed with their respective units. The third feature
        that each equipment has is also cleaned and renamed.
    """

    # drop the last column, which is 100% null
    df.drop(df.columns[-1], axis=1, inplace=True)

    # separate `engine_power` into kW and HP columns, extracting only numbers and casting to float
    engine_power_kw = (
        df["engine_power"]
        .map(arg=lambda item: item.split(" / ")[0][:-3], na_action="ignore")
        .map(arg=lambda item: float(item.replace(",", "")), na_action="ignore")
    )
    engine_power_hp = (
        df["engine_power"]
        .map(arg=lambda item: item.split(" / ")[1][:-3], na_action="ignore")
        .map(arg=lambda item: float(item.replace(",", "")), na_action="ignore")
    )
    # insert new columns and remove the old `engine_power` column
    df.insert(loc=1, column="engine_power_kw", value=engine_power_kw)
    df.insert(loc=2, column="engine_power_hp", value=engine_power_hp)
    df.drop("engine_power", axis=1, inplace=True)

    # extract only numbers from the `operating_weight` column and cast it to float
    df["operating_weight"] = df["operating_weight"].map(
        arg=lambda item: float(item[:-3].replace(",", "")), na_action="ignore"
    )
    df.rename({"operating_weight": "operating_weight_kg"}, axis=1, inplace=True)

    return df


def split_equipment_types(df):
    """"""
    df = common_preprocessing()
    equipments = df["equipment_type"].unique()

    for equipment in equipments:
        equipment_df = df.query("equipment_type == @equipment")

        # identify 100% null columns
        all_null = equipment_df.isnull().sum() / equipment_df.shape[0] == 1
        null_columns = equipment_df.columns[all_null]

        # remove 100% null columns
        equipment_df.drop(null_columns, axis=1, inplace=True)

        # extract the units, which is the last two characters
        suffix = equipment_df.iloc[0, -1][-2:]
        if suffix[-1] == "³":
            suffix = suffix.replace("³", "3")
        last_col = equipment_df.columns[-1]

        # extract only numbers from the last column and cast it to float (if possible)
        try:
            equipment_df[last_col] = equipment_df[last_col].map(
                arg=lambda item: float(item[:-3].replace(",", "")), na_action="ignore"
            )

        except Exception as ex:
            if equipment == "crushers":
                pass
            else:
                equipment_df[last_col] = equipment_df[last_col].map(
                    arg=lambda item: item[:-3].replace(",", ""), na_action="ignore"
                )
            print(f"WARNING - {ex} in DataFrame '{equipment}'. Ignoring this.")

        finally:
            # rename column with units
            if equipment == "crushers":
                pass
            else:
                equipment_df.rename(
                    {last_col: f"{last_col}_{suffix}"}, axis=1, inplace=True
                )
            # save to CSV file in the `data` directory
            equipment_df.to_csv(f"./data/{equipment}.csv", index=False)


if __name__ == "__main__":
    split_equipment_types(df=df)
