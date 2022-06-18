import streamlit as st
import streamlit.components.v1 as components
from PIL.Image import Image
from streamlit_option_menu import option_menu
from PIL import Image

# home page
def home_page():

        st.title("Welcome to GetRecs :)")
        st.text("Love watching movies, reading novels and listening to songs?")
        st.text("You have come to the right place.")
        st.text("Get recommendations for your favourite movies, books and songs all in one place!")

        col1, col2, col3 = st.columns(3)
        with col1:
            image1 = Image.open('images/movie2.jpg')
            st.image(image1, width=150 , use_column_width=True)

        with col2:
            image2 = Image.open('images/book2.jpg')
            st.image(image2, width=150 , use_column_width=True)

        with col3:
            image3 = Image.open('images/music2.jpg')
            st.image(image3, width=150 , use_column_width=True)
