import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression


class NFLDataScrapper:
    def __init__(
        self, url: str = "https://www.fantasypros.com/nfl/reports/leaders/ppr"
    ) -> None:
        self.url = url
        self.latest_gameweek = None
        self.weeks = None

    def generate_nfl_dataset(self):
        """Generate a dataset containing the weekly performances of NFL players"""
        html = requests.get(
            "https://www.fantasypros.com/nfl/reports/leaders/?year=2022&start=1&end=18"
        )

        soup = BeautifulSoup(html.content, "html.parser")
        tbody = soup.find_all("tbody")
        data = [info.text for info in tbody[0].find_all("td")]

        player_database = pd.DataFrame(
            np.array(data).reshape(int(len(data) / 24), 24),
            columns=[
                "Rank",
                "Player",
                "Position",
                "Team",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "Avg",
                "TTL",
            ],
        )

        player_database["Player"] = player_database["Player"].apply(lambda x: x.strip())
        player_database = player_database.replace("BYE", 0.0)
        player_database = player_database.replace("-", 0.0)

        for col in player_database:
            if col in ["Player", "Position", "Team"]:
                continue
            else:
                player_database[col] = player_database[col].astype("float16")

        # Read owner database into memory
        owner_database = pd.read_csv("./data/nfl-dynasty-rosters.csv")

        # Combine player database with owner database
        merged_players_with_owners = player_database.merge(
            owner_database[["Player", "Squad", "Years Remaining", "Price"]],
            how="left",
            left_on="Player",
            right_on="Player",
        )

        # Preprocess the data
        merged_players_with_owners = self.clean_data(merged_players_with_owners)

        # Add Points Above Average values for the database
        merged_players_with_owners = self.add_par_data(merged_players_with_owners)

        # Add predictions for the price of free agents
        merged_players_with_owners = self.add_price_data(merged_players_with_owners)

        # Load trade value data
        trade_values = pd.read_csv("./data/trade-value-jan-23.csv")

        # Combine stats player database with trade values for players
        merged_players_with_owners = pd.merge(
            merged_players_with_owners,
            trade_values[["Player", "Team", "Trade Value"]],
            how="left",
            right_on=["Player", "Team"],
            left_on=["Player", "Team"],
        )

        # Assign value of 1.0 to any player without a defined trade value
        merged_players_with_owners["Trade Value"] = merged_players_with_owners[
            "Trade Value"
        ].fillna(1.0)

        return merged_players_with_owners

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Additional preprocessing steps
        Returns:
            pd.DataFrame: pd.DataFrame with additional metadata added
        """
        # Add roster status
        data["Squad"] = data["Squad"].fillna("Free Agent")
        # Clarify free agent status
        data["Free Agent"] = data["Squad"] == "Free Agent"
        # Add missing values for agents - you can only sign them for 1 year
        # in the game
        data["Years Remaining"] = data["Years Remaining"].fillna(1.0)

        return data

    def add_par_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add Points Above Replacement Data
        Return:
            pd.DataFrame: Data with additional fields relating to PAR added.
        """
        avg_points_by_position = pd.DataFrame(data.groupby(["Position"])["TTL"].mean())
        avg_points_by_position.columns = ["AvgPointsByPosition"]

        data = data.merge(
            avg_points_by_position, how="left", left_on="Position", right_index=True
        )

        data["PointsAboveReplacement"] = data["TTL"] - data["AvgPointsByPosition"]

        return data

    def add_price_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate scoring model and add price predictions
        Args:
            data (pd.DataFrame): DataFrame containing the combined data for
                NFL players
        Returns:
            pd.DataFrame: Same pd.DataFrame but with predicted value for
                free agents based on their points scored.
        """
        for position in data["Position"].unique():
            try:
                # Instantiate regression model
                lr = LinearRegression()

                # Fit the data to existing data based on points scored and the
                # associated value of those players
                lr.fit(
                    data[(data["Position"] == position) & ~(data["Price"].isna())][
                        "TTL"
                    ].values.reshape(-1, 1),
                    data[(data["Position"] == position) & ~(data["Price"].isna())][
                        "Price"
                    ].values.reshape(-1, 1),
                )

                data.loc[
                    (data["Position"] == position) & (data["Price"].isna()), "Price"
                ] = lr.predict(
                    data.loc[
                        (data["Position"] == position) & (data["Price"].isna()),
                        "TTL",
                    ].values.reshape(-1, 1)
                )
            except ValueError:
                continue

        return data
