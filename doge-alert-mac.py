import requests
import datetime
import time
import random
import json
import matplotlib.pyplot as plt
from config import *
import pync


import pandas as pd

def get_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_formatted_datetime(date=datetime.datetime.now()):
    return date.strftime('%Y-%m-%d')


def get_historical_data_from_coindesk(start, end=None):
    # code from https://github.com/dursk/bitcoin-price-api/blob/master/exchanges/coindesk.py
    if not end:
        end = get_formatted_datetime()
        ## todo get hourly data
    url = (
        'https://api.coindesk.com/v1/bpi/historical/close.json'
        '?start={}&end={}'.format(
            start, end
        )
    )
    return get_response(url)



def bollinger_bands_algorithm_on_historical_data(window=20, std_diff=2.0 ):
    start = get_formatted_datetime(datetime.datetime.now() - datetime.timedelta(days=90))
    prices = get_historical_data_from_coindesk(start)
    df_price = pd.Series(prices['bpi'], name='DateValue').to_frame("price")
    df_avg = df_price.rolling(window).mean()  # pd.rolling_mean(df_price, window=window)
    df_std =  df_price.rolling(window).std()
    df_upper_band = df_avg + (df_std *std_diff )
    df_lower_band = df_avg - (df_std * std_diff)

    # ax= df_price.plot()
    # df_upper_band.plot(ax=ax)
    # df_lower_band.plot(ax=ax)
    # plt.show()
    return df_upper_band, df_lower_band


def current_coinbase_price ():


    buy_price = get_response("https://api.coinbase.com/v2/prices/buy?currency=USD")["data"]["amount"]
    sell_price = get_response("https://api.coinbase.com/v2/prices/sell?currency=USD")["data"]["amount"]
    return float(buy_price), float(sell_price)



def send_notification(message):
    print(message)

    pync.notify(message)



    # slack_data = {'text': message, "channel":SLACK_CHANNEL, "username": SLACK_USER, "icon_emoji":SLACK_ICON}
    #
    # response = requests.post(
    #     WEBHOOK_URL, data=json.dumps(slack_data),
    #     headers={'Content-Type': 'application/json'}
    # )
    # if response.status_code != 200:
    #     raise ValueError(
    #         'Request to slack returned an error %s, the response is:\n%s'
    #         % (response.status_code, response.text)
    #     )

def analyze():
    lookback_days = 3
    std_diff = 2
    df_upper, df_lower = bollinger_bands_algorithm_on_historical_data(lookback_days, std_diff)
    forecast = "HOLD" # "HOLD", "BUY", "SELL"
    while True:
        prev_forecast = forecast
        today = get_formatted_datetime()
        if df_upper.index[-1] != today:
            df_upper, df_lower = bollinger_bands_algorithm_on_historical_data(lookback_days, std_diff)

        buy_price, sell_price  = current_coinbase_price()
        optimal_buy= df_lower.iloc[-1][0]
        optimal_sell= df_upper.iloc[-1][0]

        if buy_price < optimal_buy:
            forecast = "BUY"

        elif (sell_price > optimal_sell):
            forecast = "SELL"
        else:
            forecast = "HOLD"

        if (prev_forecast != forecast):

            pre = random.choice(['According to analysis: ', 'According to bollinger bands algorithm: ', 'Forecast says: '])

            if forecast == "BUY":
                msg = pre + "Buy Bitcoins. Coinbase is selling bitcoin at a price of {0}. This exceeds optimal buy price of {1} based on {2} days history.".format(buy_price, round(optimal_buy), lookback_days)
                send_notification(msg )
            elif forecast == "SELL":
                msg = pre + "Sell your Bitcoins. Coinbase is buying bitcoin at a price of {0}. This exceeds optimal sell price of {1} based on {2} days history".format(sell_price, round(optimal_sell), lookback_days)
                send_notification(msg)
            else:
                send_notification("Coinbase buy price: " + buy_price + "Coinbase sell price: " + sell_price + ". Analysis recommands that you hold on to your bitcoins")
        time.sleep(RERUN_TIME)


if __name__ == "__main__":
    analyze()

