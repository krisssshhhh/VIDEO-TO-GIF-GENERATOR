// frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [gifs, setGifs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !youtubeUrl) {
      alert("Upload a video or paste a YouTube link.");
      return;
    }
    setIsLoading(true);

    const formData = new FormData();
    formData.append("prompt", prompt);
    if (file) formData.append("file", file);
    if (youtubeUrl) formData.append("youtube_url", youtubeUrl);

    try {
      const res = await axios.post("http://localhost:8000/generate", formData);
      setGifs(res.data.gifs);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (gifPath, idx) => {
    try {
      const url = `http://localhost:8000/${gifPath}`;
      const response = await axios.get(url, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'image/gif' });
      const localUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = localUrl;
      link.download = `gif_${idx}.gif`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(localUrl);
    } catch (err) {
      console.error("Download failed", err);
      alert("Download failed. Check the console for details.");
    }
  };

  return (
    <div className="container">
      <h1>AI Video → GIF Maker</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="e.g. motivational quote"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          required
          disabled={isLoading}
        />
        <input
          type="file"
          accept="video/mp4"
          onChange={(e) => {
            setFile(e.target.files[0]);
            setYoutubeUrl('');
          }}
          disabled={isLoading}
        />
        <div className="or-divider">— OR —</div>
        <input
          type="text"
          placeholder="Paste a YouTube video link"
          value={youtubeUrl}
          onChange={(e) => {
            setYoutubeUrl(e.target.value);
            setFile(null);
          }}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading} className={isLoading ? 'loading' : ''}>
          {isLoading ? 'Processing…' : 'Create GIFs'}
        </button>
      </form>

      <div className="gifs-container">
        {gifs.map((gifPath, idx) => (
          <div className="gif-card" key={idx}>
            <img src={`http://localhost:8000/${gifPath}`} alt={`gif-${idx}`} />
            <button onClick={() => handleDownload(gifPath, idx)}>Download</button>
          </div>
        ))}
      </div>

      <footer className="footer">
        Created by <strong>Krish Kumar</strong> | 📧 <a href="mailto:krish892002@gmail.com">krish892002@gmail.com</a> | 🔗 <a href="https://github.com/krisssshhhh" target="_blank" rel="noreferrer">GitHub</a>
      </footer>
    </div>
  );
}

export default App;