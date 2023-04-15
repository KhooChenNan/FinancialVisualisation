import streamlit as st

import hashlib
import base64
import sqlite3
from multiapp import MultiApp
from apps import Charts_And_Analysis, Portfolio_Management, Machine_Learning_Optimisation
from PIL import Image

# --- Computer Security ---
#passlib,hashlib,bcrypt,scrypt
def make_hashes(password):
	"""
    Takes a password string as input, converts it to bytes, encodes it and passes it to the sha256 function in the hashlib module. The resulting hash is then returned as a hexadecimal string.

    Args:
        password (str): The password string to be hashed.

    Returns:
        str: A hexadecimal string representing the hashed password.
	"""
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
	"""
	Checks whether a given password matches a given hashed text.

	Args:
		password (str): The password to check.
		hashed_text (str): The hashed text to check against.

	Returns:
		str: The given hashed text if the password matches, otherwise False.
	"""
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

# --- Database Management ---
conn = sqlite3.connect('data.db')
connection = conn.cursor()

# Database Functions
def create_usertable():
	"""
	Creates the userstable table in the database if it does not already exist.
    The table contains two columns: 'username' and 'password'.
	"""
	connection.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username,password):
	"""
	This function adds a new row to the userstable table in the SQLite database data.db. The row contains the provided username and password values.

	Args:

	username: A string representing the username of the new user.
	password: A string representing the password of the new user.
	Returns:

	None. The function only adds the new user information to the database.
	"""
	connection.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username,password))
	conn.commit()

def login_user(username,password):
	"""
	Authenticates a user by checking if the given `username` and `password` match an existing user in the userstable.
    
    Args:
    - username (str): the username to check
    - password (str): the password to check
    
    Returns:
    - list: a list containing the user data (username, password) if the authentication is successful, an empty list otherwise.
	"""
	connection.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username,password))
	data = connection.fetchall()
	return data

def view_all_users():
	"""
    Retrieves all user data from the "userstable" table in the database.

    Returns:
    data (list): A list of tuples containing all rows from the "userstable" table.
    Each tuple contains two elements, the username and hashed password.
	"""
	connection.execute('SELECT * FROM userstable')
	data = connection.fetchall()
	return data

