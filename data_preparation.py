import pandas as pd

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
        that are processed.
    """

    # drop the last column, which is 100% null
    df.drop(df.columns[-1], axis=1, inplace=True)

    # replace all nulls with empty string to make cleaning easier
    # df.fillna("", inplace=True)

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

    return df


def split_equipment_types(df):
    """"""
    df = common_preprocessing()
    equipments = df["equipment_type"].unique()
    
    
    for equipment in equipments:
        equipment_df = df.query('equipment_type == @equipment')
        # cleaning
        
        equipment_df.to_csv(f"./data/{equipment}.csv", index=False)
        
        print(equipment_df)

print(split_equipment_types(df=df))
# data_exploration()
