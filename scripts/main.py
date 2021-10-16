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

    #Convert albums data to pandas DataFrame and drop duplicates
    albums_df = pd.DataFrame.from_dict(albums_list)
    albums_df = albums_df.drop_duplicates(subset=['album_id'])

    print(albums_df)
