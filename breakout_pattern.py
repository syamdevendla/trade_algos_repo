
#import pandas_ta as ta
import pandas as pd
#from scipy import stats
import numpy as np
import yfinance as yf


class BreakoutSignal:
    def __init__(self, time_period):
        self.time_period = time_period

    def addEMASignal(self, df):
        EMAsignal = [0]*len(df)
        backcandles = 15

        for row in range(backcandles, len(df)):
            upt = 1
            dnt = 1
            for i in range(row-backcandles, row+1):
                if max(df.open[i], df.close[i])>=df.EMA[i]:
                    dnt=0
                if min(df.open[i], df.close[i])<=df.EMA[i]:
                    upt=0
            if upt==1 and dnt==1:
                EMAsignal[row]=3
            elif upt==1:
                EMAsignal[row]=2
            elif dnt==1:
                EMAsignal[row]=1

        df['EMASignal'] = EMAsignal

    def generateSignal(self, df):

        df=df[df['Volume']!=0]
        df.reset_index(drop=True, inplace=True)
        day = np.arange(1, len(df) + 1)
        df['day'] = day
        #df.drop(columns=['Adj Close'], inplace=True)
        df = df[['day', 'Open', 'High', 'Low', 'Close', 'Volume']]



        def isPivot(candle, window):
            """
            function that detects if a candle is a pivot/fractal point
            args: candle index, window before and after candle to test if pivot
            returns: 1 if pivot high, 2 if pivot low, 3 if both and 0 default
            """
            #candle = df.index.get_loc(candle_index)

            if candle-window < 0 or candle+window >= len(df):
                return 0

            pivotHigh = 1
            pivotLow = 2
            for i in range(candle-window, candle+window+1):
                if df.iloc[candle].Low > df.iloc[i].Low:
                    pivotLow=0
                if df.iloc[candle].High < df.iloc[i].High:
                    pivotHigh=0
            if (pivotHigh and pivotLow):
                return 3
            elif pivotHigh:
                return pivotHigh
            elif pivotLow:
                return pivotLow
            else:
                return 0


        def pointpos(row):
            zone_width = 0.05
            if row['isPivot'] == 2:  # Pivot Low
                return row['Low'] - zone_width
            elif row['isPivot'] == 1:  # Pivot High
                return row['High'] + zone_width
            else:
                return np.nan

        def detect_structure(candle, backcandles, window):
            """
            Attention! window should always be greater than the pivot window! to avoid look ahead bias
            """

            if (candle <= (backcandles+window)) or (candle+window+1 >= len(df)):
                return 0

            localdf = df.iloc[candle-backcandles-window:candle-window] #window must be greater than pivot window to avoid look ahead bias
            highs = localdf[localdf['isPivot'] == 1].High.tail(3).values
            lows = localdf[localdf['isPivot'] == 2].Low.tail(3).values

            levelbreak = 0
            zone_width =  0.05
            if len(lows)==3:
                support_condition = True
                mean_low = lows.mean()
                for low in lows:
                    if abs(low-mean_low)>zone_width:
                        support_condition = False
                        break
                if support_condition and (mean_low - df.loc[candle].Close)>zone_width*2:
                    levelbreak = 1

            if len(highs)==3:
                resistance_condition = True
                mean_high = highs.mean()
                for high in highs:
                    if abs(high-mean_high)>zone_width:
                        resistance_condition = False
                        break
                if resistance_condition and (df.loc[candle].Close-mean_high)>zone_width*2:
                    levelbreak = 2

            return levelbreak

        #window=10
        #df['isPivot'] = df.apply(lambda x: isPivot(x.name, window), axis=1)
        #df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)

        window = 10
        df['isPivot'] = [isPivot(i, window) for i in range(len(df))]
        df['pointpos'] = df.apply(pointpos, axis=1)
        df['pattern_detected'] = [detect_structure(i, backcandles=60, window=11) for i in range(len(df))]


        #df['pattern_detected'] = df.apply(lambda row: detect_structure(row.name, backcandles=60, window=11), axis=1)
        df1 = df['pattern_detected']!=0
        print(df1)
        return df


