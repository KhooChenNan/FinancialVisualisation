import datetime

import pandas as pd
import numpy as np
from dbfx import *
import yahoo_fin.stock_info as si

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import requests
import plotly.graph_objs as go
import plotly.express as px

import streamlit as st

def get_portfolio():
    """
    Retrieves a list of asset names, their average buy price, and the number of shares held for each asset 
    from the 'portfolio' database table.

    Returns:
        list of tuples: A list of tuples where each tuple contains the name of an asset, its average buy price, 
        and the number of shares held for that asset.
    """
    # Connect to the database and retrieve the data
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT asset_name, SUM(valuation)/SUM(no_of_shares) as avg_buy_price, SUM(no_of_shares) FROM portfolio GROUP BY asset_name")
    rows = c.fetchall()
    return rows

def rebalance(asset_name_list, pnl_list, predictions_list):
    """
    Rebalances the portfolio by adjusting the value of each asset based on its performance and predicted market trend.
    
    Args:
        asset_name_list (list): A list of strings representing the name of each asset in the portfolio.
        pnl_list (list): A list of floats representing the profit/loss for each asset in the portfolio.
        predictions_list (list): A list of floats representing the predicted market trend for each asset in the portfolio.
        
    Returns:
        tuple: A tuple containing three lists. The first list contains the rebalanced asset names, the second list 
        contains the rebalanced asset values, and the third list contains the asset types.
        
    Note:
        - This function requires the 'get_valuation' function to retrieve the current valuation of each asset.
        - The portfolio is rebalanced based on the following rules:
            - If an asset has both positive profit and a predicted market trend of 'pump', the function will buy 5% more of 
              that asset with cash.
            - If an asset has positive profit but a predicted market trend of 'dump', the function will sell all of the 
              profit for that asset and keep it in cash if the predicted dump is greater than the profit.
            - If an asset has both negative profit and a predicted market trend of 'dump', the function will sell off 15% 
              of the initial holdings for that asset and keep it in cash.
            - If an asset has negative profit but a predicted market trend of 'pump', the function will sell off 10% of 
              the initial holdings for that asset if the predicted pump is greater than the loss.
    """
    rebalanced_name_list = []
    rebalanced_value_list = []
    rebalanced_asset_type_list = []

    for name, pnl, pred in zip(asset_name_list, pnl_list, predictions_list):
        rebalanced_name_list.append(name)

        # Initial we assume loss and predict dump
        value_by_name = get_valuation(name)
        value_by_name = value_by_name[0]
        value_by_name = float('.'.join(str(ele) for ele in value_by_name))
        rebalanced_value = value_by_name * 0.85

        if pnl > 0 and pred > 0: # profit and predict pump
            # Buy 5% more with cash
            value_by_name = get_valuation(name)
            value_by_name = value_by_name[0]
            value_by_name = float('.'.join(str(ele) for ele in value_by_name)) # This line converts from tuple to float
            rebalanced_value = value_by_name + (pnl * 0.1)
        elif pnl > 0 and pred < 0: # profit but predict dump
            # Sell all profit to cash if predicted dump > profit
            value_by_name = get_valuation(name)
            value_by_name = value_by_name[0]
            value_by_name = float('.'.join(str(ele) for ele in value_by_name))
            current_value = pnl + value_by_name
            if abs(pred - current_value) > pnl:
                rebalanced_value = get_valuation(name)
        elif pnl < 0 and pred < 0: # loss and predict dump
            # Sell off 15% of initial holdings to cash
            value_by_name = get_valuation(name)
            value_by_name = value_by_name[0]
            value_by_name = float('.'.join(str(ele) for ele in value_by_name))
            rebalanced_value = value_by_name * 0.85
        elif pnl < 0 and pred > 0: # loss but predict pump
            # Sell off 10% only if predicted pump > loss
            value_by_name = get_valuation(name)
            value_by_name = value_by_name[0]
            value_by_name = float('.'.join(str(ele) for ele in value_by_name))
            current_value = pnl + value_by_name
            if (pred - current_value) > abs(pnl):
                rebalanced_value *= 0.90
        rebalanced_value_list.append(rebalanced_value)
    
    return rebalanced_name_list, rebalanced_value_list

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

