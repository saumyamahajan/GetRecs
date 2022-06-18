import spotipy as spotipy
import streamlit as st
import streamlit.components.v1 as components
import pickle
import requests
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
from collections import defaultdict


def get_playlist_id_from_url(playlist_url):
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    return playlist_id


def create_necessary_outputs(playlist_id, df, sp):
    # generate playlist dataframe
    playlist = pd.DataFrame()

    for ix, i in enumerate(sp.playlist(playlist_id)['tracks']['items']):
        # print(i['track']['artists'][0]['name'])
        playlist.loc[ix, 'artist'] = i['track']['artists'][0]['name']
        playlist.loc[ix, 'track_name'] = i['track']['name']
        playlist.loc[ix, 'track_id'] = i['track']['id']  # ['uri'].split(':')[2] track-id for spotify_df1 otherwise id
        playlist.loc[ix, 'url'] = i['track']['album']['images'][1]['url']
        playlist.loc[ix, 'date_added'] = i['added_at']

    playlist['date_added'] = pd.to_datetime(playlist['date_added'])
    playlist = playlist[playlist['track_id'].isin(df['track_id'].values)].sort_values('date_added', ascending=False)

    return playlist


# def generate_playlist_feature(complete_feature_set, playlist_df, weight_factor, sp, spotify_df):
def generate_playlist_feature(complete_feature_set, playlist_df, weight_factor):
    complete_feature_set_playlist = complete_feature_set[complete_feature_set['track_id'].isin(playlist_df['track_id'].values)]
    # .drop('id', axis = 1).mean(axis =0)
    complete_feature_set_playlist = complete_feature_set_playlist.merge(playlist_df[['track_id', 'date_added']], on='track_id', how='inner')
    complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['track_id'].isin(playlist_df['track_id'].values)]
    # .drop('id', axis = 1)

    playlist_feature_set = complete_feature_set_playlist.sort_values('date_added', ascending=False)

    most_recent_date = playlist_feature_set.iloc[0, -1]

    for ix, row in playlist_feature_set.iterrows():
        playlist_feature_set.loc[ix, 'months_from_recent'] = int((most_recent_date.to_pydatetime() - row.iloc[-1].to_pydatetime()).days)

    playlist_feature_set['weight'] = playlist_feature_set['months_from_recent'].apply(lambda x: weight_factor ** (-x))

    playlist_feature_set_weighted = playlist_feature_set.copy()
    playlist_feature_set_weighted.update(playlist_feature_set_weighted.iloc[:, :-3].mul(playlist_feature_set_weighted.weight.astype(int), 0))
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-3]

    # generate_playlist_recos(spotify_df, playlist_feature_set_weighted_final.sum(axis=0), complete_feature_set_nonplaylist, sp)
    return playlist_feature_set_weighted_final.sum(axis=0), complete_feature_set_nonplaylist



def generate_playlist_recs(df, features, nonplaylist_features, sp):

    non_playlist_df = df[df['track_id'].isin(nonplaylist_features['track_id'].values)]
    non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop(['track_id'], axis=1).values, features.drop(labels='track_id').values.reshape(1, -1))[:, 0]
    non_playlist_df_top_10 = non_playlist_df.sort_values('sim', ascending=False).head(12)
    non_playlist_df_top_10['url'] = non_playlist_df_top_10['track_id'].apply(lambda x: sp.track(x)['album']['images'][1]['url'])

    # display_recommendations(non_playlist_df_top_10)
    return non_playlist_df_top_10


def display_recommendations(recommendations):
    tracks = []
    for id in recommendations['track_id']:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(id)
        tracks.append(track)

    with st.container():
        col1, col2, col3 = st.columns([2, 2, 2])
        i = 0
        for track, recommendation in zip(tracks, recommendations['track_id']):
            if i % 3 == 0:
                with col1:
                    components.html(track,height=400,)
                i += 1
            elif i==1 or i==4 or i==7 or i==10:
                with col2:
                    components.html(track,height=400,)
                i += 1
            else:
                with col3:
                    components.html(track,height=400,)
                i += 1


def song_page():

    spotify_df1 = pickle.load(open('spotify_df1.pkl', 'rb'))
    dataset = pickle.load(open('SpotifyFeatures.pkl', 'rb'))

    # ohe_cols = 'popularity'
    # client id and secret for my application
    client_id = '31bc4ef11e4348748989a55ef944ed04'
    client_secret = '1d849d0760cc46faab09832c098df97c'
    scope = 'user-library-read'
    # if len(sys.argv) > 1:
    #     username = sys.argv[1]
    # else:
    #     print("Usage: %s username" % (sys.argv[0],))
    #     sys.exit()

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    token = util.prompt_for_user_token(scope, client_id=client_id, client_secret=client_secret, redirect_uri='http://localhost:8881/callback')
    sp = spotipy.Spotify(auth=token)

    if "get_recommendation" not in st.session_state:
        st.session_state.get_recommendation = False

    st.title('Get recommendations for any spotify playlists')
    playlist_url = st.text_input("Enter any playlist Url")
    playlist_id = get_playlist_id_from_url(playlist_url)


    if (st.button("Get Recommendations") or st.session_state.get_recommendation):
        with st.spinner("Fetching Recommendations..."):
            st.session_state.get_recommendation = True

            list1 = create_necessary_outputs(playlist_id, dataset, sp)
            complete_feature_set_playlist_vector_list1, complete_feature_set_nonplaylist_list1 = generate_playlist_feature(spotify_df1, list1, 1.09)
            # generate_playlist_feature(complete_feature_set, list1, 1.5, sp, spotify_df)
            list_recs = generate_playlist_recs(dataset, complete_feature_set_playlist_vector_list1,complete_feature_set_nonplaylist_list1, sp)
            display_recommendations(list_recs)


