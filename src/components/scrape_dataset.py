import random
import time
from datetime import date

import requests
from bs4 import BeautifulSoup

from src.logger import CustomLogger


logger = CustomLogger(__name__)


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
        ASOF_STR = self.asof_date.strftime("%B %d, %Y")
        latest_news_links = []

        logger.info("Started scraping Inquirer website..")

        for page_no in range(1, self.total_page + 1):
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
                logger.warning(
                    f"Failed to fetch articles from page {page_no} after 5 attempts."
                )
                continue

            for article in articles:
                try:
                    news_link = article.a["href"]
                    pub_date = article.find("div", {"id": "ch-postdate"}).span.text
                    print(pub_date, news_link)
                    if pub_date == ASOF_STR:
                        latest_news_links.append(news_link)
                except TypeError:  # Skips div tags mainly for styling
                    pass

            # Add random delay per page access to avoid bot-behavior
            time.sleep(5 + random.randint(0, 5))

        try:
            assert latest_news_links
        except AssertionError:
            logger.error(f"No news from {ASOF_STR} were fetched.")

        logger.info("Inquirer news were successfully scraped!")

        # Get all LATEST news
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


if __name__ == "__main__":
    ## Manual assign
    PREV_DATE = date(2024, 1, 24)
    scraper = NewsScraper(
        url="https://newsinfo.inquirer.net/category/nation",
        total_page=4,
        asof_date=PREV_DATE_STR,
    )
    news_data = scraper.scrape_inquirer()
