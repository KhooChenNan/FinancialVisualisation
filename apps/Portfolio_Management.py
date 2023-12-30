
import pandas as pd
from dbfx import *

import streamlit as st
from plotly import graph_objs as go
import plotly.express as px
import altair as alt
from vega_datasets import data
import numpy as np
import yahoo_fin.stock_info as si

def treemap_visualisation():
	"""Generate a tree map chart visualizing the total valuation of all assets grouped by asset type and name.

    Retrieves data from the 'portfolio' table and creates a pandas DataFrame 'treemapdf' using the columns 'asset_name',
    'ticker_symbol', 'asset_buy_price', 'no_of_shares', 'valuation', 'asset_type', and 'date_of_purchase'. The data is then
    grouped by 'asset_type' and 'asset_name', and the sum of 'valuation' is calculated using the pandas `groupby()` method.

    The resulting DataFrame is used to create a Plotly treemap chart 'treemapfig', with 'asset_type' and 'asset_name' as the
    chart's path, and 'valuation' as the chart's values.

    Finally, the chart is displayed using Streamlit's `st.plotly_chart()` function, with the 'use_container_width' and
    'width' parameters set to 'True' and '100%' respectively.

    Returns:
        None
    """
	# --- Tree Map ---
	treemapdata = view_all_asset()
	treemapdf = pd.DataFrame(treemapdata, columns = ['asset_name', 'ticker_symbol', 'asset_buy_price', 'no_of_shares', 'valuation', 'asset_type', 'date_of_purchase'])
	treemapdf = treemapdf.groupby(['asset_type', 'asset_name']).sum()['valuation'].reset_index()
	treemapfig = px.treemap(treemapdf, path = ['asset_type','asset_name'], values = 'valuation', labels = 'asset_name')
	st.plotly_chart(treemapfig, use_container_width = True, width = "100%")
	# --- End of Tree Map ---

def line_chart_portfolio_value():
	"""
    Displays a line chart for the cumulative valuation of a portfolio over time.

    Returns:
        None
    """
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

