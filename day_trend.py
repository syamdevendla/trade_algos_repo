import pandas as pd

class DayTrend:
    def __init__(self, time_period):
        self.time_period = time_period

    def generateSignal(self, df):
        print("entered day_trend generateSignal: ", len(df.index))
        volume_data = df
        # Assume `volume_data` is a DataFrame containing the market profile data, with columns "Price" and "Volume"
        value_area_high = volume_data.loc[volume_data['Volume'].rolling(window=int(len(volume_data)*0.7)).sum().idxmax()]
        value_area_low = volume_data.loc[volume_data['Volume'].rolling(window=int(len(volume_data)*0.7)).sum().idxmin()]

        print("Value Area High: Price = ", value_area_high["High"])
        print("Value Area Low: Price = ", value_area_low["Low"])