import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from configparser import ConfigParser
import pandas as pd

def main():
    config = ConfigParser()
    config.read('src/config.ini')

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=config['SPOTIFY']['CLIENT_ID'], 
        client_secret=config['SPOTIFY']['CLIENT_SECRET'], 
        redirect_uri=config['SPOTIFY']['REDIRECT_URI'], 
        scope='user-read-recently-played'))
    recently_played = sp.current_user_recently_played(limit=50)

    print("Extract complete: Finished extracting Spotify listening data. Moving to transform step.")

    # Build a list of dictionaries for each table containing their respective entries
    albums_list = []
    for row in recently_played['items']:
        album_id = row['track']['album']['id']
        album_name = row['track']['album']['name']

        # Provide less-specific date formats a default month/day of the first
        date_precision = row['track']['album']['release_date_precision'].lower()
        if date_precision == 'day':
            album_release_date = row['track']['album']['release_date']
        elif date_precision == 'year':
            album_release_date = row['track']['album']['release_date'] + '-01-01'
        elif date_precision == 'month':
            album_release_date = row['track']['album']['release_date'] + '-01'

        album_url = row['track']['album']['external_urls']['spotify']
        artist_id = row['track']['artists'][0]['id']
        
        album_elem = {'album_id':album_id, 'name':album_name, 'release_date':album_release_date, 'url':album_url, 'artist_id':artist_id}
        albums_list.append(album_elem)

    artists_list = []
    for row in recently_played['items']:
        artist_id = row['track']['artists'][0]['id']
        artist_name = row['track']['artists'][0]['name']
        artist_url = row['track']['artists'][0]['external_urls']['spotify']

        artist_elem = {'artist_id':artist_id, 'name':artist_name, 'url':artist_url}
        artists_list.append(artist_elem)

    tracks_list = []
    for row in recently_played['items']:
        track_id = row['track']['id']
        track_name = row['track']['name']
        track_duration = row['track']['duration_ms']
        track_url = row['track']['external_urls']['spotify']
        album_id = row['track']['album']['id']
        artist_id = row['track']['album']['artists'][0]['id']
        
        track_elem = {'track_id':track_id, 'name':track_name, 'duration':track_duration, 'url':track_url, 'album_id':album_id, 'artist_id':artist_id}
        tracks_list.append(track_elem)

    tracks_played_list = []
    for row in recently_played['items']:
        track_id = row['track']['id']
        track_time_played = row['played_at']
        
        tracks_played_elem = {'track_id':track_id, 'time_played':track_time_played}
        tracks_played_list.append(tracks_played_elem)

    #Convert list objects to pandas DataFrame and drop duplicates
    albums_df = pd.DataFrame.from_dict(albums_list)
    albums_df = albums_df.drop_duplicates(subset=['album_id'])

    artists_df = pd.DataFrame.from_dict(artists_list)
    artists_df = artists_df.drop_duplicates(subset=['artist_id'])

    tracks_df = pd.DataFrame.from_dict(tracks_list)
    tracks_df = tracks_df.drop_duplicates(subset=['track_id'])

    tracks_played_df = pd.DataFrame.from_dict(tracks_played_list)
    
    # Convert column to datetime and desired timezone
    tracks_played_df['time_played'] = pd.to_datetime(tracks_played_df['time_played'])
    tracks_played_df['time_played'] = tracks_played_df['time_played'].dt.tz_convert('US/Eastern')
    
    # Only keep the relevant pieces of timestamp (%Y-%m-%d %H:%M:%S)
    tracks_played_df['time_played'] = pd.to_datetime(tracks_played_df['time_played'].astype(str).str[:-13])

    # Use the track id and timestamp concatenated as a unique identifier for played tracks
    tracks_played_df.insert(loc=0, column='unique_id', value=(tracks_played_df['time_played'].astype('int64') // 10 ** 9))
    tracks_played_df['unique_id'] = tracks_played_df['track_id'] + '|' + tracks_played_df['unique_id'].astype(str)

    print("Transform complete: Finished transforming data. Beginning database load.")

    engine = create_engine(f'mysql+mysqlconnector://{config["DB"]["USER"]}:{config["DB"]["PASSWORD"]}@{config["DB"]["HOST"]}:{config["DB"]["PORT"]}/my_spotify')
    cnxn = engine.raw_connection()
    cursor = cnxn.cursor()

    # Load dataframes into staging tables and insert unique rows into production tables
    albums_df.to_sql('albums_staging', con=engine, if_exists='replace', index=False)
    cursor.execute("""
        INSERT INTO my_spotify.albums
        SELECT tmp.*
        FROM albums_staging tmp
        LEFT JOIN my_spotify.albums prod
            ON tmp.album_id = prod.album_id
        WHERE prod.album_id IS NULL;
    """)
    cnxn.commit()

    artists_df.to_sql('artists_staging', con=engine, if_exists='replace', index=False)
    cursor.execute("""
        INSERT INTO my_spotify.artists
        SELECT tmp.*
        FROM artists_staging tmp
        LEFT JOIN my_spotify.artists prod
            ON tmp.artist_id = prod.artist_id
        WHERE prod.artist_id IS NULL;
    """)
    cnxn.commit()

    tracks_df.to_sql('tracks_staging', con=engine, if_exists='replace', index=False)
    cursor.execute("""
        INSERT INTO my_spotify.tracks
        SELECT tmp.*
        FROM tracks_staging tmp
        LEFT JOIN my_spotify.tracks prod
            ON tmp.track_id = prod.track_id
        WHERE prod.track_id IS NULL;
    """)
    cnxn.commit()

    tracks_played_df.to_sql('tracks_played_staging', con=engine, if_exists='replace', index=False)
    cursor.execute("""
        INSERT INTO my_spotify.tracks_played
        SELECT tmp.*
        FROM tracks_played_staging tmp
        LEFT JOIN my_spotify.tracks_played prod
            ON tmp.unique_id = prod.unique_id
        WHERE prod.unique_id IS NULL;
    """)
    cnxn.commit()

    cursor.close()

    print("Load complete: Finished loading Spotify data to MySQL database.")


if __name__ == '__main__':
    main()
