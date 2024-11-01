import streamlit as st
import pymongo
from pymongo import MongoClient
import bcrypt

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017")

# User database for login and register functionality
user_db = client["user_database"]
users = user_db["users"]

# Games database to view and filter games list
games_db = client["games_database"]
games = games_db["games"]  # Collection name for games data

# Session State to manage login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def register_user(username, password):
    if users.find_one({"username": username}):
        st.warning("Username already exists!")
    else:
        hashed_pw = hash_password(password)
        users.insert_one({"username": username, "password": hashed_pw})
        st.success("You have successfully registered!")

def login_user(username, password):
    user = users.find_one({"username": username})
    if user and check_password(password, user["password"]):
        st.success("Login successful!")
        st.session_state.logged_in = True  # Update session state
    else:
        st.warning("Incorrect username or password")

# Logout function to reset login status
def logout_user():
    st.session_state.logged_in = False
    st.sidebar.info("You have been logged out.")

# Function to retrieve and display games with filters, sorting, and pagination
def view_games():
    st.subheader("Games List")
    
    # Filter Options
    genre_filter = st.selectbox("Filter by Genre", options=["All"] + sorted(games.distinct("Genre")))
    publisher_filter = st.selectbox("Filter by Publisher", options=["All"] + sorted(games.distinct("Publisher")))
    
    # Sort Option
    sort_option = st.radio("Sort by Rank", options=["Ascending", "Descending"])
    sort_order = 1 if sort_option == "Ascending" else -1

    # Pagination: Show 20 games at a time
    page = st.number_input("Page", min_value=1, step=1)
    skip = (page - 1) * 20  # Calculate documents to skip

    # Query with filters
    query = {}
    if genre_filter != "All":
        query["Genre"] = genre_filter
    if publisher_filter != "All":
        query["Publisher"] = publisher_filter
    
    # Fetch and display games with sorting and pagination
    games_list = list(games.find(query).sort("Rank", sort_order).skip(skip).limit(20))
    for game in games_list:
        st.write(f"Rank: {game['Rank']} - Name: {game['Name']} - Genre: {game['Genre']} - Publisher: {game['Publisher']}")
    
    # Navigation controls
    st.write("Showing page", page)
    if len(games_list) == 20:
        st.button("Next Page", on_click=lambda: st.experimental_set_query_params(page=page+1))
    if page > 1:
        st.button("Previous Page", on_click=lambda: st.experimental_set_query_params(page=page-1))

# Streamlit Interface
st.title("Welcome to the User Portal")

# Sidebar menu options
menu = ["Login", "Register"]
if st.session_state.logged_in:
    menu.append("Browse")  # Show "Browse" only when logged in
    menu.append("Logout")  # Show "Logout" option

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login" and not st.session_state.logged_in:
    st.subheader("Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        login_user(username, password)

elif choice == "Register":
    st.subheader("Register Section")
    new_username = st.text_input("Create a Username")
    new_password = st.text_input("Create a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if new_password == confirm_password:
            register_user(new_username, new_password)
        else:
            st.warning("Passwords do not match!")

elif choice == "Browse" and st.session_state.logged_in:
    view_games()  # Show games list with filters, sorting, and pagination

elif choice == "Logout" and st.session_state.logged_in:
    logout_user()
    st.success("You have been logged out successfully.")