# Driver code
def app():
	"""
	The main driver code of the "Portfolio Management" web page.

    Functionalities include:
        1. Create, Read, Update, and Delete (CRUD) function for a management system.
		2. Interactive Data Visualisations such as linked Scatter plots and etc.
		3. Tracks the user's investments.
	"""
	st.markdown("<h2 style = 'text-align: center; font-weight: bold;'>Portfolio Management System</h2>", unsafe_allow_html = True)
	create_tab, update_tab, delete_tab = st.tabs(["Add New Asset", "Edit Asset Data", "Delete Asset"])
	df = pd.read_json('https://api.binance.com/api/v3/ticker/24hr')

	# --- Function 1: Creating/Adding new asset ---
	with create_tab:

		# --- Brushing Scatter Plot ---
		# Connect to the database
		conn = sqlite3.connect('portfolio.db')

		# Query the data and load it into a Pandas dataframe
		testing_df = pd.read_sql_query('SELECT asset_name, ticker_symbol, asset_buy_price, no_of_shares, valuation, asset_type, date_of_purchase FROM portfolio', conn)

		# Brush for selection
		brush = alt.selection_interval()

		# Scatter Plot
		points = alt.Chart(testing_df).mark_point().encode(
			x='no_of_shares:Q',
			y='asset_buy_price:Q',
			color=alt.condition(brush, 'asset_type:O', alt.value('grey'))
		).add_selection(brush)

		# Base chart for data tables
		ranked_text = alt.Chart(testing_df).mark_text().encode(
			y=alt.Y('row_number:O',axis=None)
		).transform_window(
			row_number='row_number()'
		).transform_filter(
			brush
		).transform_window(
			rank='rank(row_number)'
		).transform_filter(
			alt.datum.rank<20
		)

		# Data Tables
		asset_name = ranked_text.encode(text='asset_name:N').properties(title='Name')
		ticker_symbol = ranked_text.encode(text='ticker_symbol:N').properties(title='Ticker')
		asset_buy_price = ranked_text.encode(text='asset_buy_price:N').properties(title='Buy Price')
		no_of_shares = ranked_text.encode(text='no_of_shares:N').properties(title='No. of Shares')
		valuation = ranked_text.encode(text='valuation:N').properties(title='Valuation')
		asset_type = ranked_text.encode(text='asset_type:N').properties(title='Asset Type')
		date_of_purchase = ranked_text.encode(text='date_of_purchase:N').properties(title='Date of Purchase')
		text = alt.hconcat(asset_name, ticker_symbol, asset_buy_price, no_of_shares, valuation, asset_type, date_of_purchase) # Combine data tables

		# Build chart
		purchase_history_chart = alt.hconcat(
			points,
			text
		).resolve_legend(
			color="independent"
		)

		# Show in Streamlit
		st.altair_chart(purchase_history_chart, use_container_width = True)
		# --- End of Brushing Scatter Plot ---
	
		select_export_col, output_filename_col, blank_col = st.columns([4, 4, 7])

		with select_export_col:
			# --- Export to Excel Feature ---
			export_database_list = ["Purchase History", "Investment List"]
			select_export_database = st.selectbox("Data To Be Exported", export_database_list, key = 60)
		with output_filename_col:
			# Get user input for file name
			filename = st.text_input("Enter output file name:", "Enter File Name Here")
		# Connect to the database
		export_conn = sqlite3.connect('portfolio.db')

		# Define a function to export data to Excel
		def export_purchase_history_to_excel():
			# Read data from the database
			df = pd.read_sql_query("SELECT asset_name as Name, ticker_symbol as Symbol, asset_buy_price as Price, no_of_shares as Shares, valuation as Valuation, asset_type as Type, date_of_purchase as Date from portfolio", export_conn)
			# Export data to Excel file
			df.to_excel(f'{filename}.xlsx', index = True)

		def export_investment_list_to_excel():
			# Read data from the database
			df = pd.read_sql_query("SELECT asset_name as Name, ticker_symbol as Symbol, SUM(valuation) as Valuation, SUM(valuation)/SUM(no_of_shares) as Price, SUM(no_of_shares) as Shares, asset_type Type FROM portfolio GROUP BY asset_name", export_conn)
			# Export data to Excel file
			df.to_excel(f'{filename}.xlsx', index = True)

		# Create a Streamlit button to trigger data export
		if st.button("Export"):
			if select_export_database == "Purchase History":
				export_purchase_history_to_excel()
				st.success("Successfully Exported")
			elif select_export_database == "Investment List":
				export_investment_list_to_excel()
				st.success("Successfully Exported")
		# --- End of export to excel feature ---

		user_input_col, visualisation_col = st.columns([2, 3])

		# --- User Input Function ---
		with user_input_col:
			st.markdown("---")
			st.markdown("<h3 style = 'text-align: center;'>Data Input</h3>", unsafe_allow_html = True)
			left_user_input_col, right_user_input_col = st.columns(2)
			with left_user_input_col:
				new_asset_name = st.text_input("Name")
				new_no_of_shares = st.text_input("Number of Shares")
				new_asset_type = st.selectbox("Asset Type", ["Stocks", "Crypto"], key = 1)
			with right_user_input_col:
				new_ticker_symbol = st.text_input("Ticker Symbol")
				new_asset_buy_price = st.text_input("Buy price")
				new_date_of_purchase = st.date_input("Date of Purchase", key = 2)
		with visualisation_col:
			visualisation_list = ["Asset Distribution - Tree Map", "Profit and Loss - Bar Chart with Heat Map"]
			select_visualisation = st.selectbox("Account Overview", visualisation_list)

			if select_visualisation == "Asset Distribution - Tree Map":
				treemap_visualisation()
			elif select_visualisation == "Profit and Loss - Bar Chart with Heat Map":
				# --- Bar Chart with Heat Map ---
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

				df = pd.DataFrame({'Asset': asset_names_list, 'P&L': pnl_list})
				
				# create a horizontal bar chart using Plotly Express
				bar_chart_w_heatmap_fig = px.bar(df, x='P&L', y='Asset', color='P&L', orientation='h', color_continuous_scale=px.colors.diverging.RdYlBu_r)

				# set the chart layout
				st.markdown("<h3 style = 'text-align: center;'>Bar Chart with Heat Map</h3>", unsafe_allow_html = True)
				bar_chart_w_heatmap_fig.update_layout(xaxis_title='P&L', yaxis_title='Asset')

				# display the chart in Streamlit
				st.plotly_chart(bar_chart_w_heatmap_fig, use_container_width=True)
				# --- End of Bar Chart with Heat Map ---

	# add button
		if st.button("Add new Asset"):
			if(new_asset_type == 'Crypto' and new_ticker_symbol == 'BTC'):
				add_data(new_asset_name, new_ticker_symbol, new_asset_buy_price, new_no_of_shares, float(new_asset_buy_price) * float(new_no_of_shares), new_asset_type, new_date_of_purchase)
					
				st.success("Added ::{} ::To Portfolio".format(new_asset_name))
			elif(new_asset_type == 'Stocks'):
				add_data(new_asset_name, new_ticker_symbol, new_asset_buy_price, new_no_of_shares, float(new_asset_buy_price) * float(new_no_of_shares), new_asset_type, new_date_of_purchase)
					
				st.success("Added {} To Portfolio".format(new_asset_name))
			elif (new_asset_type == 'Crypto' and new_ticker_symbol != 'BTC'):
				st.error("Invalid Input.  Portfolio Management System only accepts Bitcoin.")
		# --- End of User Input Function ---

	# --- Function 2: Updating the assets ---
	with update_tab:
		with st.expander("", expanded = True):
			purchase_history_col, investment_list_col = st.columns([6, 5])

			with purchase_history_col:
				st.markdown("<h3 style = 'text-align: center;'>Purchase History</h3>", unsafe_allow_html = True)
				result = view_all_asset()
				clean_df = pd.DataFrame(result, columns = ["Asset Name", "Ticker Symbol", "Buying Price", "Number of Shares", "Valuation", "Asset Type", "Date of Purchase"])
				st.dataframe(clean_df)
			with investment_list_col:
				st.markdown("<h3 style = 'text-align: center;'>Investment List</h3>", unsafe_allow_html = True)
				average_asset = average_asset_list()
				investment_list_df = pd.DataFrame(average_asset, columns = ["Asset Name", "Ticker Symbol", "Valuation", "Average Buy Price", "Total Amount", "Asset Type"])
				st.dataframe(investment_list_df)

		list_of_assets = [i[0] for i in view_all_asset_names()]

		asset_col, date_of_purchase_col = st.columns(2)
		with asset_col:
			selected_asset = st.selectbox("Asset", list_of_assets, key = 3)
		with date_of_purchase_col:
			old_date_of_purchase = st.date_input("Date of Purchase", key = 4)

		asset_result = get_asset(selected_asset)

		if asset_result:
			asset_name = asset_result[0][0]
			ticker_symbol = asset_result[0][1]
			asset_type = asset_result[0][5]

			# --- Upper column ---
		edit_upper_c1, edit_upper_c2, edit_upper_c3, edit_upper_c4 = st.columns(4)
		
		with edit_upper_c1:
			updated_name = st.text_input("Updated Asset Name")

		with edit_upper_c2:
			updated_ticker_symbol = st.text_input("Updated Ticker Symbol")

		with edit_upper_c3:
			updated_buy_price = st.text_input("Updated Buy price")

		with edit_upper_c4:
			updated_no_of_shares = st.text_input("Updated Number of Shares")

		# --- Lower column ---
		edit_lower_c1, edit_lower_c2 = st.columns(2)

		with edit_lower_c1:
			updated_asset_type = st.selectbox("Asset Type", ["Stocks", "Crypto"], key = 5)

		with edit_lower_c2:
			updated_date_of_purchase = st.date_input("Updated Date of Purchase", key = 6)

		if st.button("Update Asset"):
			edit_asset_data(updated_name, updated_ticker_symbol, updated_buy_price, updated_no_of_shares, float(updated_buy_price) * float(updated_no_of_shares), updated_asset_type, updated_date_of_purchase, asset_name, ticker_symbol, asset_type, old_date_of_purchase)
			st.success("Updated {} To {}".format(asset_name, updated_name))

		with st.expander("View Updated Asset", expanded = False):
			result = view_all_asset()
			clean_df = pd.DataFrame(result, columns = ["Asset Name", "Ticker Symbol", "Buying Price", "Number of Shares", "Valuation", "Asset Type", "Date of Purchase"])
			st.dataframe(clean_df)

	# --- Function 3: Deleting the asset ---
	with delete_tab:
		with st.expander("Current Purchase History", expanded = True):
			result = view_all_asset()
			clean_df = pd.DataFrame(result, columns = ["Asset Name", "Ticker Symbol", "Buying Price", "Number of Shares", "Valuation", "Asset Type", "Date of Purchase"])
			st.dataframe(clean_df)

		unique_list = [i[0] for i in view_all_asset_names()]
		delete_by_asset_name =  st.selectbox("Select Asset", unique_list, key = 7)
		date_of_purchase = st.date_input("Date of Purchase", key = 8)
		if st.button("Delete"):
			delete_asset(delete_by_asset_name, date_of_purchase)
			st.warning("Deleted: '{}' purchased at '{}'".format(delete_by_asset_name, date_of_purchase))

		with st.expander("Updated Purchase History", expanded = False):
			result = view_all_asset()
			clean_df = pd.DataFrame(result, columns = ["Asset Name", "Ticker Symbol", "Buying Price", "Number of Shares", "Valuation", "Asset Type", "Date of Purchase"])
			st.dataframe(clean_df)