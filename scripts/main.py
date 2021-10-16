import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
import pandas as pd

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, redirect_uri=config.REDIRECT_URI, scope='user-read-recently-played'))
    recently_played = sp.current_user_recently_played(limit=50)

    albums_list = []
    for row in recently_played['items']:
        album_id = row['track']['album']['id']
        album_name = row['track']['album']['name']
        album_release_date = row['track']['album']['release_date']
        album_url = row['track']['album']['external_urls']['spotify']
        artist_id = row['track']['artists'][0]['id']
        
        album_elem = {'album_id':album_id, 'name':album_name, 'release_date':album_release_date, 'url':album_url, 'artist_id':artist_id}
        albums_list.append(album_elem)

    artists_arr = []
    for row in recently_played['items']:
        artist_id = row['track']['artists'][0]['id']
        artist_name = row['track']['artists'][0]['name']
        artist_url = row['track']['artists'][0]['external_urls']['spotify']

        artist_elem = {'artist_id':artist_id, 'name':artist_name, 'url':artist_url}
        artists_arr.append(artist_elem)

    tracks_arr = []
    for row in recently_played['items']:
        track_id = row['track']['id']
        track_name = row['track']['name']
        track_duration = row['track']['duration_ms']
        track_url = row['track']['external_urls']['spotify']
        album_id = row['track']['album']['id']
        artist_id = row['track']['album']['artists'][0]['id']
        
        track_elem = {'track_id':track_id, 'name':track_name, 'duration':track_duration, 'url':track_url, 'album_id':album_id, 'artist_id':artist_id}
        tracks_arr.append(track_elem)

    #Convert list objects to pandas DataFrame and drop duplicates
    albums_df = pd.DataFrame.from_dict(albums_list)
    albums_df = albums_df.drop_duplicates(subset=['album_id'])

    artists_df = pd.DataFrame.from_dict(artists_arr)
    artists_df = artists_df.drop_duplicates(subset=['artist_id'])

    tracks_df = pd.DataFrame.from_dict(tracks_arr)
    tracks_df = tracks_df.drop_duplicates(subset=['track_id'])

    #print(albums_df)
    #print(artists_df)
    #print(tracks_df)
