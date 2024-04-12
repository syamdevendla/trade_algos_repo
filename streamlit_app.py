import streamlit as st

from breakout_pattern import BreakoutSignal
from day_trend import DayTrend
from momentun_signals import MomentumSignal
import matplotlib.pyplot as plt
import datetime as dt
from datetime import timedelta

import plotly.graph_objects as plotly_go
import yfinance as yf


def day_trend(instrument):
    col1, col2, col3 = st.columns(3)
    today = dt.datetime.now()
    st.write("Important levels for the selected date")
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=today,
            max_value=today
        )
    prev_day = start_date - timedelta(days=1)
    end_date = today
    df = yf.download(instrument, prev_day, end_date)
    count = len(df.index)
    while count == 0:
        start_date = prev_day - timedelta(days=1)
        end_date = prev_day
        df = yf.download(instrument, start_date, end_date)
        count = len(df.index)
        prev_day = start_date

    df = yf.download(instrument, period="1d", interval="15m")

    day_trend_data = DayTrend(time_period="daily")
    df_instrument = day_trend_data.generateSignal(df)


def overall_trend(df, instrument):
    momentum_signal = MomentumSignal(time_period="daily")
    df_instrument = momentum_signal.generateSignal(df)

    last_valid_index = df_instrument['signal'].last_valid_index()
    if last_valid_index is not None:
        last_valid_value = df_instrument.loc[last_valid_index, 'signal']
        singaled_close_value = df_instrument.loc[last_valid_index, 'Close']

    df_instrument.sort_index(inplace=True)
    prev_signal = None
    prev_index = None
    latest_change_index = None
    for index, signal in reversed(list(df_instrument['signal'].items())):
        if prev_signal is None:
            prev_signal = signal
            continue
        if signal != prev_signal:
            latest_change_index = prev_index
            break
        prev_index = index
        prev_signal = signal

    if latest_change_index is not None:
        singaled_close_value = df_instrument.loc[latest_change_index, 'Close']

    latest_close_value = df_instrument['Close'].iloc[-1]

    # Calculate the percentage change
    percentage_change = ((latest_close_value - singaled_close_value) / singaled_close_value) * 100

    col1, col2, col3 = st.columns(3)

    if last_valid_value == 1:
        with col1:
            st.write("Major Trend: UP")
    else:
        with col1:
            st.write("Major Trend: DOWN")
    with col2:
        st.write("Signal: " + format(singaled_close_value, ".2f"))
        st.write("Close: " + format(latest_close_value, ".2f"))

    with col3:
        if last_valid_value == 1:
            st.write("percentage change: " + format(percentage_change, ".2f"))
        else:
            st.write("Return: -" + format(percentage_change, ".2f") + " %")

    plt.rcParams['figure.figsize'] = 12, 6
    plt.grid(True, alpha=.3)
    plt.plot(df_instrument.iloc[-252:]['Close'], label=instrument)
    # plt.plot(df_instrument.iloc[-252:]['9-day'], label='9-day')
    # plt.plot(df_instrument.iloc[-252:]['21-day'], label='21-day')
    # plt.plot(df_instrument.iloc[-252:]['MFI'], label='MFI')
    plt.plot(df_instrument[-252:].loc[df_instrument.entry == 2].index,
             df_instrument[-252:]['9-day'][df_instrument.entry == 2], '^',
             color='g', markersize=12)
    plt.plot(df_instrument[-252:].loc[df_instrument.entry == -2].index,
             df_instrument[-252:]['21-day'][df_instrument.entry == -2], 'v',
             color='r', markersize=12)
    plt.legend(loc=2)
    st.pyplot(plt)


def breakout_signal(df):
    bo_signal = BreakoutSignal(time_period="daily")
    df_instrument = bo_signal.generateSignal(df)
    print(df_instrument.columns)

    dfpl = df_instrument
    fig = plotly_go.Figure(data=[plotly_go.Candlestick(x=dfpl.index,
                                                       open=dfpl['Open'],
                                                       high=dfpl['High'],
                                                       low=dfpl['Low'],
                                                       close=dfpl['Close'],
                                                       )])

    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=5, color="MediumPurple"),
                    name="pivot")

    fig.update_layout(xaxis_rangeslider_visible=False)

    st.write(fig)

    # st.plotly_chart(fig, theme='streamlit')


class MyStreamlitApp:
    def __init__(self):
        self.title = "Momentum Finder"

    def run(self):
        st.title(self.title)
        st.write("Welcome to my Momentum finder app!")

        today = dt.datetime.now()
        prev_year = today.year - 1
        col1, col2, col3 = st.columns(3)
        instrument = "NVDA"
        with col1:
            instrument = st.selectbox(
                'Select instrument',
                ('GLD', 'MSFT', 'AAPL', 'NVDA', 'GOOGL',
                 "ICICIBANK.NS", "^NSEI", "^NSEBANK",
                 'AMZN', 'META', 'IBN', 'INFY'))
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

        # data_dj = yf.download(djia_symbol, period=“ytd”, interval=“1d”)

        # @st.cache(persist=True)
        #st.cache_resource

        def get_df():
            df1 = yf.download(instrument, start_date, end_date)
            return df1

        df = get_df()

        tab1, tab2, tab3 = st.tabs(["Overall-trend", "break-Out", "day-Trend"])
        with tab1:
            overall_trend(df, instrument)
            # day_trend(instrument)
        # with tab2:
        # breakout_signal(df)


if __name__ == "__main__":
    my_app = MyStreamlitApp()
    my_app.run()
