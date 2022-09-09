import scrapy


class NflStatsScraper(scrapy.Spider):
    """Scrapes data for the current season from NFL.com"""

    name = "nfl_data_spider"
    nfl_players_dict = {}
    nfl_stats_dict = {}
    nfl_columns_dict = {}

    def start_requests(self):
        """Generator for URLs to be parsed
        Notes:
            Loops through the passing, rushing, receiving and kicing data for the current season
        Yields:
            str: Initial URL to start web scraping from.
        """
        # Define URLs
        urls = [
            "https://www.nfl.com/stats/player-stats/category/passing/2022/REG/all/passingyards/desc",
            "https://www.nfl.com/stats/player-stats/category/rushing/2022/REG/all/rushingyards/desc",
            "https://www.nfl.com/stats/player-stats/category/receiving/2022/REG/all/receivingreceptions/desc",
            "https://www.nfl.com/stats/player-stats/category/field-goals/2022/REG/all/kickingfgmade/desc",
        ]
        # Yield URL to scrapy request.
        for url in urls:
            yield scrapy.Request(url=url, callback=self._parse_stats)

    def _parse_stats(self, response):
        """Populates dictionaries for stats, player names, columns and data types
        Params:
            response(Selector): Scrapy Selector object which contains HTML for a given URL
        Yields:
             str: A further URL to scrape data from
        Notes:
            Process will continue as long as there is a 'next page' link on the URL
        """
        # Get the data type we're dealing with
        type = response.xpath(
            '//li[@class="d3-o-tabs__list-item d3-is-active"]/a/text()'
        ).extract()[0]

        # Check if the type exists and populates on the first pass but appends after.
        if type not in NflStatsScraper.nfl_players_dict.keys():
            NflStatsScraper.nfl_players_dict[type] = response.xpath(
                '//a[@class="d3-o-player-fullname nfl-o-cta--link"]/text()'
            ).extract()
        else:
            NflStatsScraper.nfl_players_dict[type].extend(
                response.xpath(
                    '//a[@class="d3-o-player-fullname nfl-o-cta--link"]/text()'
                ).extract()
            )
        # Check if the type exists and populates on the first pass but appends after.
        if type not in NflStatsScraper.nfl_stats_dict.keys():
            NflStatsScraper.nfl_stats_dict[type] = response.xpath(
                "//tr/td/text()"
            ).extract()
        else:
            NflStatsScraper.nfl_stats_dict[type].extend(
                response.xpath("//tr/td/text()").extract()
            )
        # Check if the type exists and populates on the first pass but appends after.
        if type not in NflStatsScraper.nfl_columns_dict.keys():
            NflStatsScraper.nfl_columns_dict[type] = response.xpath(
                "//th/a/text()"
            ).extract()

        # Check if there's a "next page" link
        links_to_follow = response.xpath('//link[@rel="prerender"]/@href').extract()

        # If there's a link, yield the url and continue the loop else end.
        if len(links_to_follow) == 1:
            for url in links_to_follow:
                yield response.follow(url=url, callback=self._parse_stats)
        else:
            print("All data scrapped for " + type)
