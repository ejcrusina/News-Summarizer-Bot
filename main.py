from datetime import date, timedelta

from dotenv import dotenv_values

from src.components.scrape_dataset import NewsScraper
from src.logger import CustomLogger
from src.pipeline.email_pipeline import EmailNews
from src.pipeline.export_pipeline import CalculateNewsStorage, EditNewsStorage
from src.pipeline.prediction_pipeline import SummarizerLLM

logger = CustomLogger(__name__)

# Assign global vars
config = dotenv_values(".env")

# NOTE - uncomment in prod
TODAY = date.today()
PREV_DATE = TODAY + timedelta(-1)
# PREV_DATE = date(2024, 1, 28)


# Scrape latest news
scraper = NewsScraper(
    url="https://newsinfo.inquirer.net/category/nation",
    total_page=2,
    asof_date=PREV_DATE,
)
news_data = scraper.scrape_inquirer()

logger.info("Summarizing all latest news data...")
# Initialize LLM that summarizes news
summarizer_llm = SummarizerLLM().hf_longt5()
# Add key "Summary" with summary of news content to the orig dict of each news
news_data_final = [
    dict(
        news_dict,
        **{"Summary": summarizer_llm(news_dict["Content"])[0]["summary_text"]},
    )
    for news_dict in news_data
]
logger.info("All news data were successfully summarized!")


# Email the summarized news as a newsletter
emailer = EmailNews(sender=config["SENDER_EMAIL"])
emailer.send_gmail_html(
    receiver=config["RECEIVER_EMAIL"],
    news_data=news_data_final,
    asof_date=PREV_DATE,
)


# Add IDs to each news before loading to storage
news_data_final = CalculateNewsStorage(
    table_name="news-data-last3days", latest_date=PREV_DATE
).create_news_ids(news_data_final)


# Initialize DynamoDB operator
nosql_edit = EditNewsStorage(table_name="news-data-last3days", latest_date=PREV_DATE)

# INSERT latest news
nosql_edit.insert_news(news_data_list=news_data_final)
# QUERY old news
news_to_delete = nosql_edit.get_old_news_to_delete()
# DELETE old news
nosql_edit.batch_delete_old_news(news_to_delete=news_to_delete)

logger.info("All News Summarizer Operations Completed!")
