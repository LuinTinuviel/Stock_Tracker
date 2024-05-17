import requests
import json
import yfinance as yf
from collections import OrderedDict
from twilio.rest import Client


# Load parameters
with open("api_parameters.json") as data_file:
    api_params = json.load(data_file)


def get_news():
    response = requests.get(url=api_params["news"]["endpoint"],
                            params=api_params["news"]["parameters"])
    response.raise_for_status()
    data = response.json()
    print(data["articles"])
    return data["articles"]


def get_yahoo_stock_data():
    data = yf.Ticker(api_params["stock"]["stock_name"])

    dict_data = data.history(period="5d").to_dict()["Close"]
    o_dict_data = OrderedDict(sorted(dict_data.items(), key=lambda x: x[0], reverse=False))

    last_day = o_dict_data.popitem()[1]
    previous_day = o_dict_data.popitem()[1]
    print(last_day, previous_day)

    difference = (last_day - previous_day)
    print(f"Difference: {difference}")

    percentage_difference = difference / last_day * 100
    print(f"Percentage Difference: {percentage_difference}")

    if percentage_difference > 3:
        print("Check news")
        articles = get_news()
        shares_diff = round(percentage_difference, 1)
        sign = "🔺" if shares_diff > 0 else "🔻"
        for article in articles:
            message = prepare_sms_message(sign, shares_diff, article)
            send_notification(message)


def prepare_sms_message(sign, shares_diff, article):
    top = f'{api_params["stock"]["stock_name"]}: {sign}{shares_diff}'
    header = f'Header: {article["title"]}'
    brief = f'Brief: {article["description"]}'
    message = f"{top}\n{header}\n{brief}"
    print(message)
    return message


def send_notification(message):
    client = Client(api_params["twilio"]["account_sid"], api_params["twilio"]["auth_token"])
    message = client.messages \
        .create(
        body=message,
        from_=api_params["twilio"]["from_number"],
        to=api_params["twilio"]["to_number"]
    )
    print(message.status)

get_yahoo_stock_data()

