import numpy as np
import pandas as pd
# import pandas_datareader as pdr
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
from datetime import datetime, timedelta



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
        # gld = yf.download(instrument, start_date, end_date)
        gld = df

        day = np.arange(1, len(gld) + 1)
        gld['day'] = day
        # gld.drop(columns=['Adj Close'], inplace=True)
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
        # print(gld.head())

        return money_flow_index(gld, 14)

        # plt.show()

        print("************end here***********************")

        # columns_list1 = gld.columns
        # print("Columns using .columns attribute:", columns_list1)

    def get_last_month_imp_levels(self, instrument):
        df = self.get_monthly_data(instrument)
        # day_trend_data = DayTrend(time_period="daily")
        # list_instrument = day_trend_data.generateSignal(df)
        volume_profile = df.groupby(pd.cut(df['Close'], bins=20))['Volume'].sum()

        # Calculate cumulative sum of volume profile
        cumulative_volume_profile = volume_profile.cumsum()

        # Calculate total volume
        total_volume = cumulative_volume_profile.iloc[-1]

        # Calculate value area (70%)
        value_area = cumulative_volume_profile[cumulative_volume_profile <= total_volume * 0.7]

        # Calculate VAH, VAL, and POC
        vah = value_area.index.max().right
        val = value_area.index.min().left
        poc = volume_profile.idxmax()

        highest_high = df['High'].max()
        lowest_low = df['Low'].min()
        final_close = df['Close'].iloc[-1]

        return [poc, vah, val, highest_high, lowest_low, final_close]

    def initiative_buying_selling(self, instrument):
        df = self.get_monthly_data(instrument)
        # Calculate price movements
        df['Price Movement'] = df['Close'] - df['Open']

        # Calculate volume weighted average price (VWAP)
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()

        # Calculate percentage thresholds
        price_movement_threshold_percent = 1.0  # Example threshold for significant price movement (1%)
        volume_threshold_percent = 0.5  # Example threshold for high volume (0.5% of average volume)

        # Calculate absolute thresholds based on percentages
        average_volume = df['Volume'].mean()
        price_movement_threshold = price_movement_threshold_percent / 100 * df['Close'].mean()
        volume_threshold = volume_threshold_percent / 100 * average_volume

        # Identify initiative buying and selling
        df['Initiative'] = 'None'
        df.loc[(df['Price Movement'] > price_movement_threshold) & (
                df['Volume'] > volume_threshold), 'Initiative'] = 'Buying'
        df.loc[(df['Price Movement'] < -price_movement_threshold) & (
                df['Volume'] > volume_threshold), 'Initiative'] = 'Selling'

        return df

    # def get_daily_data(self, instrument, df):

    #   return df

    def get_monthly_data(self, instrument):
        # Get the current date and time
        current_date = datetime.now()

        # Get the first day of the current month
        first_day_of_current_month = current_date.replace(day=1)

        # Subtract one day to get the last day of the previous month
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

        # Extract the year and month of the previous month
        previous_month_year = last_day_of_previous_month.year
        previous_month = last_day_of_previous_month.month

        # Calculate the start date as the first day of the previous month
        start_date = datetime(previous_month_year, previous_month, 1).strftime('%Y-%m-%d')

        # Calculate the end date as the last day of the previous month
        # end_date = last_day_of_previous_month.strftime('%Y-%m-%d')
        end_date = first_day_of_current_month.strftime('%Y-%m-%d')

        # print(start_date, end_date)
        # Fetch historical data from Yahoo Finance
        df = yf.download(instrument, start=start_date, end=end_date)
        return df


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
    # print("mfi: ", mfi)
    df['MFI'] = mfi
    return df

# Example usage:
# if __name__ == "__main__":
# Initialize MomentumSignal class with a time_period
# momentum_signal = MomentumSignal(time_period="daily")
# momentum_signal.generateSignal()
# print("MomentumSignal")
