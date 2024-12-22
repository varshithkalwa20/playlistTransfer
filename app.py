from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace these with your actual credentials
SPOTIFY_CLIENT_ID = "2d4c852b97b747189bd2dd55d1a0e9e1"
SPOTIFY_CLIENT_SECRET = "a96f2b9eca80445cbc7c7281df9dcf78"
SPOTIFY_REDIRECT_URI = "https://varshithkalwa20.github.io/playlistTransfer/callback"

@app.route('/transfer', methods=['POST'])
def transfer_playlist():
    try:
        # Extract tokens from the request
        data = request.json
        youtube_token = data['youtubeToken']
        spotify_token = data['spotifyToken']

        # Authenticate YouTube API
        youtube_credentials = Credentials(token=youtube_token)
        youtube_service = build('youtube', 'v3', credentials=youtube_credentials)

        # Authenticate Spotify API
        sp = spotipy.Spotify(auth=spotify_token)

        # Fetch YouTube playlists
        playlists = youtube_service.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        ).execute()

        if not playlists['items']:
            return jsonify({"error": "No YouTube playlists found!"}), 400

        first_playlist = playlists['items'][0]
        playlist_title = first_playlist['snippet']['title']
        playlist_id = first_playlist['id']

        # Fetch songs from the YouTube playlist
        videos = youtube_service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        ).execute()

        song_titles = [video['snippet']['title'] for video in videos['items']]

        # Create a new Spotify playlist
        user_id = sp.me()['id']
        spotify_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_title,
            public=True,
            description="Transferred from YouTube"
        )

        spotify_playlist_id = spotify_playlist['id']

        # Search for tracks on Spotify and add them to the playlist
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
