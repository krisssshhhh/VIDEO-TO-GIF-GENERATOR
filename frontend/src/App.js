// src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BASE_URL = "https://video-to-gif-generator.onrender.com";

function App() {
  const [prompt, setPrompt] = useState('');
  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [gifs, setGifs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    /* Google Identity script should be added in index.html */
    if (window.google) {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        scope: 'https://www.googleapis.com/auth/youtube.readonly',
        callback: (res) => setAccessToken(res.access_token),
      });
      window.gsiClient = client;
    }
  }, []);

  const handleAuth = () => {
    window.gsiClient.requestAccessToken();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !youtubeUrl) {
      alert("Upload a video or paste a YouTube link.");
      return;
    }
    if (youtubeUrl && !accessToken) {
      alert("Please authorize YouTube first.");
      return;
    }
    setIsLoading(true);

    const formData = new FormData();
    formData.append("prompt", prompt);
    if (file) formData.append("file", file);
    if (youtubeUrl) {
      formData.append("youtube_url", youtubeUrl);
      formData.append("yt_token", JSON.stringify({ access_token: accessToken }));
    }

    try {
      const res = await axios.post(`${BASE_URL}/generate`, formData);
      setGifs(res.data.gifs);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (gifPath, idx) => {
    // same as your existing download logic...
  };

  return (
    <div className="container">
      <h1>AI Video → GIF Maker</h1>

      <button onClick={handleAuth} disabled={!!accessToken}>
        {accessToken ? 'YouTube Authorized ✓' : 'Authorize YouTube'}
      </button>

      <form onSubmit={handleSubmit}>
        {/* prompt, file and URL inputs as before */}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing…' : 'Create GIFs'}
        </button>
      </form>

      {/* render GIFs and download buttons */}
      <footer>…</footer>
    </div>
  );
}

export default App;
