from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import string
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace these with your actual credentials
SPOTIFY_CLIENT_ID = "2d4c852b97b747189bd2dd55d1a0e9e1"
SPOTIFY_CLIENT_SECRET = "a96f2b9eca80445cbc7c7281df9dcf78"
SPOTIFY_REDIRECT_URI = "https://varshithkalwa20.github.io/playlistTransfer/callback"
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def authenticate_youtube(youtube_token):
    """
    Authenticate and return the YouTube API service.
    """
    youtube_credentials = Credentials(token=youtube_token)
    youtube_service = build('youtube', 'v3', credentials=youtube_credentials)
    return youtube_service

def fetch_youtube_playlists(youtube_service):
    """
    Fetch and return the user's YouTube playlists.
    """
    request = youtube_service.playlists().list(
        part='snippet,contentDetails',
        mine=True,
        maxResults=50  
    )
    response = request.execute()

    playlists = []
    for playlist in response.get('items', []):
        title = playlist['snippet']['title']
        playlist_id = playlist['id']
        playlists.append((title, playlist_id))
    
    return playlists

def fetch_playlist_videos(youtube_service, playlist_id):
    """
    Fetch the videos in a YouTube playlist and return the video titles.
    """
    request = youtube_service.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=playlist_id,
        maxResults=50  
    )
    response = request.execute()

    songs = [video['snippet']['title'] for video in response.get('items', [])]
    return songs

def authenticate_spotify(spotify_token):
    """
    Authenticate and return the Spotify API client.
    """
    sp = spotipy.Spotify(auth=spotify_token)
    return sp

def create_spotify_playlist(sp, user_id, name, description):
    """
    Create a new Spotify playlist for the authenticated user.
    """
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=description)
    return playlist['id']

@app.route('/transfer', methods=['POST'])
def transfer_playlist():
    try:
        # Extract tokens from the request
        data = request.json
        youtube_token = data['youtubeToken']
        spotify_token = data['spotifyToken']

        # Authenticate YouTube API
        youtube_service = authenticate_youtube(youtube_token)

        # Authenticate Spotify API
        sp = authenticate_spotify(spotify_token)

        # Fetch YouTube playlists
        playlists = fetch_youtube_playlists(youtube_service)
        if not playlists:
            return jsonify({"error": "No YouTube playlists found!"}), 400

        first_playlist = playlists[0]
        playlist_title = first_playlist[0]
        playlist_id = first_playlist[1]

        # Fetch songs from the YouTube playlist
        song_titles = fetch_playlist_videos(youtube_service, playlist_id)

        # Create a new Spotify playlist
        user_id = sp.me()['id']
        spotify_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_title,
            public=True,
            description="Transferred from YouTube"
        )

        spotify_playlist_id = spotify_playlist['id']

        # Search and add tracks to Spotify playlist
        track_uris = []
        for song in song_titles:
            search_result = sp.search(q=song, limit=1, type='track')
            if search_result['tracks']['items']:
                track_uris.append(search_result['tracks']['items'][0]['uri'])

        sp.user_playlist_add_tracks(user=user_id, playlist_id=spotify_playlist_id, tracks=track_uris)

        return jsonify({"message": f"Successfully transferred playlist '{playlist_title}' to Spotify!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
