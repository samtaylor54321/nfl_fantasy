import pandas as pd
import pytest
import numpy as np

from src.scrapper import NFLDataScrapper


@pytest.fixture()
def scrapper():
    # Instantiate scrapper
    scrapper = NFLDataScrapper()
    # Get current gameweek infomation
    scrapper.scrape_weeks()

    yield scrapper


@pytest.fixture()
def sample_data():
    df = pd.DataFrame(
        {
            "Price": [10, 20, 30, np.nan],
            "Position": ["QB", "RB", "WR", "WR"],
            "total_pts": [4, 6, 8, 10],
            "Team": ["Team1", "Team2", "Team3", np.nan],
            "Years Remaining": [1.0, 1.0, 2.0, np.nan],
        }
    )
    yield df


class TestScrapper(object):
    def test_generate_nfl_dataset(object, scrapper):
        """Test the overall functionality of the module"""
        # Generate actual results
        actual = scrapper.generate_nfl_dataset()

        # Load expected results
        expected = pd.read_csv("./data/test-database.csv")

        assert (actual.shape[0] == expected.shape[0]) and (
            actual.shape[1] == expected.shape[1]
        )

    def test_scrape_weeks(object, scrapper):
        """Test the ability to identify how far we are through the season"""
        assert scrapper.latest_gameweek == 17, "The latest gameweek is not shown"

        assert len(scrapper.weeks) == 18, "Not all weeks are included"

    def test_scrape_weekly_results(object, scrapper):
        """Test that we're getting the correctly weekly results"""
        players, weekly_results = scrapper.scrape_weekly_results()

        assert (
            len(weekly_results.keys()) == scrapper.latest_gameweek + 1
        ), "Results are missing for at least one gameweek"

    def test_combine_weekly_performance_with_players(object, scrapper):
        # Scrape player level data for each game week
        players, weekly_results = scrapper.scrape_weekly_results()

        # Combine the weekly results with the entire player pool
        actual = scrapper.combine_weekly_performance_with_players(
            players, weekly_results
        )

        # Load expected data into memory
        expected = pd.read_csv("./data/test-database.csv", index_col=0)

        assert (actual.shape[0] == 720) and (actual.shape[1] == 20)

    def test_clean_data(object, scrapper, sample_data):
        """Test that the missing values are filled"""
        cleaned_data = scrapper.clean_data(sample_data)

        assert cleaned_data["Team"].isna().sum() == 0

        assert cleaned_data["Years Remaining"].isna().sum() == 0

    def test_add_par_data(object, scrapper, sample_data):
        """Test that additional fields are added correctly"""
        data_with_par = scrapper.add_par_data(sample_data)

        assert (
            data_with_par.columns.values
            == np.array(
                [
                    "Price",
                    "Position",
                    "total_pts",
                    "Team",
                    "Years Remaining",
                    "AvgPointsByPosition",
                    "PointsAboveReplacement",
                    "AvgPoints",
                ]
            ).astype("object")
        ).all()

    def test_add_price_data(object, scrapper, sample_data):
        """Test that linear model for predicting value is added correctly"""
        data_with_predictions = scrapper.add_price_data(sample_data)

        assert data_with_predictions["Price"].isna().sum() == 0
