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

# Collection for storing each user's personal game list
personal_games = user_db["personal_games"]

# Session State to manage login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

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

def login_user_callback(username, password):
    user = users.find_one({"username": username})
    if user and check_password(password, user["password"]):
        st.success("Login successful!")
        st.session_state.logged_in = True  # Update session state
        st.session_state.username = username  # Set the username in session state
    else:
        st.warning("Incorrect username or password")


# Logout function to reset login status
def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = None  # Reset username in session state
    st.sidebar.info("You have been logged out.")


# Function to retrieve and display games with filters, sorting, pagination, and search functionality
def view_games():
    # Initialize session state for page number and search query
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "last_search_query" not in st.session_state:
        st.session_state.last_search_query = ""

    st.subheader("Games List")
    
    # Search bar for game name
    search_query = st.text_input("Search for a game by name")
    
    # Reset to page 1 if the search query changes
    if search_query != st.session_state.last_search_query:
        st.session_state.current_page = 1
        st.session_state.last_search_query = search_query
    
    # Filter Options
    genre_filter = st.selectbox("Filter by Genre", options=["All"] + sorted(games.distinct("Genre")))
    publisher_filter = st.selectbox("Filter by Publisher", options=["All"] + sorted(games.distinct("Publisher")))
    
    # Sort Option
    sort_option = st.radio("Sort by Rank", options=["Ascending", "Descending"])
    sort_order = 1 if sort_option == "Ascending" else -1

    # Pagination: Show 20 games at a time
    page = st.session_state.current_page
    skip = (page - 1) * 20  # Calculate documents to skip

    # Build the query
    query = {}
    if search_query:
        query["Name"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search for the game name
    if genre_filter != "All":
        query["Genre"] = genre_filter
    if publisher_filter != "All":
        query["Publisher"] = publisher_filter

    # Fetch and display games with sorting, pagination, and search
    games_list = list(games.find(query).sort("Rank", sort_order).skip(skip).limit(20))
    for game in games_list:
        st.write(f"Rank: {game['Rank']} - Name: {game['Name']} - Genre: {game['Genre']} - Publisher: {game['Publisher']}")
        
        # "Add" button to add the game to the user's personal list with on_click callback
        st.button("Add", key=f"add_{game['Name']}", on_click=add_game_to_personal_list, args=(game,))

    # Navigation controls with unique keys
    st.write(f"Showing page {page}")
    if len(games_list) == 20:
        if st.button("Next Page", key="next_page"):
            st.session_state.current_page += 1
    if page > 1:
        if st.button("Previous Page", key="previous_page"):
            st.session_state.current_page -= 1




# Function to add game to user's personal list
def add_game_to_personal_list(game):
    user_personal_list = personal_games.find_one({"username": st.session_state.username})
    
    if user_personal_list:
        # Check if game name is already in the user's list
        if game["Name"] not in user_personal_list["games"]:
            personal_games.update_one(
                {"username": st.session_state.username},
                {"$push": {"games": game["Name"]}}
            )
            st.success(f"{game['Name']} added to your personal list!")
        else:
            st.info(f"{game['Name']} is already in your personal list.")
    else:
        # Create a new document for the user with just the game name
        personal_games.insert_one({"username": st.session_state.username, "games": [game["Name"]]})
        st.success(f"{game['Name']} added to your personal list!")


# Function to display the user's personal game list with options to remove or display activity
def view_personal_list():
    st.subheader(f"{st.session_state.username}'s Personal Game List")
    user_personal_list = personal_games.find_one({"username": st.session_state.username})
    
    if user_personal_list and user_personal_list["games"]:
        # Display each game name in the user's personal list
        for game_name in user_personal_list["games"]:
            st.write(game_name)  # Display just the name

            # "Remove" button to remove the game from the user's personal list with on_click callback
            st.button("Remove", key=f"remove_{game_name}", on_click=remove_game_from_personal_list, args=(game_name,))
            st.button("Display Activity", key=f"activity_{game_name}", on_click=display_game_activity, args=(game_name,))
    else:
        st.info("Your personal game list is empty.")


# Function to display activity for a game
def display_game_activity(game_name):
    st.write(f"Displaying activity for: {game_name}")
    # Code here to handle the display activity for the game


# Function to remove a game from the user's personal list
def remove_game_from_personal_list(game_name):
    personal_games.update_one(
        {"username": st.session_state.username},
        {"$pull": {"games": game_name}}
    )
    st.success(f"{game_name} removed from your personal list.")


# Streamlit Interface
st.title("Welcome to the User Portal")

# Sidebar menu options
menu = ["Login", "Register"]
if st.session_state.logged_in:
    menu.append("Browse")  # Show "Browse" only when logged in
    menu.append("Profile")  # Show "Profile" to view personal list
    menu.append("Logout")  # Show "Logout" option

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login" and not st.session_state.logged_in:
    st.subheader("Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", on_click=login_user_callback, args=(username, password)):
        login_user_callback(username, password)

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

elif choice == "Profile" and st.session_state.logged_in:
    view_personal_list()  # Show personal game list
    
elif choice == "Logout" and st.session_state.logged_in:
    logout_user()
    st.success("You have been logged out successfully.")
