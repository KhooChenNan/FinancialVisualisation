import sqlite3

portfolio_conn = sqlite3.connect('portfolio.db', check_same_thread = False)
c_portfolio_conn = portfolio_conn.cursor()

#1 --- Create table --- E.g. Creates a table for the database
def create_portfolio_table():
	"""
	Creates the 'portfolio' table in the 'c_portfolio' database if it does not already exist.

	The 'portfolio' table stores information about assets such as their names, ticker symbols, buy prices, 
	number of shares held, valuations, types, and dates of purchase.

	Args:
		None

	Returns:
		None

	"""
	c_portfolio_conn.execute('CREATE TABLE IF NOT EXISTS portfolio(asset_name TEXT, ticker_symbol TEXT, asset_buy_price FLOAT, no_of_shares FLOAT, valuation FLOAT, asset_type TEXT, date_of_purchase DATE)')

#2 --- Add data --- E.g. Adds new entries to the database
def add_data(asset_name, ticker_symbol, asset_buy_price, no_of_shares, valuation, asset_type, date_of_purchase):
	"""
    Adds data for a new asset to the 'portfolio' database table.

    Args:
        asset_name (str): The name of the asset.
        ticker_symbol (str): The ticker symbol of the asset.
        asset_buy_price (float): The average buy price of the asset.
        no_of_shares (float): The number of shares held for the asset.
        valuation (float): The current valuation of the asset.
        asset_type (str): The type of asset (e.g. stock, cryptocurrency, etc.).
        date_of_purchase (str): The date the asset was purchased in the format YYYY-MM-DD.

    Returns:
        None
	"""
	c_portfolio_conn.execute('INSERT INTO portfolio(asset_name, ticker_symbol, asset_buy_price, no_of_shares, valuation, asset_type, date_of_purchase) VALUES (?, ?, ?, ?, ?, ?, ?)', (asset_name, ticker_symbol, asset_buy_price, no_of_shares, valuation, asset_type, date_of_purchase))
	portfolio_conn.commit()

#3 --- All assets/purchase history --- E.g. Returns everything from the database
def view_all_asset():
	"""
    Retrieves all data from the 'portfolio' database table.

    Returns:
        list of tuples: A list of tuples where each tuple contains the data of an asset including its name, ticker symbol, 
        average buy price, number of shares held, valuation, asset type, and date of purchase.
	"""
	c_portfolio_conn.execute('SELECT * FROM portfolio')
	data = c_portfolio_conn.fetchall()
	return data

#4 --- All asset name --- E.g. Returns all the asset names without repetition
def view_all_asset_names():
	"""
    Retrieves a list of all unique asset names from the 'portfolio' database table.

    Returns:
        list of tuples: A list of tuples where each tuple contains a unique asset name.
	"""
	c_portfolio_conn.execute('SELECT DISTINCT asset_name FROM portfolio')
	data = c_portfolio_conn.fetchall()
	return data

#5 --- Asset data by name --- E.g. Returns all info from the database for that specific asset (Not distinct or summed)
def get_asset(asset_name):
	"""
    Retrieves all the data associated with a specific asset from the 'portfolio' database table.

    Args:
        asset_name (str): The name of the asset to retrieve data for.

    Returns:
        list of tuples: A list of tuples where each tuple contains the data for a single asset entry in the portfolio table.
	"""
	c_portfolio_conn.execute('SELECT * FROM portfolio WHERE asset_name = "{}"'.format(asset_name))
	data = c_portfolio_conn.fetchall() # Need to fetchall when returning data
	return data

#6 --- Asset data by ticker symbol --- E.g. returns the asset info by ticker symbol (Not distinct or summed)
def get_asset_by_ticker_symbol(ticker_symbol):
	"""
	Retrieves all data from the 'portfolio' database table where the ticker symbol matches the specified parameter.

	Args:
		ticker_symbol (str): The ticker symbol of the asset.

	Returns:
		list of tuples: A list of tuples containing all data from the 'portfolio' database table where the ticker symbol 
		matches the specified parameter.
	"""
	c_portfolio_conn.execute('SELECT * FROM portfolio WHERE ticker_symbol = "{}"'.format(ticker_symbol))
	data = c_portfolio_conn.fetchall()
	return data

