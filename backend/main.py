import os, uuid, shutil, subprocess, gc
from fastapi import FastAPI, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import whisper, yt_dlp

os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = None
@app.on_event("startup")
def on_startup():
    global model
    model = whisper.load_model("tiny")

def make_gif(src, dst, start, end):
    pal = dst.replace(".gif", "_pal.png")
    duration = end - start
    subprocess.run([...], check=True)  # ffmpeg palettegen
    subprocess.run([...], check=True)  # ffmpeg paletteuse
    os.remove(pal)

@app.post("/generate")
async def generate(
    prompt: str = Form(...),
    file: UploadFile = None,
    youtube_url: str = Form(None),
    yt_token: dict = Form(None)  # contains oauth tokens
):
    if not file and not youtube_url:
        raise HTTPException(400, "Provide upload or YouTube URL + tokens.")

    tmp_vid = f"videos/{uuid.uuid4()}.mp4"
    os.makedirs("videos", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    if file:
        with open(tmp_vid, "wb") as f:
            shutil.copyfileobj(file.file, f)
    else:
        opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "merge_output_format": "mp4",
            "outtmpl": tmp_vid,
            "youtube_oauth2": {
                "client_id": os.getenv("YT_CLIENT_ID"),
                "client_secret": os.getenv("YT_CLIENT_SECRET"),
                "token": yt_token
            },
        }
        try:
            yt_dlp.YoutubeDL(opts).download([youtube_url])
        except Exception as e:
            raise HTTPException(400, "Download failed: " + str(e))

    try:
        trimmed = tmp_vid.replace(".mp4", "_trim.mp4")
        subprocess.run([...], check=True)  # ffmpeg trim first 15s

        res = model.transcribe(trimmed, fp16=False, language="en")
        segs = res.get("segments", [])[:1]
        if not segs:
            raise HTTPException(400, "No speech detected.")

        gifs = []
        for i, s in enumerate(segs):
            out = f"output/gif_{uuid.uuid4()}.gif"
            make_gif(trimmed, out, s["start"], s["end"])
            gifs.append(out)

        # free memory
        del res, segs
        gc.collect()

        return {"gifs": gifs}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/output/{fname}")
def get_gif(fname: str):
    p = os.path.join("output", fname)
    if not os.path.exists(p):
        raise HTTPException(404, "Not found.")
    return FileResponse(p)
