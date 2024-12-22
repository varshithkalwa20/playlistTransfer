from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import string

app = Flask(__name__)

# Replace these with your credentials
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "https://<your-username>.github.io/callback"

@app.route('/transfer', methods=['POST'])
def transfer_playlist():
    data = request.json
    youtube_token = data['youtubeToken']
    spotify_token = data['spotifyToken']

    youtube_service = build('youtube', 'v3', credentials={"token": youtube_token})
    sp = spotipy.Spotify(auth=spotify_token)

    # Fetch playlists
    playlists = youtube_service.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    first_playlist = playlists['items'][0]
    playlist_title = first_playlist['snippet']['title']
    playlist_id = first_playlist['id']

    # Fetch songs from YouTube playlist
    videos = youtube_service.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=50
    ).execute()

    song_titles = [video['snippet']['title'] for video in videos['items']]

    # Create Spotify playlist
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

if __name__ == '__main__':
    app.run(debug=True)