#7 --- Edit data --- E.g. Edit the asset info from the database
def edit_asset_data(new_name, new_ticker_symbol, new_buy_price, new_no_of_shares, new_valuation, new_asset_type, new_date_of_purchase, asset_name, ticker_symbol, asset_type, date_of_purchase):
	"""
	Updates data in the 'portfolio' database table for the specified asset.

	Args:
		new_name (str): The new name of the asset.
		new_ticker_symbol (str): The new ticker symbol of the asset.
		new_buy_price (float): The new buy price of the asset.
		new_no_of_shares (float): The new number of shares of the asset.
		new_valuation (float): The new valuation of the asset.
		new_asset_type (str): The new asset type of the asset.
		new_date_of_purchase (str): The new date of purchase of the asset.
		asset_name (str): The current name of the asset.
		ticker_symbol (str): The current ticker symbol of the asset.
		asset_type (str): The current asset type of the asset.
		date_of_purchase (str): The current date of purchase of the asset.

	Returns:
		list of tuples: A list of tuples containing all data from the 'portfolio' database table where the asset name, ticker symbol, asset type, and date of purchase match the specified parameters after updating the data.
	"""
	c_portfolio_conn.execute("UPDATE portfolio SET asset_name = ?,ticker_symbol = ?, asset_buy_price = ?, no_of_shares = ?, valuation = ?, asset_type = ?, date_of_purchase = ? WHERE asset_name = ? and ticker_symbol =? and asset_type = ? and date_of_purchase = ?",(new_name, new_ticker_symbol, new_buy_price, new_no_of_shares, new_valuation, new_asset_type, new_date_of_purchase, asset_name, ticker_symbol, asset_type, date_of_purchase))
	portfolio_conn.commit() # Need to commit when updating
	data = c_portfolio_conn.fetchall()
	return data

#8 --- Delete data --- E.g. Deletes the asset from the database
def delete_asset(asset_name, date_of_purchase):
	"""
	Deletes an asset entry from the 'portfolio' database table based on the asset name and date of purchase.

	Args:
		asset_name (str): The name of the asset to be deleted.
		date_of_purchase (str): The date of purchase of the asset to be deleted.

	Returns:
		None
	"""
	c_portfolio_conn.execute('DELETE FROM portfolio WHERE asset_name = "{}" and date_of_purchase = "{}"'.format(asset_name, date_of_purchase))
	portfolio_conn.commit()

#9 --- No of shares by asset name --- E.g. Returns the ENTIRE sum invested in the specific asset
def get_no_of_shares(asset_name):
	"""
	Retrieves the number of shares of an asset from the 'portfolio' database table where the asset name matches the specified parameter.

	Args:
		asset_name (str): The name of the asset.

	Returns:
		list of tuples: A list of tuples containing the number of shares of the asset from the 'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT no_of_shares FROM portfolio WHERE asset_name = "{}"'.format(asset_name))
	data = c_portfolio_conn.fetchall()
	return data

#10 --- Valuation by asset name --- E.g. Returns the ENTIRE sum invested in the specific asset.  (100k)
def get_valuation(asset_name):
	"""
	Retrieves the total valuation of an asset from the 'portfolio' database table.

	Args:
		asset_name (str): The name of the asset.

	Returns:
		list of tuples: A list of tuples containing the total valuation of the asset.
	"""
	c_portfolio_conn.execute('SELECT SUM(valuation) FROM portfolio WHERE asset_name = "{}"'.format(asset_name))
	data = c_portfolio_conn.fetchall()
	return data

#11 --- Sum of valuation --- E.g. Returns the ENTIRE sum invested (500k)
def sum_valuation():
	"""
	Calculates the sum of all valuations in the 'portfolio' database table.

	Returns:
		float: The sum of all valuations in the 'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT SUM(valuation) FROM portfolio')
	data = c_portfolio_conn.fetchall()
	return data

