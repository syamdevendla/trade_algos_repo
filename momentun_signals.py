import numpy as np
import pandas as pd
# import pandas_datareader as pdr
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf


class MomentumSignal:
    def __init__(self, time_period):
        self.time_period = time_period

    def generateSignal(self, df):
        print("entered generateSignal")

        # gld = pdr.get_data_yahoo('GLD')
        # day = np.arange(1, len(gld) + 1)
        # gld['day'] = day
        # gld.head()
        # company = 'TATAELXSI.NS'

        # Define a start date and End Date
        # start = dt.datetime(2023, 1, 1)
        # end = dt.datetime(2024, 1, 1)

        # Read Stock Price Data
        #gld = yf.download(instrument, start_date, end_date)
        gld = df

        day = np.arange(1, len(gld) + 1)
        gld['day'] = day
        #gld.drop(columns=['Adj Close'], inplace=True)
        gld = gld[['day', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # gld.info()

        gld.loc[:, '9-day'] = gld['Close'].rolling(9).mean()
        gld.loc[:, '21-day'] = gld['Close'].rolling(21).mean()

        gld.loc[:, 'signal'] = np.where(gld['9-day'] > gld['21-day'], 1, 0)
        gld.loc[:, 'signal'] = np.where(gld['9-day'] < gld['21-day'], -1, gld['signal'])

        gld.dropna(inplace=True)

        gld.loc[:, 'return'] = np.log(gld['Close']).diff()
        gld.loc[:, 'system_return'] = gld['signal'] * gld['return']
        gld.loc[:, 'entry'] = gld.signal.diff()
        #print(gld.head())

        return money_flow_index(gld, 14)


        # plt.show()

        print("************end here***********************")

        # columns_list1 = gld.columns
        # print("Columns using .columns attribute:", columns_list1)


def money_flow_index(df, n):
    # Calculate the typical price
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3

    # Calculate the raw money flow
    raw_money_flow = typical_price * df['Volume']

    # Calculate the positive and negative money flows
    positive_money_flow = (raw_money_flow * (typical_price > typical_price.shift(1))).fillna(0)
    negative_money_flow = (raw_money_flow * (typical_price < typical_price.shift(1))).fillna(0)

    # Calculate the money flow ratios
    money_flow_ratio = positive_money_flow.rolling(n).sum() / negative_money_flow.rolling(n).sum()

    # Calculate the Money Flow Index (MFI)
    mfi = 100 - (100 / (1 + money_flow_ratio))

    df['MFI'] = mfi
    return df

# Example usage:
# if __name__ == "__main__":
# Initialize MomentumSignal class with a time_period
# momentum_signal = MomentumSignal(time_period="daily")
# momentum_signal.generateSignal()
# print("MomentumSignal")