def linear_regression_model(x, y):
    """
    Performs linear regression on the input data points.

    Args:
    x (list): A list of floats representing the x-coordinates of the input data points.
    y (list): A list of floats representing the y-coordinates of the input data points.

    Returns:
        tuple: A tuple containing the calculated intercept (alpha) and slope (beta) of the regression line.
    """
    n = len(x)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    xy_cov = sum([xi * yi for xi, yi in zip(x, y)]) / n - x_mean * y_mean
    x_var = sum([xi ** 2 for xi in x]) / n - x_mean ** 2
    beta = xy_cov / x_var
    alpha = y_mean - beta * x_mean
    return alpha, beta

def predict_stock_price(ticker):
    """
    Retrieves historical closing prices of a given stock over the past 30 days and predicts its price for the next day
    using a linear regression model.

    Args:
        ticker (str): The stock symbol of the stock to be predicted.

    Returns:
        float: The predicted price of the stock for the next day.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?symbol={}&interval=1h&period1={}&period2={}".format(ticker, ticker, int(start_date.timestamp()), int(end_date.timestamp()))
    data = urllib.request.urlopen(url).read().decode()
    data = json.loads(data)

    closing_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
    timestamps = data['chart']['result'][0]['timestamp']
    date_str = [datetime.fromtimestamp(x).strftime('%Y-%m-%d') for x in timestamps]

    X = list(range(len(date_str)))
    Y = closing_prices

    alpha, beta = linear_regression_model(X, Y)

    next_day = len(date_str)
    predicted_price = alpha + beta * next_day

    return predicted_price

def get_historical_price_data(crypto_id):
    """
    Retrieves historical price data for a cryptocurrency from the Coingecko API.

    Args:
        crypto_id (str): The ID of the cryptocurrency to retrieve price data for.

    Returns:
        list of tuples: A list of tuples where each tuple contains a timestamp and the corresponding price of the 
        cryptocurrency in USD. The timestamps are represented as Unix timestamps.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API request.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=30&interval=hourly"
    response = requests.get(url)
    data = response.json()
    prices = data["prices"]
    return prices

# function to perform linear regression and predict future prices
def predict_crypto_price(prices):
    """
    Predicts the next value in a linear regression model fitted to historical price data for a cryptocurrency.

    Args:
        prices (list): A list of tuples containing the timestamp and price data for a cryptocurrency.

    Returns:
        float: The predicted value for the next timestamp based on the linear regression model fitted to the input data.
    """
    x = [i for i in range(len(prices))]
    y = [p[1] for p in prices]
    n = len(prices)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    numer = sum([xi*yi for xi, yi in zip(x, y)]) - n * x_mean * y_mean
    denom = sum([xi**2 for xi in x]) - n * x_mean**2
    b = numer / denom
    a = y_mean - b * x_mean
    next_x = len(prices)
    next_y = a + b * next_x
    return next_y

def get_pnl_list():
    """
    Retrieves a list of profit and loss for the assets.

    Returns:
        list of tuples: A list of tuples where each tuple contains the net gains of an asset.
    """
    # ai rebalance
    df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')
    portfolio_assets = average_asset_list()
    asset_names_list = []
    asset_valuations_list = []
    asset_types_list = []
    pnl_list = []
    predictions_list = []
    
    for assets in portfolio_assets: # for each assets, iterate through the loop
        asset_name = assets[0]
        ticker_symbol = assets[1]
        valuation = assets[2]
        avg_buy_price = assets[3]
        no_of_shares = assets[4]
        asset_type = assets[5]
        asset_names_list.append(asset_name)
        asset_valuations_list.append(valuation)
        asset_types_list.append(asset_type)

        # defining pnl list
        if asset_type == 'Stocks':
            live_price = si.get_live_price(ticker_symbol)
            current_valuation = live_price * no_of_shares
            gains = current_valuation - assets[2]
            gains = gains
            pnl_list.append(gains)
        elif asset_type == 'Crypto':
            df_coin_name = ticker_symbol + "USDT"
            df_coin = df[df.symbol == df_coin_name]
            price_coin = df_coin.lastPrice
            current_valuation = price_coin * no_of_shares
            gains = current_valuation - valuation
            pnl_list.append(gains.iloc[0])
        elif asset_type == 'Cash':
            pnl_list.append("0")
    return pnl_list