#12 --- Sum of valuation.  E.g. 20k, 10k, 40k (But won't show asset name)
def sum_distinct_valuation():
	"""
    Retrieves the sum of distinct valuations for each asset name from the 'portfolio' database table.

    Returns:
        list of tuples: A list of tuples containing the sum of distinct valuations for each asset name from the 
        'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT SUM(DISTINCT valuation) FROM portfolio GROUP BY asset_name')
	data = c_portfolio_conn.fetchall()
	return data

#13 --- Sum of valuation with name.  E.g. BTC & 20k; ETH & 10k
def sum_valuation_and_name():
	"""
	Retrieves the sum of valuation for each asset in the portfolio, grouped by the asset name.

	Returns:
		list of tuples: A list of tuples containing the asset name and sum of valuation for each asset in the portfolio.
	"""
	c_portfolio_conn.execute('SELECT asset_name, sum(valuation) FROM portfolio GROUP BY asset_name')
	data = c_portfolio_conn.fetchall()
	return data

#14 --- Sum of valuation with name and asset type.  E.g. BTC, 20k, Crypto; ETH, 10k, Crypto (No repetition)
def sum_valuation_and_name_with_type():
	"""
	Retrieves the sum of the valuations for all assets grouped by name and asset type, sorted by asset type.

	Returns:
		list of tuples: A list of tuples containing the asset name, sum of valuations, and asset type for all assets in the 
		'portfolio' database table, grouped by name and asset type and sorted by asset type.
	"""
	c_portfolio_conn.execute('SELECT asset_name, sum(valuation), asset_type FROM portfolio GROUP BY asset_name ORDER BY asset_type')
	data = c_portfolio_conn.fetchall()
	return data

#15 --- Number of DISTINCT assets --- E.g. Returns how many assets we have (4)
def no_of_distinct_assets():
	"""
	Returns the number of distinct assets in the portfolio.

	Returns:
		list of tuples: A list containing a single tuple, which contains the count of distinct assets in the portfolio.
	"""
	c_portfolio_conn.execute('SELECT COUNT(DISTINCT asset_name) FROM portfolio')
	data = c_portfolio_conn.fetchall()
	return data

#16 --- Asset Type and Sum of valuation by asset type --- E.g. Returns the sum of valuation of all stocks.  E.g. Stocks, 80k;  Crypto, 100k. (No repetition)
def valuation_sum_on_asset_type():
	"""
	Retrieves the sum of valuations for each asset type in the 'portfolio' database table.

	Returns:
		list of tuples: A list of tuples containing the sum of valuations and asset type for each distinct asset type in 
		the 'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT asset_type, sum(valuation) FROM portfolio GROUP BY asset_type')
	data = c_portfolio_conn.fetchall()
	return data

#17 --- Sum of valuation by asset type --- E.g. Returns the ENTIRE sum invested in the specific asset type (200k)
def valuation_by_asset_type(asset_type):
	"""
	Retrieves the total valuation of assets of a specific asset type from the 'portfolio' database table.

	Args:
		asset_type (str): The type of asset for which the valuation is to be retrieved.

	Returns:
		list of tuples: A list of tuples containing the total valuation of assets of the specified type from the 
		'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT SUM(valuation) FROM portfolio WHERE asset_type = "{}"'.format(asset_type))
	data = c_portfolio_conn.fetchall()
	return data

#18 --- Average Asset List (Returns the list of assets invested with the average buy price)
def average_asset_list():
	"""
	Retrieves a list of assets with their average buy price, total number of shares, and total valuation. 

	Returns:
		list of tuples: A list of tuples containing the asset name, ticker symbol, total valuation, average buy price, 
		total number of shares, and asset type for each asset in the 'portfolio' database table.
	"""
	c_portfolio_conn.execute('SELECT asset_name, ticker_symbol, SUM(valuation), SUM(valuation)/SUM(no_of_shares) as avg_buy_price, SUM(no_of_shares), asset_type FROM portfolio GROUP BY asset_name')
	data = c_portfolio_conn.fetchall()
	return data

#19 --- Average Asset List WITHOUT a specific asset (Same as 18 but use for target allocation & returns without that asset)
def specific_average_asset_list(exclude_asset = None):
    """
	Retrieves a list of asset names and their average valuation, calculated as the sum of valuations divided by the number of shares.

	Args:
		exclude_asset (str): Optional parameter to exclude a specific asset name from the result.

	Returns:
		list of tuples: A list of tuples containing asset names and their average valuation, calculated as the sum of valuations 
		divided by the number of shares. If exclude_asset is provided, the function will return the same result but with the specified 
		asset name excluded.
	"""
    if exclude_asset:
        query = f"SELECT asset_name, SUM(valuation) FROM portfolio WHERE asset_name != '{exclude_asset}' GROUP BY asset_name"
    else:
        query = "SELECT asset_name, SUM(valuation) FROM portfolio GROUP BY asset_name"

    c_portfolio_conn.execute(query)
    data = c_portfolio_conn.fetchall()
    return data

#20 --- Return all asset name, valuation, and DOP in the order from oldest to latest---
def dop_list():
	"""
    Retrieves the valuation and date of purchase of all assets in the 'portfolio' database table.

    Returns:
        list of tuples: A list of tuples containing the valuation and date of purchase of all assets in the 'portfolio' 
        database table, sorted by date of purchase in ascending order.
	"""
	c_portfolio_conn.execute('SELECT valuation, date_of_purchase FROM portfolio ORDER BY date_of_purchase')
	data = c_portfolio_conn.fetchall()
	return data

#21 --- Return all ticker symbols:
def get_tickers_and_type():
	"""
	Retrieves a list of all distinct ticker symbols and asset types present in the 'portfolio' database table.

	Returns:
		list of tuples: A list of tuples containing distinct ticker symbols and asset types present in the 'portfolio' 
		database table.
	"""
	c_portfolio_conn.execute('SELECT DISTINCT ticker_symbol, asset_type FROM portfolio')
	data = c_portfolio_conn.fetchall()
	return data

