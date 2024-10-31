import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def spot(uri):
    # artist_uri = f'spotify:artist:{uri}'
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    results = spotify.artist(uri)
    name = results['name']
    followers = results['followers']['total']
    data = {"name": name, "followers": followers}    
    return data