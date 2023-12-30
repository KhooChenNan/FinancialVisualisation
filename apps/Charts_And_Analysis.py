import datetime

import pandas as pd

import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yahoo_fin.stock_info as si
import requests
import altair as alt

from dbfx import *

def rounding_values(input_value):
    """
    This function takes an input value and rounds it to either 2 decimal places if the value is greater than 1, 
    or to 4 decimal places if the value is less than or equal to 1.

    Args:
        input_value (float): The input value to be rounded.

    Returns:
        float: The rounded output value.
    """
    if input_value.values > 1:
        a = float(round(input_value, 2))
    else:
        a = float(round(input_value, 4))
    return a

def app():
    """
    The driver code for "Charts And Analysis" web page.

    Functionalities include:
        1. Retrieving live price of the assets.
        2. Historical Cumulative Returns of assets for comparison (SPX500, DOW, NASDAQ).
        3. Volume History for Assets.
        4. Dip Finder View that calculates and displays the current price of the asset with the 200 day moving average.
    """
    
    st.markdown("##")
    st.markdown("<h1 style='text-align: center;'>Account Metrix</h1>", unsafe_allow_html=True)

    create_portfolio_table()

    date_of_purchase = datetime.datetime(2023, 4, 1)
    date_string = date_of_purchase.strftime('%Y-%m-%d')
    
	# Open connection and cursor to the database
    tconn = sqlite3.connect('portfolio.db')
    tc = tconn.cursor()

	# Execute SELECT query to count number of rows in table
    tc.execute('SELECT COUNT(*) FROM portfolio')
    count = tc.fetchone()[0]

	# Check if table is empty
    if count == 0:
		# Add data to table
        add_data("Bitcoin", "BTC", "20000", "1", "20000", "Crypto", date_string)
        add_data("Netflix", "NFLX", "300", "50", "15000", "Stocks", date_string)
        tconn.commit()

    tc.close()
    tconn.close()
    
    cumulative_returns_col, live_price_and_overview_col = st.columns([4, 3])

    # --- Cumulative returns ---
    with cumulative_returns_col:
        dow_tab, nasdaq_tab, spx500_tab = st.tabs(["Dow Jones", "Nasdaq", "S&P 500"])

        with dow_tab:
            st.markdown("<h3 style = 'text-align: center;'>Dow Jones' Cumulative Returns</h3>", unsafe_allow_html = True)
            dow_asset_dropdown, dow_start_date, dow_end_date = st.columns(3)

            with dow_asset_dropdown:
                dow_tickers = si.tickers_dow()
                dow_dropdown_input = st.multiselect('Ticker Symbol', dow_tickers, default = ["BA", "CAT"])
            with dow_start_date:
                dow_start_date_input = st.date_input('Start', value = pd.to_datetime('2020-01-01'), key = "1")
            with dow_end_date:
                dow_end_date_input = st.date_input('End', value = pd.to_datetime('today'), key = "2")

            def relativeret(df):
                rel = df.pct_change()
                cumret = (1 + rel).cumprod() - 1
                cumret = cumret.fillna(0)
                return cumret

            if len(dow_dropdown_input) > 0:
                df = relativeret(yf.download(dow_dropdown_input, dow_start_date_input, dow_end_date_input)['Adj Close'])
                st.line_chart(df, height = 550)

        with nasdaq_tab:
            st.markdown("<h3 style = 'text-align: center;'>NASDAQ's Cumulative Returns</h3>", unsafe_allow_html = True)

            nasdaq_asset_dropdown, nasdaq_start_date, nasdaq_end_date = st.columns(3)

            with nasdaq_asset_dropdown:
                nasdaq_tickers = si.tickers_nasdaq()
                nasdaq_dropdown_input = st.multiselect('Ticker Symbol', nasdaq_tickers, default = ["BZ", "ENG"])
            with nasdaq_start_date:
                nasdaq_start_date_input = st.date_input('Start', value = pd.to_datetime('2020-01-01'), key = "3")
            with nasdaq_end_date:
                nasdaq_end_date_input = st.date_input('End', value = pd.to_datetime('today'), key = "4")

            if len(nasdaq_dropdown_input) > 0:
                df = relativeret(yf.download(nasdaq_dropdown_input, nasdaq_start_date_input, nasdaq_end_date_input)['Adj Close'])
                st.line_chart(df, height = 550)

        with spx500_tab:
            st.markdown("<h3 style = 'text-align: center;'>S&P500's Cumulative Returns</h3>", unsafe_allow_html = True)

            spx500_asset_dropdown, spx500_start_date, spx500_end_date = st.columns(3)

            with spx500_asset_dropdown:
                spx500_tickers = ["AAPL", "BLK"]
                spx500_dropdown_input = st.multiselect('Ticker Symbol', spx500_tickers, default = ["BLK"])
            with spx500_start_date:
                spx500_start_date_input = st.date_input('Start', value = pd.to_datetime('2020-01-01'), key = "5")
            with spx500_end_date:
                spx500_end_date_input = st.date_input('End', value = pd.to_datetime('today'), key = "6")

            if len(spx500_dropdown_input) > 0:
                df = relativeret(yf.download(spx500_dropdown_input, spx500_start_date_input, spx500_end_date_input)['Adj Close'])
                st.line_chart(df, height = 550)
        # --- End of Cumulative returns ---

        # --- Live Price Feature ---
        # data fetching for initial phase
        df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')
        dow_tickers_live_data = si.tickers_dow()

        # request live data
        select_col1, select_col2 = st.columns(2)

        with select_col1:
            sel_stocks = st.selectbox('Stocks', dow_tickers_live_data)
        with select_col2:
            sel_coin = st.selectbox('Cryptocurrency', df.symbol, list(df.symbol).index('BTCUSDT'))

        df_coin = df[df.symbol == sel_coin]

        price_stocks = f'{si.get_live_price(sel_stocks):.2f}'
        price_coin = rounding_values(df_coin.lastPrice)

        percent_coin = f'{float(df_coin.priceChangePercent)}%'

        display_live_price_left_col, display_live_price_right_col = st.columns(2)

        display_live_price_left_col.metric(
            label = sel_stocks,
            value = price_stocks,
        )

        display_live_price_right_col.metric(
            label = sel_coin,
            value = price_coin,
            delta = percent_coin,
        )
        
        # When user presses the button
        placeholder = st.empty() # Creates a container (Stores the elements/values)

        if st.button("Request live data"):
            with placeholder.container(): # Clears the entire data within the container when pressing (Basically refreshes the container)
                df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')

                df_coin1 = df[df.symbol == sel_coin]

                price_stocks1 = f'{si.get_live_price(sel_stocks):.2f}'
                price_coin1 = rounding_values(df_coin1.lastPrice)

                percent_coin1 = f'{float(df_coin1.priceChangePercent)}%'
        # --- End of Live Price Feature ---

    with live_price_and_overview_col:
        visualisation_list = ["Funds Allocation - Pie Chart", "Asset Type Allocation - Sun Burst", "Networth Over Time - Line Chart"]
        st.markdown("###")
        visualisation_selection =  st.selectbox("Select Visualisation", visualisation_list, key = "7")

        # --- Pie and Sun Burst Charts ---
        if visualisation_selection == "Funds Allocation - Pie Chart":
            # Fetching the list of assets
            sum_with_name_result = sum_valuation_and_name()
            sum_with_name_result_df = pd.DataFrame(sum_with_name_result, columns = ["Asset Name", "Valuation"])
            newlist = sum_with_name_result_df[["Asset Name", "Valuation"]].values.tolist() # List is now in the form of [[x1, y1], [x2, y2], ...]

            # Separating the list into 2
            revenue_wise_name = [item[0] for item in newlist]
            revenue_wise_valuation = [item[1] for item in newlist]

            revenue_wise_chart = go.Figure(data = [go.Pie(labels = revenue_wise_name, values = revenue_wise_valuation)])
            revenue_wise_chart.update_traces(marker=dict(line=dict(color='#000000', width=2)))
            st.plotly_chart(revenue_wise_chart, use_container_width = True)
        elif visualisation_selection == "Asset Type Allocation - Sun Burst":
            # --- Sun Burst Chart ---
            sunburstdata = view_all_asset()
            sunburstdf = pd.DataFrame(sunburstdata, columns = ['asset_name', 'ticker_symbol', 'asset_buy_price', 'no_of_shares', 'valuation', 'asset_type', 'date_of_purchase'])
            sunburstfig = px.sunburst(sunburstdf, path=['asset_type', 'asset_name'], values='valuation')
            st.write(sunburstfig)
            # --- End of Sun Burst Chart ---
        elif visualisation_selection == "Networth Over Time - Line Chart":
            # --- Line Chart for Portfolio Value ---
            not_linechart = dop_list()
            not_linechart_df = pd.DataFrame(not_linechart, columns = ["Valuation", "Date of Purchase"])
            not_linechart_list = not_linechart_df[["Valuation", "Date of Purchase"]].values.tolist()

            # --- Separating the list into 2 ---
            not_value = [item[0] for item in not_linechart_list]
            not_dop = [item[1] for item in not_linechart_list]

            # calculate the cumulative valuation
            cumulative_valuation = [sum(not_value[:i+1]) for i in range(len(not_value))]

            # create the plotly figure
            not_fig = go.Figure()
            not_fig.add_trace(go.Scatter(x=not_dop, y=cumulative_valuation, mode='lines', name='Cumulative Valuation'))

            # set the layout of the plot
            not_fig.update_layout(xaxis_title='Date', yaxis_title='Valuation')

            # show the plot
            st.plotly_chart(not_fig, use_container_width = True)
            # --- End of Line Chart for Portfolio Value ---
        else:
            st.error("Please select a valid visualisation from the list.")
        # --- End of Pie and Sunburst Chart ---

        # --- Dip Finder View ---
        st.markdown("<h5 style = 'text-align: center;'>Dip Finder View</h5>", unsafe_allow_html = True)
        moving_average_list = ["Short-term", "Intermediate-term", "Long-term"]
        select_moving_average = st.selectbox('Investment Period', moving_average_list)
        symbols = get_tickers_and_type()
        interval = "1d" # daily timeframe
        period = "1y" # historical data goes all the way back to 1 year (using 1y cuz we need to use at least 200 days for the MA)
        moving_average_days = 50 # default value is set to 50 (Short-term)

        ticker_symbols = []
        asset_type = []
        ma_values = []

        for i in symbols:
            ticker = i[0]
            type = i[1]
            ticker_symbols.append(ticker)
            asset_type.append(type)

        # obtain 200 day MA list
        for k in range(len(ticker_symbols)):
            tick = ticker_symbols[k]
            type = asset_type[k]
            if type == "Crypto":
                # define the cryptocurrency symbol and the currency
                symbol = "bitcoin"
                currency = "usd"

                # define the API endpoint URL
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency={currency}&days=max"

                # send an HTTP request to the API endpoint and retrieve the data
                response = requests.get(url)
                data = response.json()

                # convert the data to a Pandas DataFrame
                prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
                prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
                prices.set_index("timestamp", inplace=True)

                # calculate the moving average
                if select_moving_average == "Short-term":
                    moving_average_days = 50
                elif select_moving_average == "Intermediate-term":
                    moving_average_days = 100
                elif select_moving_average == "Long-term":
                    moving_average_days = 200

                ma = prices["price"].rolling(window = moving_average_days).mean()

                # get the most recent 200-day moving average value
                ma_value = ma[-1]
                ma_values.append(ma_value)
            elif type == "Stocks":
                data = yf.download(ticker_symbols[k], interval=interval, period=period)
                # calculate the moving average
                if select_moving_average == "Short-term":
                    moving_average_days = 50
                elif select_moving_average == "Intermediate-term":
                    moving_average_days = 100
                elif select_moving_average == "Long-term":
                    moving_average_days = 200

                ma = data["Close"].rolling(window = moving_average_days).mean()
                ma_value = ma[-1]
                ma_values.append(ma_value)

        # obtain the current price list
        current_price = []
        symbols = get_tickers_and_type()
        ticker_symbols = []
        asset_type = []

        for i in symbols:
            ticker = i[0]
            type = i[1]
            ticker_symbols.append(ticker)
            asset_type.append(type)

        for i in range(len(ticker_symbols)):
            tick = ticker_symbols[i]
            type = asset_type[i]

            if type == "Crypto":
                df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')
                df_coin = df[df.symbol == "BTCUSDT"]
                price_coin = df_coin.lastPrice.iloc[0]
                # price_coin = df_coin.lastPrice
                current_price.append(price_coin)
            elif type == "Stocks":
                live_price = si.get_live_price(tick)
                current_price.append(live_price)

        # calculate the percentage difference
        percentage_diff = []
        for i in range(len(ma_values)):
            diff = ((current_price[i] - ma_values[i]) / ma_values[i]) * 100
            percentage_diff.append(diff)

        # plotting the graph
        
        trace = go.Bar(
            x = ticker_symbols,
            y = percentage_diff,
            marker=dict(
                color=['red' if i < 0 else 'green' for i in percentage_diff] # set color based on sign of value
            )
        )

        # create layout
        layout = go.Layout(
            xaxis=dict(title='Ticker Symbol'),
            yaxis=dict(title='Percentage Difference')
        )

        # create figure
        dip_finder_fig = go.Figure(data=[trace], layout=layout)
        st.plotly_chart(dip_finder_fig, use_container_width = True)
        # --- End of Dip Finder View ---
    st.markdown("---")

    selection_histogram_col, volume_col = st.columns([2,3])

    with selection_histogram_col:
        # --- Selection Histogram ---
        st.markdown("<h3 style = 'text-align: center;'>Selection Histogram</h3>", unsafe_allow_html = True)
        # Connect to the database
        conn = sqlite3.connect('portfolio.db')

        # Query the data and load it into a Pandas dataframe
        df = pd.read_sql_query('SELECT * FROM portfolio', conn)

        # Define the chart
        brush = alt.selection_interval()
        chart = alt.Chart(df).mark_point().encode(
            x='no_of_shares:Q',
            y='valuation:Q',
            color=alt.Color('asset_name:N', legend=None),
            tooltip=['asset_name', 'valuation', 'no_of_shares']
        ).add_selection(
            brush
        )

        # Define the histogram
        hist = alt.Chart(df).mark_bar().encode(
            y=alt.Y('asset_name:N', axis=alt.Axis(orient='right')),
            color=alt.Color('asset_name:N', legend=None),
            x=alt.X('count(asset_name):Q', axis=alt.Axis(title='Number of purchases')),
        ).transform_filter(
            brush
        )

        # Combine the chart and the histogram
        st.altair_chart(chart & hist, use_container_width = True)
        # --- End of Selection Histogram ---
    with volume_col:
        # --- Volume Feature ---
        st.markdown("<h3 style = 'text-align: center;'>Volume</h3>", unsafe_allow_html = True)
        # fetch data from yahoo finance using yfinance
        ticker = st.text_input("Enter a Ticker Symbol:", value = "BTC-USD")
        if not ticker:
            st.error("Invalid ticker symbol")
        else:
            df = yf.download(ticker, start="2022-01-01", end="2022-12-31")

            # Filter the data to include only the desired time period
            start_date_str = df.index.min().strftime("%Y-%m-%d")
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date_str = df.index.max().strftime("%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            selected_date_range = st.date_input("Select Date Range", value=(start_date, end_date))
            start_date_ns = pd.to_datetime(selected_date_range[0]).to_pydatetime()
            end_date_ns = pd.to_datetime(selected_date_range[1]).to_pydatetime()
            filtered_df = df[(df.index >= start_date_ns) & (df.index <= end_date_ns)]

            # Plot the data using Plotly
            volume_fig = px.line(filtered_df, x = filtered_df.index.strftime("%Y-%m-%d"), y = 'Volume')
            volume_fig.update_layout(xaxis_title='Date')

            st.plotly_chart(volume_fig, use_container_width = True)
        # --- End of Volume Feature ---

    st.markdown("##")
    st.markdown("##")