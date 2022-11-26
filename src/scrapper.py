import pandas as pd
import re
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
        # Scrape gameweek values
        self.scrape_weeks()

        # Scrape player level data for each game week
        players, weekly_results = self.scrape_weekly_results()

        # Combine the weekly results with the entire player pool
        player_database = self.combine_weekly_performance_with_players(
            players, weekly_results
        )

        # Read owner database into memory
        owner_database = pd.read_csv("./data/nfl-dynasty-rosters.csv")

        # Combine player database with owner database
        merged_players_with_owners = player_database.merge(
            owner_database[["Player", "Team", "Years Remaining", "Price"]],
            how="left",
            left_on="Name",
            right_on="Player",
        )

        # Preprocess the data
        merged_players_with_owners = self.clean_data(merged_players_with_owners)

        # Add Points Above Average values for the database
        merged_players_with_owners = self.add_par_data(merged_players_with_owners)

        # Add predictions for the price of free agents
        merged_players_with_owners = self.add_price_data(merged_players_with_owners)

        # Load trade value data
        trade_values = pd.read_csv("./data/trade-value-nov-22.csv")

        # Combine stats player database with trade values for players
        merged_players_with_owners = pd.merge(
            merged_players_with_owners,
            trade_values[["Name", "Trade Value"]],
            how="left",
            right_on="Name",
            left_on="Name",
        )

        # Assign value of 1.0 to any player without a defined trade value
        merged_players_with_owners["Trade Value"] = merged_players_with_owners[
            "Trade Value"
        ].fillna(1.0)

        return merged_players_with_owners

    def scrape_weeks(self) -> list:
        """Gets the current week of the latest game week"""
        # Scrape data
        response = requests.get(self.url)

        # Extract response content
        soup = BeautifulSoup(response.content, features="html.parser")

        # Find the weekly values
        tags = soup.find("select", attrs={"aria-label": "end date"})

        # Work through the soup to get out the number of game weeks through the
        # season we current are
        self.weeks = [
            "".join(re.findall(r"\d", str(x.string)))
            for x in tags.children
            if x.string != "\n"
        ]

        # Grab the latest gameweek as an attribute
        self.latest_gameweek = int(max(self.weeks)) - 1

    def scrape_weekly_results(self) -> tuple:
        """Scrape weekly player data
        Returns:
            tuple: tuple containing a set of distinct players across all game
                weeks and the a dictionary of weekly results for those players
        """
        # Instantiate empty set
        players = set()

        # Instantiate empty dictionary
        weekly_results = {}

        # Loop through each gameweek and get week by week breakdown
        for week in list(map(int, self.weeks)):
            html = requests.get(
                f"https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2022&start=1&end={week}"
            )
            soup = BeautifulSoup(html.content, "html.parser")

            # Find all table data
            table_rows = soup.find_all("tr")

            results = []

            for i, row in enumerate(table_rows):
                if i == 0:
                    continue
                else:
                    results.append([row.text for row in row.find_all("td")])

            weekly_result = pd.DataFrame(
                results,
                columns=["Rank", "Name", "Team", "Position", "Score", "Games", "Avg"],
            )

            weekly_result["Score"] = weekly_result["Score"].astype(float)

            players = players.union(weekly_result["Name"])

            weekly_results[week] = weekly_result

        return players, weekly_results

    def combine_weekly_performance_with_players(self, players, weekly_results):
        """Combine data and add latest roster infomation
        Return:
            pd.DataFrame: pd.DataFrame containing player level data with
                roster level data.
        """
        # Convert set of players into a pd.DataFrame so that it can be merged
        player_database = pd.DataFrame(players, columns=["Name"])

        # Iterate through the weeks to grab append the scores to the player pool
        for i, week in enumerate(weekly_results.values()):
            player_database = player_database.merge(
                week[["Name", "Score", "Position"]],
                how="left",
                left_on="Name",
                right_on="Name",
                suffixes=["y", i],
            )

        # Get player names and player ositions
        players_position = player_database.iloc[:, [0, -1]]

        # Drop extract columns which are created as part of the joining process
        player_database = player_database.loc[
            :,
            (player_database.columns.str.contains("Score*"))
            | (player_database.columns == "Name"),
        ]

        # Get complete DataFrame of players and their weekly scores
        player_database = pd.merge(
            players_position,
            player_database,
            how="inner",
            left_on="Name",
            right_on="Name",
        )

        # Fill missing values for points scored with 0.0
        player_database = player_database.fillna(0.0)

        # Rename columns to reflect the game weeks
        player_database.columns = (
            ["Name"]
            + ["Position"]
            + [week for week in range(0, (max(list(map(int, self.weeks)))))]
        )

        return player_database

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Additional preprocessing steps
        Returns:
            pd.DataFrame: pd.DataFrame with additional metadata added
        """
        # Add the latest score
        data["total_pts"] = data[self.latest_gameweek]
        # Add roster status
        data["Team"] = data["Team"].fillna("Free Agent")
        # Clarify free agent status
        data["Free Agent"] = data["Team"] == "Free Agent"
        # Add missing values for agents - you can only sign them for 1 year
        # in the game
        data["Years Remaining"] = data["Years Remaining"].fillna(1.0)

        return data

    def add_par_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add Points Above Replacement Data
        Return:
            pd.DataFrame: Data with additional fields relating to PAR added.
        """
        avg_points_by_position = pd.DataFrame(
            data.groupby(["Position"])[int(max(self.weeks)) - 1].mean()
        )

        avg_points_by_position.columns = ["AvgPointsByPosition"]

        data = data.merge(
            avg_points_by_position, how="left", left_on="Position", right_index=True
        )

        data["PointsAboveReplacement"] = (
            data[self.latest_gameweek] - data["AvgPointsByPosition"]
        )

        data["AvgPoints"] = data[self.latest_gameweek] / self.latest_gameweek

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
                        "total_pts"
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
                        "total_pts",
                    ].values.reshape(-1, 1)
                )
            except ValueError:
                continue

        return data
