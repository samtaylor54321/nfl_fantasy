import numpy as np
import pandas as pd


def build_dataframe(stats, names, columns):
    """Builds a dataframe from scrapped web data
    Args:
        stats(list): List of data values
        names(list): List of player names
        columns(list): List of variables contained in the dataset
    Returns:
        pd.DataFrame: Scrapped data for a given statistic.
    """
    # Strip the strings of each field where the values are populated and ignore blank spaces
    player_stats = [data.strip() for data in stats if data.strip() != '']
    player_names = [data.strip() for data in names if data.strip() != '']
    player_columns = [data.strip() for data in columns if data.strip() != '']
    # Build a DataFrame from the result
    dataset = pd.DataFrame(np.asarray(player_stats).reshape((int(len(np.asarray(player_stats)) / len(player_columns)),
                           len(player_columns))), index=np.asarray(player_names), columns=np.asarray(player_columns))

    return dataset


def scorer(df):
    """Converts raw data into fantasy points
    Args:
    df(pd.DataFrame): DataFrame for a given statistic
    Returns:
    pd.DataFrame: DataFrame which contains only columns required
    Notes:
    Fantasy scoring data is available from this URL https://fantasydata.com/api/fantasy-scoring-system/nfl
    """
    try:
        # Replace missing values with zero
        df = df.fillna(0)

        # Score rushing
        df["rushing_yard_pts"] = df["Rush Yds"].astype(int) / 10
        df["rushing_td_pts"] = df["TDRushing"].astype(int) * 6
        df["rushing_first_down_pts"] = df["Rush 1st"].astype(int) * 0.5
        df["rushing_fumbles_pts"] = df["Rush FUM"].astype(int) * 2

        # Score passing
        df["passing_yard_pts"] = df["Pass Yds"].astype(int) / 25
        df["passing_td_pts"] = df["TD"].astype(int) * 4
        df["passing_int_pts"] = df["INT"].astype(int) * 2

        # Score recieving
        df["reception_pts"] = df["Rec"].astype(int) * 0.5
        df["recieving_yards_pts"] = df["Yds"].astype(int) / 10
        df["recieving_td_pts"] = df["TDReceiving"].astype(int) * 6
        df["recieving_first_down_pts"] = df["Rec 1st"].astype(int) * 0.5

        # Generate overall score
        df["overall_pts"] = df["rushing_yard_pts"] + df["rushing_td_pts"] + df["rushing_first_down_pts"] -\
            df["rushing_fumbles_pts"] + df["passing_yard_pts"] + df["passing_td_pts"] - df["passing_int_pts"] +\
            df["reception_pts"] + df["recieving_yards_pts"] + df["recieving_td_pts"] + df["recieving_first_down_pts"]

        # Generate cost per point
        df["cost_per_point"] = df["overall_pts"] / df["Value"].astype(int)
        return df
    except KeyError:
        # Raise error if all fields are present
        print("Missing data present in the DataFrame")
