import pandas as pd
import numpy as np

class DayTrend:
    def __init__(self, time_period):
        self.time_period = time_period

    def generateSignal(self, df):
        print("entered day_trend generateSignal: ", len(df.index))
        #print("columns:", df.columns)

        # Calculate the typical price
        df['Typical Price'] = (df['High'] + df['Low'] + df['Close']) / 3

        # Identify the Point of Control (POC), which is the price level with the highest volume
        poc_index = df['Volume'].idxmax()
        poc = df.loc[poc_index, 'Typical Price']

        # Calculate the 70th percentile of volume
        value_area_volume = np.percentile(df['Volume'], 70)

        # Filter the DataFrame to include only the rows within the value area
        value_area_df = df[df['Volume'].cumsum() <= value_area_volume]

        # Calculate VAH and VAL based on the typical price within the value area
        vah = value_area_df['Typical Price'].max()
        val = value_area_df['Typical Price'].min()

        #print("POC:", poc)
        #print("VAH:", vah)
        #print("VAL:", val)

        highest_high = df['High'].max()
        lowest_low = df['Low'].min()
        final_close = df['Close'].iloc[-1]

        #print("Highest High:", highest_high)
        #print("Lowest Low:", lowest_low)
        #print("Final Close:", final_close)

        return [poc, vah, val, highest_high, lowest_low, final_close]

    def initiative_buying_selling_daily(self, instrument, df):
        #df = self.get_monthly_data(instrument)
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
