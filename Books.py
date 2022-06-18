import streamlit as st
import pickle
import numpy as np


def recommend(book_name, books, similarity_scores, pt):
    # index fetch
    index = np.where(pt.index == book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        # print(pt.index[i[0]])
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))

        data.append(item)

    return data

def book_page():

    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

    list = []
    for i in range(706):
        list.append(pt.index[i])

    st.title('Get recommendations for your favourite books')
    # books['Book-Title'].values
    selected_book_name = st.selectbox('Type or select a book from the dropdown', list)

    if st.button('Recommend'):
        data = recommend(selected_book_name, books, similarity_scores, pt)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(data[0][0])
            st.image(data[0][2].replace("http", "https"))
            st.text(data[0][1])
        with col2:
            st.text(data[1][0])
            st.image(data[1][2].replace("http", "https"))
            st.text(data[1][1])
        with col3:
            st.text(data[2][0])
            st.image(data[2][2].replace("http", "https"))
            st.text(data[2][1])
        with col4:
            st.text(data[3][0])
            st.image(data[3][2].replace("http", "https"))
            st.text(data[3][1])
        with col5:
            st.text(data[4][0])
            st.image(data[4][2].replace("http", "https"))
            st.text(data[4][1])
