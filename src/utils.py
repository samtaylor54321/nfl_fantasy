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

def keep_features(df):
    """Excludes any variables which don't have fantasy points associated from the DataFrame
    Args:
        df(pd.DataFrame): DataFrame for a given statistic
    Returns:
        pd.DataFrame: DataFrame which contains only columns required
    """
    df.drop()