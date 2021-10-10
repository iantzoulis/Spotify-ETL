import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config
#import pandas as pd
import json
import sys

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, redirect_uri=config.REDIRECT_URI, scope='user-read-recently-played'))
    recently_played = sp.current_user_recently_played(limit=50)

    print(recently_played)
    