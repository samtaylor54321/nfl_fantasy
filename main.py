import numpy as np
import pandas as pd
from scrapy.crawler import CrawlerProcess
from src.scrapper import NflStatsScraper
from src.utils import build_dataframe, scorer


def main():
    # Parse player values into memory
    player_values = pd.read_excel("data/player_values.xlsx", index_col="Player")

    # Crawl NFL.com for data
    process = CrawlerProcess()
    process.crawl(NflStatsScraper)
    process.start()

    # Parse datasets from the webscraper
    for types in sorted(NflStatsScraper.nfl_columns_dict.keys()):
        player_values = pd.merge(left=player_values,
                                 right=build_dataframe(stats=NflStatsScraper.nfl_stats_dict[types],
                                                       names=NflStatsScraper.nfl_players_dict[types],
                                                       columns=NflStatsScraper.nfl_columns_dict[types]),
                                 suffixes=["", types],
                                 left_index=True,
                                 right_index=True,
                                 how="left")

    # Reduce dataset down to the necessary columns
    player_values = player_values[['Position', 'Value', 'Team', 'Rush Yds', 'TDRushing', 'Rush FUM', 'Rush 1st',
                                   'Pass Yds', 'TD', 'INT', 'Rec', 'Yds', 'TDReceiving', "Rec 1st"]]

    # Score dataset
    player_values = scorer(player_values)

    player_values.to_csv("dataset.csv")


if __name__ == "__main__":
    main()
