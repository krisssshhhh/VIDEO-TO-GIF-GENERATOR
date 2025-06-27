import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uuid, shutil, subprocess
import whisper, yt_dlp

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ✅ Health check route for Render
@app.get("/")
def health():
    return {"status": "Backend is live"}

# ✅ Load the whisper model lazily and keep it tiny
model = None

@app.on_event("startup")
def load_model():
    global model
    model = whisper.load_model("tiny")  # Render free = 512MB max

def make_gif_ffmpeg(src: str, dst: str, start: float, end: float):
    palette = dst.replace(".gif", "_palette.png")
    duration = end - start
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
        "-i", src, "-vf", "fps=5,scale=320:-1:flags=lanczos,palettegen", palette
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
        "-i", src, "-i", palette,
        "-lavfi", "fps=5,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse",
        dst
    ], check=True)
    os.remove(palette)

@app.post("/generate")
async def generate(prompt: str = Form(...), file: UploadFile = None, youtube_url: str = Form(None)):
    if not file and not youtube_url:
        raise HTTPException(400, "Upload an MP4 or provide a YouTube URL.")

    os.makedirs("videos", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    video_path = os.path.join("videos", f"{uuid.uuid4()}.mp4")
    if file:
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    else:
        try:
            opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "merge_output_format": "mp4",
                "outtmpl": video_path,
            }
            yt_dlp.YoutubeDL(opts).download([youtube_url])
        except Exception as e:
            print(f"[yt-dlp ERROR] {e}")
            raise HTTPException(400, "YouTube video could not be downloaded. It may require sign-in.")

    try:
        # ✅ Only transcribe the first 15 seconds to save memory
        res = model.transcribe(video_path, fp16=False, language='en', duration=15)
        segs = res.get("segments", [])[:1]  # ✅ Limit to only 1 GIF (less memory)
        if not segs:
            raise HTTPException(400, "No speech detected.")

        gifs = []
        for i, s in enumerate(segs):
            dst = os.path.join("output", f"gif_{i}.gif")
            try:
                make_gif_ffmpeg(video_path, dst, s["start"], s["end"])
                gifs.append(dst)
            except subprocess.CalledProcessError as e:
                print(f"[ffmpeg ERROR] {e}")
                raise HTTPException(500, f"GIF conversion error: {e}")

        return {"gifs": gifs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Unhandled ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/output/{fname}")
def get_gif(fname: str):
    p = os.path.join("output", fname)
    if not os.path.exists(p):
        raise HTTPException(404, "GIF not found.")
    return FileResponse(p)
