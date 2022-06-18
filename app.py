import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from PIL import Image

from Books import book_page
from Home import home_page
from Movies import movie_page
from Songs import song_page

st.set_page_config(
     page_title="GetRecs",
     # page_icon="🎵",
     layout="wide",
     menu_items={}
    )

with st.sidebar:
    # navigation bar
    curr_page = option_menu(
        menu_title="Recommend for",
        options=["Home", "Movies", "Books","Songs"],
        icons=[ "house", "film", "book-half", "music-note-beamed"],
        default_index=0,
        )

if "curr_page" not in st.session_state: # setting the default page as home page
    st.session_state.curr_page="Home"

if (curr_page == "Home"):
    st.session_state.curr_page = "Home"
    home_page()

if (curr_page == "Movies"):
    st.session_state.curr_page = "Movies"
    movie_page()

if (curr_page == "Books"):
    st.session_state.curr_page = "Books"
    book_page()

if (curr_page == "Songs"):
    st.session_state.curr_page = "Songs"
    song_page()