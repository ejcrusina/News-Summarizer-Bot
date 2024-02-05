import os
import sys

import openai
import pandas as pd
from dotenv import dotenv_values
from langchain import LLMChain, OpenAI, PromptTemplate
from transformers import pipeline

from src.exception import CustomException
from src.logger import logging
from src.utils import load_object
from src.logger import CustomLogger


# config = dotenv_values(".env")
config = os.environ
logger = CustomLogger(__name__)


class SummarizerLLM:
    def __init__(self) -> None:
        pass

    def openai_gpt(self):
        openai.api_key = config["OPENAI_API_KEY"]

        template = """
            You are an expert journalist and a reader that can highlight the most important points written in a news article; 
            You need to summarize a news article in just 1 sentence similar to a headline but more descriptive. 
            Add a second sentence only if necessary. Limit the total words between 20 to 30 words and do not use too many commas. Make it sound logical;

            TITLE: {title}
            CONTENT: {content}
        """

        prompt = PromptTemplate(template=template, input_variables=["title", "content"])

        summarizer_llm = LLMChain(
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1),
            prompt=prompt,
            verbose=True,
        )

        return summarizer_llm

    def hf_longt5(self):
        summarizer_llm = pipeline(
            "summarization",
            "pszemraj/long-t5-tglobal-base-16384-book-summary",
            max_length=256,
        )

        return summarizer_llm


class PredictPipeline:
    def __init__(self):
        pass

    logging.info("Prediction Pipeline Started")

    def predict(self, features):
        try:
            preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")
            model_path = os.path.join("artifacts", "model.pkl")

            preprocessor = load_object(preprocessor_path)
            model = load_object(model_path)

            data_scaled = preprocessor.transform(features)

            pred = model.predict(data_scaled)
            logging.info("Prediction Pipeline Class ended")
            return pred

        except Exception as e:
            logging.info("Exception occured in prediction pipeline")
            raise CustomException(e, sys)


class CustomData:
    def __init__(
        self,
        Gender: str,
        Customer_Type: str,
        Age: float,
        Type_of_Travel: str,
        Class: str,
        Flight_Distance: float,
        Inflight_wifi_service: float,
        Departure_or_Arrival_time_convenient: float,
        Ease_of_Online_booking: float,
        Gate_location: float,
        Food_and_drink: float,
        Online_boarding: float,
        Seat_comfort: float,
        Inflight_entertainment: float,
        On_board_service: float,
        Leg_room_service: float,
        Baggage_handling: float,
        Checkin_service: float,
        Inflight_service: float,
        Cleanliness: float,
        Departure_Delay_in_Minutes: float,
        Arrival_Delay_in_Minutes: float,
    ):
        self.Gender = Gender
        self.Customer_Type = Customer_Type
        self.Age = Age
        self.Type_of_Travel = Type_of_Travel
        self.Class = Class
        self.Flight_Distance = Flight_Distance
        self.Inflight_wifi_service = Inflight_wifi_service
        self.Departure_or_Arrival_time_convenient = Departure_or_Arrival_time_convenient
        self.Ease_of_Online_booking = Ease_of_Online_booking
        self.Gate_location = Gate_location
        self.Food_and_drink = Food_and_drink
        self.Online_boarding = Online_boarding
        self.Seat_comfort = Seat_comfort
        self.Inflight_entertainment = Inflight_entertainment
        self.On_board_service = On_board_service
        self.Leg_room_service = Leg_room_service
        self.Baggage_handling = Baggage_handling
        self.Checkin_service = Checkin_service
        self.Inflight_service = Inflight_service
        self.Cleanliness = Cleanliness
        self.Departure_Delay_in_Minutes = Departure_Delay_in_Minutes
        self.Arrival_Delay_in_Minutes = Arrival_Delay_in_Minutes

    def get_data_as_dataframe(self):
        try:
            custom_data_input_dict = {
                "Gender": [self.Gender],
                "Customer_Type": [self.Customer_Type],
                "Age": [self.Age],
                "Type_of_Travel": [self.Type_of_Travel],
                "Class": [self.Class],
                "Flight_Distance": [self.Flight_Distance],
                "Inflight_wifi_service": [self.Inflight_wifi_service],
                "Departure_or_Arrival_time_convenient": [
                    self.Departure_or_Arrival_time_convenient
                ],
                "Ease_of_Online_booking": [self.Ease_of_Online_booking],
                "Gate_location": [self.Gate_location],
                "Food_and_drink": [self.Food_and_drink],
                "Online_boarding": [self.Online_boarding],
                "Seat_comfort": [self.Seat_comfort],
                "Inflight_entertainment": [self.Inflight_entertainment],
                "On_board_service": [self.On_board_service],
                "Leg_room_service": [self.Leg_room_service],
                "Baggage_handling": [self.Baggage_handling],
                "Checkin_service": [self.Checkin_service],
                "Inflight_service": [self.Inflight_service],
                "Cleanliness": [self.Cleanliness],
                "Departure_Delay_in_Minutes": [self.Departure_Delay_in_Minutes],
                "Arrival_Delay_in_Minutes": [self.Arrival_Delay_in_Minutes],
            }
            df = pd.DataFrame(custom_data_input_dict)
            logging.info("Dataframe Gathered")
            return df

        except Exception as e:
            logging.info("Exception Occured in prediction pipeline")
            raise CustomException(e, sys)
