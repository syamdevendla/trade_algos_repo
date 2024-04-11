import streamlit as st
from momentun_signals import MomentumSignal
import matplotlib.pyplot as plt
import datetime as dt


class MyStreamlitApp:
    def __init__(self):
        self.title = "Momentum Finder"

    def run(self):
        st.title(self.title)
        st.write("Welcome to my Momentum finder app!")

        today = dt.datetime.now()
        prev_year = today.year - 1
        col1, col2, col3 = st.columns(3)
        with col1:
            instrument = st.selectbox(
                'Select instrument',
                ('GLD', 'MSFT', 'AAPL', 'NVDA', 'GOOGL', 'AMZN', 'META', 'IBN', 'INFY'))
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=dt.date(prev_year, 1, 1),
                max_value=today
            )

        with col3:
            end_date = st.date_input(
                "End Date",
                max_value=today
            )
        print(start_date)
        momentum_signal = MomentumSignal(time_period="daily")
        df_instrument = momentum_signal.generateSignal(instrument,start_date,end_date)

        last_valid_index = df_instrument['signal'].last_valid_index()
        # Get the last non-null value from column 'A'
        last_valid_value = df_instrument.loc[last_valid_index, 'signal']

        if last_valid_value == 1:
            st.write("Current Trend: UP")
        else:
            st.write("Current Trend: DOWN")

        plt.rcParams['figure.figsize'] = 12, 6
        plt.grid(True, alpha=.1)
        plt.plot(df_instrument.iloc[-252:]['Close'], label=instrument)
        #plt.plot(df_instrument.iloc[-252:]['9-day'], label='9-day')
        #plt.plot(df_instrument.iloc[-252:]['21-day'], label='21-day')
        plt.plot(df_instrument.iloc[-252:]['MFI'], label='MFI')
        plt.plot(df_instrument[-252:].loc[df_instrument.entry == 2].index, df_instrument[-252:]['9-day'][df_instrument.entry == 2], '^',
                 color='g', markersize=12)
        plt.plot(df_instrument[-252:].loc[df_instrument.entry == -2].index, df_instrument[-252:]['21-day'][df_instrument.entry == -2], 'v',
                 color='r', markersize=12)
        plt.legend(loc=2)
        st.pyplot(plt)


if __name__ == "__main__":
    my_app = MyStreamlitApp()
    my_app.run()
