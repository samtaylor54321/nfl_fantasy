import pandas as pd
import pytest
import numpy as np

from src.scrapper import NFLDataScrapper


@pytest.fixture()
def scrapper():
    # Instantiate scrapper
    scrapper = NFLDataScrapper()

    yield scrapper


@pytest.fixture()
def sample_data():
    df = pd.DataFrame(
        {
            "Price": [10, 20, 30, np.nan],
            "Position": ["QB", "RB", "WR", "WR"],
            "TTL": [4, 6, 8, 10],
            "Squad": ["Team1", "Team2", "Team3", np.nan],
            "Years Remaining": [1.0, 1.0, 2.0, np.nan],
        }
    )
    yield df


class TestScrapper(object):
    def test_generate_nfl_dataset(object, scrapper):
        """Test the overall functionality of the module"""
        # Generate actual results
        actual = scrapper.generate_nfl_dataset()

        assert (actual.shape[0] == 723) and (actual.shape[1] == 31)

    def test_clean_data(object, scrapper, sample_data):
        """Test that the missing values are filled"""
        cleaned_data = scrapper.clean_data(sample_data)

        assert cleaned_data["Squad"].isna().sum() == 0

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
                    "TTL",
                    "Squad",
                    "Years Remaining",
                    "AvgPointsByPosition",
                    "PointsAboveReplacement",
                ]
            ).astype("object")
        ).all()

    def test_add_price_data(object, scrapper, sample_data):
        """Test that linear model for predicting value is added correctly"""
        data_with_predictions = scrapper.add_price_data(sample_data)

        assert data_with_predictions["Price"].isna().sum() == 0
