# ⚡ AI-Powered Video to GIF Generator

A prototype that generates **captioned GIFs** from user-uploaded MP4 videos using **OpenAI Whisper** and **MoviePy**.

## 🎯 Features

- Upload an MP4 video
- Enter a theme prompt (e.g., "funny quotes")
- Get 2–3 GIFs generated from the video, each with captions
- Download and preview GIFs directly

---

## 🛠️ Tech Stack

- **Frontend**: React.js
- **Backend**: FastAPI
- **Transcription**: OpenAI Whisper
- **Video Processing**: MoviePy, FFmpeg

---

## 🚀 How to Run Locally

### 1. Clone or Download the Project
```
git clone <repo>  # OR download the zip
cd ai-video-to-gif-generator
```

---

### 2. Run Backend

#### ✅ Prerequisites
- Python 3.8+
- FFmpeg installed (`brew install ffmpeg` on Mac)

#### ▶️ Setup
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### 3. Run Frontend

#### ▶️ Setup
```
cd frontend
npm install
npm start
```

---

### 📦 Output
Visit `http://localhost:3000`, upload a video, and generate GIFs.
GIFs will appear below the form with download links.

---

## 📝 Notes

- Only MP4 upload is supported (no YouTube yet).
- Whisper runs locally using the base model.
- Improve logic in backend to pick better lines using GPT or NLP.

---

## 📄 License

MIT — Free to use and extend!