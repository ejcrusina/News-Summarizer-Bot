## Run


import os
import sys
from src.logger import logging
from src.exception import CustomException
import pandas as pd

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

if __name__ == "__main__":
    obj = DataIngestion()
    (
        train_data_path,
        test_data_path,
    ) = obj.initiate_data_ingestion()  # Its returning train data & and test data
    # so variable name adha kudukurom
    # raw data no need because namma pipeline diagram la first data ingestion block vandhu
    # raw data va input vangitu train data and test data va dha return pannum

    data_transformation = DataTransformation()
    train_arr, test_arr, _ = data_transformation.initiate_data_transformation(
        train_data_path, test_data_path
    )

    model_trainer = ModelTrainer()
    model_trainer.initiate_model_training(train_arr, test_arr)


class EditNewsStorage:
    def __init__(self) -> None:
        pass

    def insert_news(news_data_list: list) -> None:
        """Inserts one news record in DynamoDB table.

        Parameters
        ----------
        news_data_list : list
            List of dictionaries with all key-value pairs of a news.
        """
        print("Inserting news...")
        for news_data in news_data_list:
            # Insert 1 news
            response = news_nosql_db.put_item(Item=news_data)
            print(response)

        return print("Done insert!")
