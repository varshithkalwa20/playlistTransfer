const YOUTUBE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";
const SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize";

const YOUTUBE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID";
const SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID";

const REDIRECT_URI = "https://<your-username>.github.io/callback"; // Replace with your GitHub Pages URL

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

// Transfer Playlist
document.getElementById("transfer-playlist").onclick = async function () {
    const youtubeToken = localStorage.getItem("youtube_token");
    const spotifyToken = localStorage.getItem("spotify_token");

    if (!youtubeToken || !spotifyToken) {
        alert("Please log in to both YouTube and Spotify!");
        return;
    }

    const response = await fetch("https://your-backend-server.com/transfer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ youtubeToken, spotifyToken }),
    });

    const result = await response.json();
    document.getElementById("output").innerText = `Playlist Transfer: ${result.message}`;
};
