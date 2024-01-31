import warnings
from datetime import date, datetime, timedelta

from boto3 import resource
from boto3.dynamodb.conditions import Key

from src.logger import CustomLogger


logger = CustomLogger(__name__)


class CalculateNewsStorage:
    def __init__(self, table_name, latest_date) -> None:
        self.nosql_table = resource("dynamodb").Table(table_name)
        self.latest_date = latest_date

    def create_news_ids(self, news_data: dict) -> dict:
        """Adds IDs for each news data in DynamoDB table

        Parameters
        ----------
        news_data : dict
            News data with complete keys to be stored

        Returns
        -------
        dict
            News data with additional IDs and CreationDate per news
        """
        # Add IDs for DynamoDB table
        LATEST_DATE_ID = self.latest_date.strftime("%Y%m%d")

        for idx, _ in enumerate(news_data):
            news_data[idx]["dateID"] = LATEST_DATE_ID
            news_data[idx]["newsID"] = (
                LATEST_DATE_ID + "-" + str(len(news_data) - idx)
            )  # Start ID as 1 for the last news_data in list
            news_data[idx]["CreationDate"] = datetime.now().isoformat()

        return news_data

    def count_news_with_dateID(self, news_dateID: str) -> int:
        """Returns the number of news with Partition Key of dateID

        Parameters
        ----------
        news_dateID : str
            dateID key to query in DynamoDB table.

        Returns
        -------
        int
            Total number of news with dateID Partition key.
        """
        # Query records with dateID as key
        response = {}
        filtering_exp = Key("dateID").eq(news_dateID)
        response = self.nosql_table.query(KeyConditionExpression=filtering_exp)

        # Count records
        news_list = response["Items"]
        total_news = len(news_list)
        return total_news


class EditNewsStorage:
    TODAY = date.today()

    def __init__(self, table_name, latest_date: date = None) -> None:
        self.nosql_table = resource("dynamodb").Table(table_name)
        self.latest_date = latest_date
        self.calc = CalculateNewsStorage(table_name, latest_date)

    def insert_news(self, news_data_list: list = []) -> None:
        """Inserts one news record in DynamoDB table.

        Parameters
        ----------
        news_data_list : list
            List of dictionaries with all key-value pairs of a news.
        """
        logger.info("Inserting news in DynamoDB table...")
        for news_data in news_data_list:
            # Insert 1 news
            response = self.nosql_table.put_item(Item=news_data)
            print(response)

        logger.info("Done insert!")

    def batch_delete_old_news(self, news_to_delete: list = []) -> None:
        """Delete old newsID records in DynamoDB table by batch to clear storage.

        Parameters
        ----------
        news_to_delete : list
            List of dictionaries with dateID and newsID of records to be deleted.
        """
        logger.info("Deleting old news in DynamoDB table...")
        # Break out if input is empty
        if not news_to_delete:
            logger.info("No news to delete.")

        response = {}
        # NOTE - batch delete is better if Partition Key + Sort Key pair is not unique
        # Overkill if each batch is a unique record but this is the only available method
        with self.nosql_table.batch_writer() as batch:
            for news_data in news_to_delete:
                # Delete 1 news
                part_key = news_data["dateID"]
                sort_key = news_data["newsID"]
                response = batch.delete_item(
                    Key={"dateID": part_key, "newsID": sort_key}
                )
                logger.info(f"dateID:{part_key} newsID:{sort_key} || {response}")

        # Check if the dateIDs were successfully deleted
        logger.info("Scanning again the updated table...")
        response_whole_db = self.nosql_table.scan()
        remaining_dateIDs = set([item["dateID"] for item in response_whole_db["Items"]])
        deleted_dateIDs = set([news["dateID"] for news in news_to_delete])

        try:
            assert remaining_dateIDs.isdisjoint(deleted_dateIDs)
        except AssertionError:
            logger.error("Not all dateIDs were deleted!")

        logger.info("Done deletion!")

    def count_news_with_dateID(self, news_dateID: str) -> int:
        """Returns the number of news with Partition Key of dateID

        Parameters
        ----------
        news_dateID : str
            dateID key to query in DynamoDB table.

        Returns
        -------
        int
            Total number of news with dateID Partition key.
        """
        # Query records with dateID as key
        response = {}
        filtering_exp = Key("dateID").eq(news_dateID)
        response = self.nosql_table.query(KeyConditionExpression=filtering_exp)

        # Count records
        news_list = response["Items"]
        total_news = len(news_list)
        return total_news

    def get_old_news_to_delete(self, days_to_keep: int = 3) -> list:
        """Returns unique dateIDs of old news in DynamoDB table that will be deleted to maintain limited storage.

        Parameters
        ----------
        days_to_keep : int, optional
            Number of days to look back to get min date to keep, by default 3.

        Returns
        -------
        list
            Contains dictionary of news to be deleted with Partition Key dateID and Sort Key newsID.
        """
        # Get min dateID to keep in table
        min_date_stored = self.TODAY + timedelta(-days_to_keep)
        min_date_id = min_date_stored.strftime("%Y%m%d")

        # Scan entire table
        logger.info("Scanning the entire table...")
        response_whole_db = self.nosql_table.scan()
        # Get all dateIDs so far
        old_dateIDs = set([item["dateID"] for item in response_whole_db["Items"]])
        # Select dateIDs for deletion
        delete_dateIDs = [dateID for dateID in old_dateIDs if dateID < min_date_id]
        logger.info("Done retrieving dateIDs \n")

        # Get newsID to be deleted per dateID
        logger.info("Generating newsIDs to delete...")
        news_to_delete = []
        for dateID in delete_dateIDs:
            total_news = self.calc.count_news_with_dateID(news_dateID=dateID)
            # Generate newsID based on logic of how it was made before using total record count
            newsID_list = [
                {"dateID": dateID, "newsID": dateID + "-" + str(idx + 1)}
                for idx in range(total_news)
            ]
            news_to_delete += newsID_list

        if not news_to_delete:
            logger.warning("No old records were found.")
        else:
            print("Done!")

        return news_to_delete


if __name__ == "__main__":
    news_nosql_db = resource("dynamodb").Table("news-data-last3days")
    nosql_edit = EditNewsStorage(news_nosql_db)

    # INSERT latest news
    # TODO - insert method that gives news_data_final from other file
    nosql_edit.insert_news(news_data_list=news_data_final)

    # QUERY old news
    news_to_delete = nosql_edit.get_old_news_to_delete()
    # DELETE old news
    nosql_edit.batch_delete_old_news(news_to_delete=news_to_delete)