def app():
    """
    The main driver code of the "Machine Learning Optimisation" web page.

    Functionalities include:
        1. Providing the basic statistical overview of the user's portfolio such as the networth, unrealized profit and loss, percentage gain, and etc.
        2. An Artificial Intelligence Rebalancing Bot that optimizes the user's portfolio by utilizing machine learning techniques.
        3. Specific Target Allocation feature which rebalances the portfolio given a specific percentage of the entire portfolio's funds to be allocated to the targetted asset.
    """
    st.markdown("<h1 style='text-align: center;'>Machine Learning Optimisation</h1>", unsafe_allow_html = True)
    st.markdown("---")
    df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')

    chart_col, networth_col = st.columns([2, 1])

    with chart_col:
        stock_predict_col, crypto_predict_col = st.columns(2)

        with stock_predict_col:
            st.markdown("<h3 style = 'text-align: center;'>Stock Price Predictor</h3>", unsafe_allow_html = True)
            stock_ticker = st.text_input("Enter stock/crypto ticker symbol (e.g. AAPL, MSFT, TSLA):", key = 11)

            if st.button("Predict Next Day Price", key = 12):
                if not stock_ticker:
                    st.error("Invalid ticker symbol")
                else:
                    predicted_price = predict_stock_price(stock_ticker)
                    st.write(f"Predicted {stock_ticker} price in usd for next day: ", round(predicted_price, 2))
        with crypto_predict_col:
            st.markdown("<h3 style = 'text-align: center;'>Crypto Price Predictor</h3>", unsafe_allow_html = True)
            crypto_name = st.text_input("Enter crypto name (e.g. bitcoin, ripple, ethereum)", key = 13)
            crypto_name = crypto_name.lower()

            if st.button("Predict Next Day Price", key = 14):
                if not crypto_name:
                    st.error("Invalid Crypto Name.")
                else:
                    prices = get_historical_price_data(crypto_name)
                    next_price = predict_crypto_price(prices)
                    st.write(f"Predicted {crypto_name} price in usd for next day: {next_price:.2f}")
    try:                
        with networth_col:
            # Current Networth
            total_valuation = 0

            portfolio_assets = average_asset_list()

            for asset in portfolio_assets:
                asset_name = asset[0]
                asset_ticker_symbol = asset[1]
                asset_total_valuation = asset[2]
                asset_avg_buy_price = asset[3]
                asset_total_share = asset[4]
                asset_type = asset[5]

                if asset_type == "Stocks":
                    live_price = si.get_live_price(asset_ticker_symbol)
                    current_valuation = live_price * asset_total_share
                    total_valuation += current_valuation
                elif asset_type == "Crypto":
                    df_coin = df[df.symbol == "BTCUSDT"]
                    price_coin = df_coin.lastPrice
                    current_valuation = price_coin * asset_total_share
                    total_valuation += current_valuation
                elif asset_type == "Cash":
                    current_valuation = asset_total_valuation
                    total_valuation += current_valuation

            st.metric(label = "Networth", value = rounding_values(total_valuation))

            portfolio_assets = average_asset_list()
            pnl_list = get_pnl_list()
            pnl_sum = sum(pnl_list)
            pnl_sum = float(pnl_sum)
            st.metric(label = "Profit and Loss", value = round(pnl_sum, 3))

            # Percentage Gains
            investment_sum = sum_valuation()
            investment_sum = investment_sum[0]
            investment_sum = float(investment_sum[0])

            percentage_change = (pnl_sum/investment_sum)*100
            percentage_change = float(percentage_change)
            st.metric(label="Percentage Gains", value = round(percentage_change, 3))
    except AttributeError:
        st.error("Portfolio is empty")

    st.markdown("---")
    st.markdown("<h3 style = 'text-align: center;'>AI Rebalancing Bot</h3>", unsafe_allow_html = True)
    
    input_col, ai_rebalanced_col = st.columns(2)
    
    with input_col:

        # To be added
        # strategy_col, warning_col = st.columns(2)
        # with strategy_col:
        unique_list = ["Defensive"]
        strategy_select =  st.selectbox("Select Strategy", unique_list, key = 15)
        with st.expander(label = "Please Read", expanded = True):
            st.warning("IMPORTANT: Please be advised that the results generated by the AI Rebalancing bot are intended for informational purposes only and should not be construed as financial advice. The bot is not intended for commercial use, and users should exercise caution and their own discretion when making investment decisions based on its recommendations. We do not assume any liability for any financial losses or other damages resulting from the use of the bot or its recommendations.")
        st.markdown("###")
        enter_button = st.button("Enter", key = 16)
    try:
        with ai_rebalanced_col:
            # Start of AI Rebalance feature
            if enter_button == True and strategy_select != "":
                # Start of AI Rebalance feature
                # --- Fetching the list of assets ---
                sum_with_name_result = sum_valuation_and_name()
                sum_with_name_result_df = pd.DataFrame(sum_with_name_result, columns = ["Asset Name", "Valuation"])
                newlist = sum_with_name_result_df[["Asset Name", "Valuation"]].values.tolist() # List is now in the form of [[x1, y1], [x2, y2], ...]

                # --- Separating the list into 2 ---
                revenue_wise_name = [item[0] for item in newlist]
                revenue_wise_valuation = [item[1] for item in newlist]

                portfolio_assets = average_asset_list()
                asset_names_list = []
                asset_valuations_list = []
                asset_types_list = []
                pnl_list = []
                predictions_list = []
                
                for assets in portfolio_assets: # Define the 2 lists
                    asset_name = assets[0]
                    ticker_symbol = assets[1]
                    valuation = assets[2]
                    avg_buy_price = assets[3]
                    no_of_shares = assets[4]
                    asset_type = assets[5]
                    asset_names_list.append(asset_name)
                    asset_valuations_list.append(valuation)
                    asset_types_list.append(asset_type)

                    # defining pnl list
                    if asset_type == 'Stocks':
                        live_price = si.get_live_price(ticker_symbol)
                        current_valuation = live_price * no_of_shares
                        gains = current_valuation - assets[2]
                        gains = gains
                        pnl_list.append(gains)
                    elif asset_type == 'Crypto':
                        df_coin_name = ticker_symbol + "USDT"
                        df_coin = df[df.symbol == df_coin_name]
                        price_coin = df_coin.lastPrice
                        current_valuation = price_coin * no_of_shares
                        gains = current_valuation - valuation
                        pnl_list.append(gains.iloc[0])
                    elif asset_type == 'Cash':
                        pnl_list.append("0")

                    # defining predictions list
                    if asset_type == 'Stocks':
                        future_price = predict_stock_price(ticker_symbol)
                        predictions_list.append(future_price)
                    elif asset_type == 'Crypto':
                        asset_name = asset_name.lower()
                        prices = get_historical_price_data(asset_name)
                        future_price = predict_crypto_price(prices)
                        predictions_list.append(future_price)
                    elif asset_type == 'Cash':
                        predictions_list.append("0")

                rebalanced_names, rebalanced_values = rebalance(asset_names_list, pnl_list, predictions_list)

                labels = rebalanced_names
                values = rebalanced_values
                labels.append("Cash")
                total_valuation = 0

                portfolio_assets = average_asset_list()

                for asset in portfolio_assets:
                    asset_name = asset[0]
                    asset_ticker_symbol = asset[1]
                    asset_total_valuation = asset[2]
                    asset_avg_buy_price = asset[3]
                    asset_total_share = asset[4]
                    asset_type = asset[5]

                    if asset_type == "Stocks":
                        live_price = si.get_live_price(asset_ticker_symbol)
                        current_valuation = live_price * asset_total_share
                        total_valuation += current_valuation
                    elif asset_type == "Crypto":
                        df_coin = df[df.symbol == "BTCUSDT"]
                        price_coin = df_coin.lastPrice
                        current_valuation = price_coin * asset_total_share
                        total_valuation += current_valuation
                    elif asset_type == "Cash":
                        current_valuation = asset_total_valuation
                        total_valuation += current_valuation
                values.append(total_valuation.iloc[0] - sum(rebalanced_values))

                ai_rebalanced_figure = go.Figure(data = [go.Pie(labels = labels, values = values)])
                ai_rebalanced_figure.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                ai_rebalanced_figure.update_layout(title = "AI Optimised Allocation")
                # create traces for the pie charts
                initial_trace = go.Pie(labels=revenue_wise_name, values=revenue_wise_valuation, name='Initial Allocation')
                rebalanced_trace = go.Pie(labels=labels, values=values, name='Rebalanced Allocation')

                # define the color scale to be used
                color_scale = px.colors.sequential.Plasma

                # set the color sequence for the traces using the color scale
                initial_trace['marker']['colors'] = color_scale[:len(revenue_wise_name)]
                rebalanced_trace['marker']['colors'] = color_scale[:len(values)]

                # create the figure and add the traces
                ai_rebalanced_figure = go.Figure(data=[initial_trace, rebalanced_trace])
                ai_rebalanced_figure.update_layout(
                        title='AI Allocation Rebalanced',
                        coloraxis=dict(
                            colorbar=dict(title='Assets')
                        ),
                        updatemenus=[dict(
                            type='buttons',
                            showactive=False,
                            buttons=[dict(
                                label='Compare Before and After',
                                method='animate',
                                args=[None, dict(frame=dict(duration=500), fromcurrent=True)]
                            )]
                        )],
                        sliders=[dict(
                            active=0,
                            steps=[dict(label='Initial Allocation',
                                        method='update',
                                        args=[{'visible': [True, False]},
                                            {'title': 'Initial Allocation'}]),
                                dict(label='Rebalanced Allocation',
                                        method='update',
                                        args=[{'visible': [False, True]},
                                            {'title': 'Rebalanced Allocation'}])]
                        )]
                    )
                ai_rebalanced_figure.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                st.plotly_chart(ai_rebalanced_figure, use_container_width = True)
            else:
                st.error("Please select a valid strategy from the list.")
            portfolio_assets = average_asset_list()
            asset_names_list = []
            asset_valuations_list = []
            asset_types_list = []
            pnl_list = []
            predictions_list = []
            
            for assets in portfolio_assets: # Define the 2 lists
                asset_name = assets[0]
                ticker_symbol = assets[1]
                valuation = assets[2]
                avg_buy_price = assets[3]
                no_of_shares = assets[4]
                asset_type = assets[5]
                asset_names_list.append(asset_name)
                asset_valuations_list.append(valuation)
                asset_types_list.append(asset_type)

                # defining pnl list
                if asset_type == 'Stocks':
                    live_price = si.get_live_price(ticker_symbol)
                    current_valuation = live_price * no_of_shares
                    gains = current_valuation - assets[2]
                    gains = gains
                    pnl_list.append(gains)
                elif asset_type == 'Crypto':
                    df_coin_name = ticker_symbol + "USDT"
                    df_coin = df[df.symbol == df_coin_name]
                    price_coin = df_coin.lastPrice
                    current_valuation = price_coin * no_of_shares
                    gains = current_valuation - valuation
                    pnl_list.append(gains.iloc[0])
                elif asset_type == 'Cash':
                    pnl_list.append("0")

                # defining predictions list
                if asset_type == 'Stocks':
                    future_price = predict_stock_price(ticker_symbol)
                    predictions_list.append(future_price)
                elif asset_type == 'Crypto':
                    asset_name = asset_name.lower()
                    prices = get_historical_price_data(asset_name)
                    future_price = predict_crypto_price(prices)
                    predictions_list.append(future_price)
                elif asset_type == 'Cash':
                    predictions_list.append("0")

            rebalanced_names, rebalanced_values = rebalance(asset_names_list, pnl_list, predictions_list)

            labels = rebalanced_names
            values = rebalanced_values
            labels.append("Cash")
            total_valuation = 0

            portfolio_assets = average_asset_list()

            for asset in portfolio_assets:
                asset_name = asset[0]
                asset_ticker_symbol = asset[1]
                asset_total_valuation = asset[2]
                asset_avg_buy_price = asset[3]
                asset_total_share = asset[4]
                asset_type = asset[5]

                if asset_type == "Stocks":
                    live_price = si.get_live_price(asset_ticker_symbol)
                    current_valuation = live_price * asset_total_share
                    total_valuation += current_valuation
                elif asset_type == "Crypto":
                    df_coin = df[df.symbol == "BTCUSDT"]
                    price_coin = df_coin.lastPrice
                    current_valuation = price_coin * asset_total_share
                    total_valuation += current_valuation
                elif asset_type == "Cash":
                    current_valuation = asset_total_valuation
                    total_valuation += current_valuation
            values.append(total_valuation.iloc[0] - sum(rebalanced_values))
    except AttributeError:
        st.error("Portfolio is empty")
    # --- Target Allocation feature ---
    st.markdown("---")
    st.markdown("<h3 style = 'text-align: center;'>Specific Target Allocation</h3>", unsafe_allow_html = True)

    user_input_col, result_col = st.columns(2)
    
    try:
        with user_input_col:
            select_assets_col, target_allocation_input_col = st.columns(2)
            with select_assets_col:
                unique_list = [i[0] for i in view_all_asset_names()]
                target_allocation_asset_name =  st.selectbox("Select Asset", unique_list, key = 17)
                enter_button = st.button("Enter", key = 18)
            with target_allocation_input_col:
                target_allocation = st.text_input("Percentage of Target Allocation")

            # create a DataFrame from the lists
            data = {'Asset Name': asset_names_list, 'P&L': pnl_list, 'Asset Type': asset_types_list}
            top_gainers_df = pd.DataFrame(data)

            # sort the DataFrame by P&L in descending order
            top_gainers_df = top_gainers_df.sort_values(by='P&L', ascending=False)

            # add a column containing the row number starting from 1
            top_gainers_df.insert(0, 'Rank', range(1, 1+len(top_gainers_df)))

            # set the index to the 'Rank' column
            top_gainers_df.set_index('Rank', inplace=True)

            # display the table with a title
            st.markdown("---")
            st.markdown("<h6 style = 'text-align: center;'>Top Gainers</h6>", unsafe_allow_html = True)
            st.table(top_gainers_df)

        with result_col:
            # --- Target Allocation Feature ---
            if enter_button == True and target_allocation != "":
                entire_sum = sum_valuation()
                entire_sum = entire_sum[0]
                entire_sum = float('.'.join(str(ele) for ele in entire_sum))

                # Calculates the target value
                target_value = entire_sum * (float(target_allocation)/100)
                target_label_list = []
                target_value_list = []
                target_label_list.append(target_allocation_asset_name)
                target_value_list.append(target_value)

                # To be used for calculation
                original_value = get_valuation(target_allocation_asset_name)
                original_value = original_value[0]
                original_value = float('.'.join(str(ele) for ele in original_value))

                specific_average_asset = specific_average_asset_list(target_allocation_asset_name)
                test_df = pd.DataFrame(specific_average_asset, columns = ["Asset Name", "Valuation"])
                testlist = test_df[["Asset Name", "Valuation"]].values.tolist()

                test_label = [item[0] for item in testlist]
                test_value = [item[1] for item in testlist]

                for item in test_label:
                    target_label_list.append(item)
                for item2 in test_value:
                    ratio = item2/(entire_sum - original_value)
                    final_value = ratio * (entire_sum - float(target_value))
                    target_value_list.append(final_value)

                # --- Fetching the list of assets for Initial Pie ---
                sum_with_name_result = sum_valuation_and_name()
                sum_with_name_result_df = pd.DataFrame(sum_with_name_result, columns = ["Asset Name", "Valuation"])
                newlist = sum_with_name_result_df[["Asset Name", "Valuation"]].values.tolist() # List is now in the form of [[x1, y1], [x2, y2], ...]

                # --- Separating the list into 2 ---
                revenue_wise_name = [item[0] for item in newlist]
                revenue_wise_valuation = [item[1] for item in newlist]
                
                target_rebalanced_figure = go.Figure(data = [go.Pie(labels = target_label_list, values = target_value_list, name = 'Initial Allocation')])
                target_rebalanced_figure = go.Figure(data=[go.Pie(labels=revenue_wise_name, values=revenue_wise_valuation, name='Initial Allocation'),
                            go.Pie(labels=target_label_list, values=target_value_list, name='Rebalanced Allocation')])

                # Restore original order
                original_index = revenue_wise_name.index(target_allocation_asset_name) # obtain index
                valuation_storage = float(target_value_list[0]) # stores the number
                target_value_list.pop(0) # removes the element after stored
                target_value_list.insert(original_index, valuation_storage)
                # --- End of Target Allocation Feature ---

                with st.expander(label = 'Expand/Collapse', expanded = True):
                    # --- Start of Stacked Bar Chart ---
                    result = [x - y for x, y in zip(target_value_list, revenue_wise_valuation)]

                    # create the plotly trace for value_before
                    trace_before = go.Bar(
                        x=revenue_wise_name,
                        y=revenue_wise_valuation,
                        name='Before Target Allocation',
                        marker=dict(color='lightblue'),
                    )

                    # create the plotly trace for value_after
                    trace_after = go.Bar(
                        x=revenue_wise_name,
                        y=result,
                        name='After Target Allocation',
                        marker=dict(color='orange'),
                        hovertemplate='%{y}',
                        text=revenue_wise_valuation,
                    )

                    # create the stacked bar chart
                    stacked_bar_chart = go.Figure(data=[trace_before, trace_after])
                    stacked_bar_chart.update_layout(
                        title='Stacked Bar Chart',
                        xaxis_title='Name',
                        yaxis_title='Value',
                        barmode='stack',
                    )

                    # display the chart in streamlit
                    st.plotly_chart(stacked_bar_chart, use_container_width=True)
                    # --- End of Stacked Bar Chart ---
                    
                    # --- Grouped Bar Chart ---
                    grouped_bar_chart = go.Figure(data=[
                        go.Bar(name='Before Target Allocation', x = revenue_wise_name, y = revenue_wise_valuation),
                        go.Bar(name='After Target Allocation', x = target_label_list, y = target_value_list)
                    ])
                    # Change Bar Mode
                    grouped_bar_chart.update_layout(title = 'Grouped Bar Chart', barmode='group')

                    st.plotly_chart(grouped_bar_chart, use_container_width = True)
                    # --- End of Grouped Bar Chart ---
            else:
                st.error("Please Enter a valid target allocation in percent")
    except AttributeError:
        st.error("Portfolio is empty")

    st.markdown("---")    