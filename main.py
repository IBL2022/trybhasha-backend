from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests, os
from openai import OpenAI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.get("/")
def home():
    return {"status": "Trybhasha API Running - IBL International LLC", "version": "1.0"}

@app.post("/generate-script")
def generate_script(data: dict):
    topic = data.get("topic")
    prompt = f"Topic: {topic}. Write 60 sec Bangla news script, 130 words max, hook first 5 sec, monetization safe."
    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    return {"script": res.choices[0].message.content}

@app.post("/clone-voice")
async def clone_voice(file: UploadFile, name: str = Form(...)):
    url = "https://api.heygen.com/v2/voice/add"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    files = {"file": (file.filename, await file.read(), file.content_type)}
    data = {"name": name}
    r = requests.post(url, headers=headers, files=files, data=data)
    return r.json()

@app.post("/generate-video")
def generate_video(data: dict):
    script = data.get("script")
    avatar_id = data.get("avatar_id")
    voice_id = data.get("voice_id")
    url = "https://api.heygen.com/v2/video/generate"
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}
    payload = {
        "video_inputs": [{
            "character": {"type": "avatar", "avatar_id": avatar_id},
            "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
        }],
        "dimension": {"width": 1080, "height": 1920},
        "caption": True
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.json()

@app.get("/list-avatars")
def list_avatars():
    url = "https://api.heygen.com/v2/avatars"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    r = requests.get(url, headers=headers)
    return r.json()

@app.get("/list-voices")
def list_voices():
    url = "https://api.heygen.com/v2/voices"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    r = requests.get(url, headers=headers)
    return r.json()

@app.get("/video-status/{video_id}")
def video_status(video_id: str):
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    r = requests.get(url, headers=headers)
    return r.json()
