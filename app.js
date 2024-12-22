const YOUTUBE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";
const SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize";

const YOUTUBE_CLIENT_ID = "142927213626-u15lulmiu22o5ho7dqoti7tolh98002q.apps.googleusercontent.com";
const SPOTIFY_CLIENT_ID = "2d4c852b97b747189bd2dd55d1a0e9e1";
const REDIRECT_URI = "https://varshithkalwa20.github.io/playlistTransfer/callback"; // Replace with your GitHub Pages URL

// YouTube Login
document.getElementById("login-youtube").onclick = function () {
    const youtubeAuthUrl = `${YOUTUBE_AUTH_URL}?client_id=${YOUTUBE_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=token&scope=https://www.googleapis.com/auth/youtube.readonly`;
    window.location.href = youtubeAuthUrl;
};

// Spotify Login
document.getElementById("login-spotify").onclick = function () {
    const spotifyAuthUrl = `${SPOTIFY_AUTH_URL}?client_id=${SPOTIFY_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=token&scope=playlist-modify-public playlist-modify-private`;
    window.location.href = spotifyAuthUrl;
};

// Save tokens after redirect
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.hash.substr(1));
    const youtubeToken = urlParams.get("access_token");
    const spotifyToken = urlParams.get("access_token");

    if (youtubeToken) {
        localStorage.setItem("youtube_token", youtubeToken);
    }
    if (spotifyToken) {
        localStorage.setItem("spotify_token", spotifyToken);
    }
};

// Transfer Playlist
document.getElementById("transfer-playlist").onclick = async function () {
    const youtubeToken = localStorage.getItem("youtube_token");
    const spotifyToken = localStorage.getItem("spotify_token");

    if (!youtubeToken || !spotifyToken) {
        alert("Please log in to both YouTube and Spotify!");
        return;
    }

    const response = await fetch("https://https://playlisttransfer.onrender.com//transfer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ youtubeToken, spotifyToken }),
    });

    const result = await response.json();
    document.getElementById("output").innerText = `Playlist Transfer: ${result.message}`;
};