def main():
	"""
	The driver code for the entire Financial Visualisation web application.
	"""
	app = MultiApp()

	st.set_page_config(page_title = "Financial Visualisation", page_icon = '📈', layout = "wide")

	st.markdown("<h1 style = 'text-align: center; font-size: 66px'>Financial Visualisation</h1>", unsafe_allow_html = True)

	menu = ["Home", "Sign Up", "Login"]
	st.sidebar.markdown("<h2 style = 'text-align: center; font-weight: bold;'>Welcome!</h2>", unsafe_allow_html = True)
	
	choice = st.sidebar.selectbox("Navigation", menu)

	# --- Main Menu/Home Page (Selection Box) ---
	if choice == "Home":

		st.markdown("---")
		# st.markdown("<h2 style = 'text-align: center;'>Home</h2>", unsafe_allow_html = True)

		home_title1_para, home_title1_gif = st.columns([5, 4])
		with home_title1_para:
			st.markdown("<h3 style = 'text-decoration: underline;'>Analyse market with live data</h3>", unsafe_allow_html = True)
			st.markdown("<h5 style = 'text-align: justify;'>Tired of using outdated financial tools that don't provide real-time market data?  Look no further!  Financial Visualisation is a dashboard designed to give you a competitive edge by providing live market data.  You may analyze the market trends such as the historical cumulative returns of an asset and make informed investment decisions based on their performance during a specific time, be it the bear or bull market.  Sign up now to experience the power of real-time market analysis!</h5>", unsafe_allow_html = True)
		with home_title1_gif:
			file_ = open("GIF/gif1.gif", "rb")
			contents = file_.read()
			data_url = base64.b64encode(contents).decode("utf-8")
			file_.close()

			st.markdown(
				f'<img src="data:image/gif;base64,{data_url}" alt="gif1">',
				unsafe_allow_html=True,
			)
		
		home_title2_gif, home_title2_para = st.columns([4, 5])
		with home_title2_gif:
			image = Image.open('GIF/funds_allocation.png')
			st.image(image)
		with home_title2_para:
			st.markdown("<h3 style = 'text-decoration: underline;'>Elevate Your Investment Experience</h3>", unsafe_allow_html = True)
			st.markdown("<h5 style = 'text-align: justify'>Managing your portfolio just got easier with our advanced portfolio management system.  The system allows you to manipulate your portfolio holdings such as creating, reading, updating, and deleting data swiftly.  With interactive charts such as pie charts, sunburst charts, and tree maps, you can quickly identify patterns and make data-driven decisions.</h5>", unsafe_allow_html = True)
		
	# Login page selection box (Selection Box) ---
	elif choice == "Login":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password", type = 'password')
		if st.sidebar.checkbox("Login"):
			# Creates a usertable for the database then hashes the password
			create_usertable()
			hashed_password = make_hashes(password)

			result = login_user(username, check_hashes(password, hashed_password)) # Checking the password
			if result:
				st.sidebar.success("Logged In as {}".format(username)) # Gives the green box
				# --- Navigation bar ---
				app.add_app("Charts and Analysis", Charts_And_Analysis.app)
				app.add_app("Machine Learning Optimisation", Machine_Learning_Optimisation.app)
				app.add_app("Portfolio Management", Portfolio_Management.app)
				app.run()
					
			else:
				st.warning("Incorrect Username/Password")

	# --- Sign up selection box (Selection Box) ---
	elif choice == "Sign Up":
		st.markdown("---")

		upper_c1, upper_c2 = st.columns([1, 2])
		lower_c1, lower_c2 = st.columns([1, 2])

		with upper_c1:
			st.sidebar.markdown("---")
			st.sidebar.markdown("<h4 style = 'text-align: center'>Create New Account</h3>", unsafe_allow_html = True)
			st.sidebar.markdown("###")
			new_user = st.sidebar.text_input("Username")
		with lower_c1:
			new_password = st.sidebar.text_input("Password", type = 'password')
			confirm_new_password = st.sidebar.text_input("Confirm assword", type = 'password')

		if st.sidebar.button("Signup"):
			if new_password != confirm_new_password:
				st.sidebar.warning("Password does not match")
			else:
				create_usertable()
				add_userdata(new_user, make_hashes(new_password))
				st.sidebar.success("Account created successfully!")
				st.sidebar.info("Go to Login Menu to login")

		signup_title1_para, signup_title1_gif = st.columns([5, 4])

		with signup_title1_para:
			st.markdown("<h3 style = 'text-decoration: underline;'>Effortless Sign Up Process</h3>", unsafe_allow_html = True)
			st.markdown("<h5 style = 'text-align: justify'>Coming from a trader's point of view, we understand that time is valuable, which is why the system's sign up process is designed in a way to be as effortless as possible.  With juat a few simple steps, you will be on your way to taking control of your investments.  No paperwork, no hassle.  Sign up now and start enjoying the benefits of our service for absolutely free in no time!</h5>", unsafe_allow_html = True)

		with signup_title1_gif:
			file_ = open("GIF/signup_gif.gif", "rb")
			contents = file_.read()
			data_url = base64.b64encode(contents).decode("utf-8")
			file_.close()

			st.markdown(
				f'<img src="data:image/gif;base64,{data_url}" alt="signup_gif">',
				unsafe_allow_html=True,
			)

		signujp_title2_gif, signup_title2_para = st.columns([4, 5])

		with signup_title2_para:
			st.markdown("<h3 style = 'text-decoration: underline;'>Revolutionize Your Investment Strategy with Our AI Technology</h3>", unsafe_allow_html = True)
			st.markdown("<h5 style = 'text-align: justify;'>Many services on our platform are available to assist you in managing your money more successfully. You may visualise your portfolio in an interesting and educational way with the help of our interactive charts, such as sunburst and tree maps. You can simply follow your progress and make wise investment selections thanks to tools like investment lists and purchase histories. Moreover, by analysing market patterns and offering individualised suggestions for portfolio optimization, our AI technology leverages cutting-edge algorithms. Join our platform right away to take control of your assets.</h5>", unsafe_allow_html = True)

	st.markdown("##")
	st.markdown("##")
	st.write("© Copyright 2022 Khoo Chen Nan.  All rights reserved.")
			
# Must not function/be called by other files and can only run within this file
if __name__ == '__main__':
	main()