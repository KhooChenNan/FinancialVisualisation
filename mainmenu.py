import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from multiapp import MultiApp
from apps import Charts_And_Analysis, Portfolio_Management, Machine_Learning_Optimisation
import base64

from PIL import Image

def create_usertable():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        hashed_password = make_hashes(password)
        c.execute('INSERT INTO usertable(username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except Exception as e:
        print(f"Error adding user data: {e}")
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        hashed_password = make_hashes(password)
        c.execute('SELECT * FROM usertable WHERE username = ? AND password = ?', (username, hashed_password))
        data = c.fetchall()
        return data
    except Exception as e:
        print(f"Error during login: {e}")
    finally:
        conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def view_all_users():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute('SELECT * FROM usertable')
        data = c.fetchall()
        return data
    except Exception as e:
        print(f"Error viewing all users: {e}")
    finally:
        c.close()

def is_database_empty():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute('SELECT COUNT(*) FROM usertable')
        count = c.fetchone()[0]
        return count == 0
    except Exception as e:
        print(f"Error checking if the database is empty: {e}")
    finally:
        c.close()

def main():
    app = MultiApp()
    create_usertable()
    st.set_page_config(page_title = "Financial Visualisation", page_icon = '📈', layout = "wide")

    st.markdown("<h1 style = 'text-align: center; font-size: 66px'>Financial Visualisation</h1>", unsafe_allow_html = True)

    menu = ["Home", "SignUp", "Login"]
    st.sidebar.markdown("<h2 style = 'text-align: center; font-weight: bold;'>Welcome!</h2>", unsafe_allow_html = True)
	
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Home":
        st.markdown("---")

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


    elif choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type = 'password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            result = login_user(username, password)

            if result:
                st.sidebar.success("Logged In as {}".format(username))

                # --- Navigation bar ---
                app.add_app("Charts and Analysis", Charts_And_Analysis.app)
                app.add_app("Machine Learning Optimisation", Machine_Learning_Optimisation.app)
                app.add_app("Portfolio Management", Portfolio_Management.app)
                app.run()

                task = st.selectbox("Task", ["Add Post", "Analytics", "Profiles"])
                if task == "Add Post":
                    st.subheader("Add Your Post")
                elif task == "Analytics":
                    st.subheader("Analytics")
                elif task == "Profiles":
                    st.subheader('User Profiles')
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result, columns = ["Username", "Password"])
                    st.dataframe(clean_db)

            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
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
            confirm_new_password = st.sidebar.text_input("Confirm Password", type = 'password')

        if st.sidebar.button("Signup"):
            if not is_database_empty():
                st.sidebar.error("Account exists on this device")
            else:
                if new_password != confirm_new_password:
                    st.sidebar.warning("Password does not match")
                else:
                    add_userdata(new_user, new_password)
                    st.sidebar.success("Account created successfully!")
                    st.sidebar.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()