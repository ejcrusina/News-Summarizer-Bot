# -*- coding: utf-8 -*-
import logging
import random
import time
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path

import click
import requests
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv

from src.exception import CustomException
from src.logger import logging
from src.utils import load_object


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info("making final data set from raw data")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()


class NewsScraper:
    def __init__(self, url, total_page, asof_date) -> None:
        self.url = url
        self.total_page = total_page
        self.asof_date = asof_date

    def scrape_inquirer(self) -> list:
        """Scrapes Inquirer's "Nation" section to get PH news data

        Returns
        -------
        list
            Contains dictionaries with metadata of news articles
        """
        # NOTE - change print and asserts to log
        latest_news_links = []

        for page_no in range(1, self.total_page):
            articles = []
            attempts = 0
            while not articles and attempts < 5:
                URL = f"{self.url}/page/{str(page_no)}"
                page = requests.get(URL).text
                soup = BeautifulSoup(page, "lxml")
                articles = soup.find_all("div", {"id": "ch-ls-box"})
                if not articles:
                    # Add random delay per page retry to avoid bot-behavior
                    time.sleep(5 + random.randint(0, 5))
                    attempts += 1

            if attempts == 5:
                print(f"Failed to fetch articles from page {page_no} after 5 attempts.")
                continue

            for article in articles:
                try:
                    news_link = article.a["href"]
                    pub_date = article.find("div", {"id": "ch-postdate"}).span.text
                    print(news_link, pub_date)
                    if pub_date == self.asof_date:
                        latest_news_links.append(news_link)
                except TypeError:  # Skips div tags mainly for styling
                    pass

            # Add random delay per page access to avoid bot-behavior
            time.sleep(5 + random.randint(0, 5))

        assert latest_news_links, f"No news from {self.asof_date} were fetched."

        news_data = []

        for news_link in latest_news_links:
            article_page = requests.get(news_link).text
            article_soup = BeautifulSoup(article_page, "lxml")

            # Get news title
            title = article_soup.find("h1", {"class": "entry-title"}).text
            # Get news content
            page_body = article_soup.find("div", {"id": "article_content"})
            paragraphs = page_body.find_all("p", {"class": ""})
            content = ""
            for paragraph in paragraphs:
                content += (
                    f"{paragraph.text}\n "  # Populate by concatenating each paragraph
                )

            # Add to data list
            news_data.append({"Title": title, "Content": content, "Link": news_link})

        return news_data
