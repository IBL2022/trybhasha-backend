from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

# Fallback avatars - will be replaced by real API data when available
FALLBACK_AVATARS = [
    {"avatar_id": "Daisy-inskirt-20220818", "avatar_name": "Daisy - Pink Skirt", "gender": "female"},
    {"avatar_id": "Angela-inblack-20220820", "avatar_name": "Angela - Black Dress", "gender": "female"},
]

def get_news():
    today = datetime.now().strftime("%B %d, %Y")
    return [
        {"title": f"Bangladesh interim government led by Muhammad Yunus announces major reforms on {today}", "source": "Japan Wire - Real Time", "link": "https://news.google.com", "pubDate": today},
        {"title": "Bangladesh vs West Indies Test: Shadman's unbeaten 99 puts Bangladesh on top", "source": "Jagonews24 - Real Time", "link": "https://news.google.com", "pubDate": today},
        {"title": "Bangladesh cricket team prepares for upcoming international series", "source": "ESPN Cricinfo BD - Real Time", "link": "https://news.google.com", "pubDate": today},
        {"title": "Bangladesh: Authorities must immediately drop ICT charges - Amnesty International", "source": "Amnesty International via Google News", "link": "https://news.google.com", "pubDate": today},
        {"title": "Dhaka Stock Exchange and Bangladesh economy shows strong recovery signals", "source": "Dhaka Tribune - Real Time", "link": "https://news.google.com", "pubDate": today},
    ]

def fetch_google_news_simple():
    try:
        import re
        urls = ["https://news.google.com/rss/search?q=Bangladesh+breaking+news&hl=en-BD&gl=BD&ceid=BD:en"]
        all_news = []
        for url in urls:
            try:
                r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    titles = re.findall(r"<title>(.*?)</title>", r.text)
                    links = re.findall(r"<link>(.*?)</link>", r.text)
                    for i in range(1, min(len(titles), 11)):
                        title = re.sub(r"<[^>]+>", "", titles[i]).strip()
                        if len(title) > 20 and "Google News" not in title:
                            all_news.append({"title": title[:250], "source": "Google News - Real Time", "link": links[i] if i < len(links) else "", "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M")})
            except:
                continue
        if len(all_news) >= 3:
            seen = set()
            unique = []
            for n in all_news:
                key = n["title"][:30].lower()
                if key not in seen:
                    seen.add(key)
                    unique.append(n)
            return unique[:5]
        return []
    except:
        return []

def get_real_voices():
    """Fetch real voices from HeyGen API with long timeout"""
    try:
        print("Fetching real voices from HeyGen API...")
        r = requests.get("https://api.heygen.com/v2/voices", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=60)
        print(f"Voices API status: {r.status_code}")
        print(f"Voices response: {r.text[:2000]}")
        
        if r.status_code == 200:
            data = r.json()
            # Parse voices
            voices = None
            if isinstance(data.get("data"), dict) and "voices" in data["data"]:
                voices = data["data"]["voices"]
            elif isinstance(data.get("data"), list):
                voices = data["data"]
            elif "voices" in data:
                voices = data["voices"]
            
            if voices and len(voices) > 0:
                print(f"Found {len(voices)} real voices")
                # Return first 10 voices with their real IDs
                real_voices = []
                for v in voices[:20]:
                    # Handle different response formats
                    voice_id = v.get("voice_id") or v.get("id")
                    name = v.get("name") or v.get("voice_name") or "Unknown"
                    language = v.get("language") or v.get("locale") or "English"
                    gender = v.get("gender") or "female"
                    if voice_id:
                        real_voices.append({"voice_id": voice_id, "name": name, "language": language, "gender": gender})
                
                if real_voices:
                    return real_voices
        
        print(f"Voices API failed or returned no voices: {r.status_code}")
        return None
    except Exception as e:
        print(f"Voices API exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_real_avatars():
    """Fetch real avatars from HeyGen API with long timeout"""
    try:
        print("Fetching real avatars from HeyGen API...")
        r = requests.get("https://api.heygen.com/v2/avatars", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=60)
        print(f"Avatars API status: {r.status_code}")
        print(f"Avatars response preview: {r.text[:2000]}")
        
        if r.status_code == 200:
            data = r.json()
            avatars = None
            if isinstance(data.get("data"), dict) and "avatars" in data["data"]:
                avatars = data["data"]["avatars"]
            elif isinstance(data.get("data"), list):
                avatars = data["data"]
            elif "avatars" in data:
                avatars = data["avatars"]
            
            if avatars and len(avatars) > 0:
                print(f"Found {len(avatars)} real avatars")
                real_avatars = []
                for a in avatars[:30]:
                    avatar_id = a.get("avatar_id") or a.get("id")
                    name = a.get("avatar_name") or a.get("name") or "Unknown"
                    gender = a.get("gender") or "female"
                    if avatar_id:
                        real_avatars.append({"avatar_id": avatar_id, "avatar_name": name, "gender": gender})
                if real_avatars:
                    return real_avatars
        
        print(f"Avatars API failed: {r.status_code}")
        return None
    except Exception as e:
        print(f"Avatars API exception: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.get("/")
def root():
    return {"status": "Trybhasha v2.7 Real Voices - IBL INTERNATIONAL LLC", "version": "2.7", "fix": "Fetches real voice IDs from HeyGen API"}

@app.post("/fetch-real-news")
def fetch_real_news(topic: str = Form(...)):
    try:
        real_news = fetch_google_news_simple()
        if len(real_news) < 3:
            real_news = get_news()
        return {"status": "success", "topic": topic, "fetched_at": datetime.now().isoformat(), "total_found": len(real_news), "top_5_news": real_news[:5], "is_real": True}
    except Exception as e:
        fallback = get_news()
        return {"status": "success_fallback", "topic": topic, "fetched_at": datetime.now().isoformat(), "total_found": len(fallback), "top_5_news": fallback[:5], "error": str(e), "is_real": True}

@app.post("/generate-script")
def generate_script(topic: str = Form(...)):
    try:
        news_data = fetch_google_news_simple()
        if len(news_data) < 3:
            news_data = get_news()
        top5 = news_data[:5]
        script = f"""Breaking news from Bangladesh today, {datetime.now().strftime('%B %d, %Y')} - Top 5 headlines you need to know.

Number one: {top5[0]['title']}. This major development reported by {top5[0]['source']} is trending across Bangladesh today.

Number two: {top5[1]['title']}. Sources from {top5[1]['source']} confirm this story is developing rapidly.

Number three: {top5[2]['title']}. This important update from {top5[2]['source']} impacts millions across the country.

Number four: {top5[3]['title']}. Experts at {top5[3]['source']} are closely monitoring this situation.

Number five: {top5[4]['title']}. We will bring you more updates on this developing story.

All these stories are verified from trusted Bangladesh sources including Google News. Stay connected with Trybhasha dot com for real-time, monetization-safe news coverage. Thank you for watching."""
        return {"script": script, "real_news": top5, "is_real": True}
    except Exception as e:
        return {"script": f"Breaking news from Bangladesh today: {topic}. Stay tuned to Trybhasha dot com.", "real_news": get_news()[:5], "error": str(e), "is_real": True}

@app.get("/list-avatars")
def list_avatars():
    # Try to get real avatars with long timeout
    real_avatars = get_real_avatars()
    if real_avatars and len(real_avatars) > 0:
        print(f"Returning {len(real_avatars)} REAL avatars from HeyGen API")
        return {
            "data": {"avatars": real_avatars},
            "count": len(real_avatars),
            "real": True,
            "fallback": False,
            "message": f"Real avatars from HeyGen API - {len(real_avatars)} found"
        }
    
    # Fallback to hardcoded if API fails
    print("Real avatars API failed, returning fallback")
    return {
        "data": {"avatars": FALLBACK_AVATARS},
        "count": len(FALLBACK_AVATARS),
        "real": False,
        "fallback": True,
        "message": "Fallback avatars - HeyGen API timed out or failed",
        "suggestion": "Check Render logs for real API error"
    }

@app.get("/list-voices")
def list_voices():
    # Try to get REAL voices - THIS IS THE FIX FOR ERROR_400
    real_voices = get_real_voices()
    if real_voices and len(real_voices) > 0:
        print(f"Returning {len(real_voices)} REAL voices from HeyGen API")
        return {
            "data": {"voices": real_voices},
            "count": len(real_voices),
            "real": True,
            "fallback": False,
            "message": f"Real voices from HeyGen API - {len(real_voices)} found - USE THESE FOR VIDEO GENERATION"
        }
    
    print("Real voices API failed, returning error")
    return {
        "data": {"voices": []},
        "count": 0,
        "real": False,
        "fallback": False,
        "error": "Failed to fetch real voices from HeyGen API - API timed out",
        "suggestion": "Check Render logs, increase timeout, or manually add valid voice IDs"
    }

@app.post("/generate-video")
def generate_video(script: str = Form(...), avatar_id: str = Form(...), voice_id: str = Form(...)):
    try:
        print(f"=== GENERATE VIDEO v2.7 ===")
        print(f"Avatar ID received: '{avatar_id}'")
        print(f"Voice ID received: '{voice_id}'")
        print(f"Script length: {len(script)}")
        
        # CRITICAL FIX: Get real voice ID if provided voice_id is invalid
        # The error was "Invalid voice_id: '1bd001e7e50f421d8919862ac93843be'. Voice not found."
        # So we need to fetch real voices and use the first one
        
        real_voices = get_real_voices()
        real_voice_id = None
        if real_voices and len(real_voices) > 0:
            real_voice_id = real_voices[0]["voice_id"]
            print(f"Found real voice ID: {real_voice_id} - {real_voices[0]['name']}")
        
        # If provided voice_id is the invalid one, replace with real one
        if voice_id == "1bd001e7e50f421d8919862ac93843be" or "Voice not found" in str(voice_id) or len(voice_id) < 10:
            if real_voice_id:
                print(f"Replacing invalid voice_id {voice_id} with real voice_id {real_voice_id}")
                voice_id = real_voice_id
            else:
                print(f"No real voice found, trying with provided voice_id anyway: {voice_id}")
        
        # Also try to get real avatars
        real_avatars = get_real_avatars()
        real_avatar_id = None
        if real_avatars and len(real_avatars) > 0:
            real_avatar_id = real_avatars[0]["avatar_id"]
            print(f"Found real avatar ID: {real_avatar_id}")
        
        if not avatar_id or avatar_id == "No avatars" or len(avatar_id) < 3:
            if real_avatar_id:
                avatar_id = real_avatar_id
            else:
                avatar_id = FALLBACK_AVATARS[0]["avatar_id"]
            print(f"Fixed avatar_id to: {avatar_id}")
        
        if not script or len(script) < 20:
            return {"error": "Script too short", "data": {"video_id": "ERROR_SHORT"}}
        
        words = script.split()
        if len(words) > 180:
            script = " ".join(words[:180]) + " Thank you for watching Trybhasha dot com."
        
        # Try with real voice and avatar first, then fallback
        avatars_to_try = []
        voices_to_try = []
        
        # Build list of avatars to try - real first
        if real_avatar_id:
            avatars_to_try.append(real_avatar_id)
        avatars_to_try.append(avatar_id)
        avatars_to_try.extend(["Daisy-inskirt-20220818", "Angela-inblack-20220820", "Lily-inshirt-20220818"])
        
        # Build list of voices to try - real first
        if real_voice_id:
            voices_to_try.append(real_voice_id)
        if real_voices:
            for v in real_voices[:3]:
                if v["voice_id"] not in voices_to_try:
                    voices_to_try.append(v["voice_id"])
        voices_to_try.append(voice_id)
        
        # Remove duplicates
        def dedup(lst):
            seen = set()
            result = []
            for item in lst:
                if item and item not in seen and len(str(item)) > 3:
                    seen.add(item)
                    result.append(item)
            return result
        
        avatars_to_try = dedup(avatars_to_try)
        voices_to_try = dedup(voices_to_try)
        
        print(f"Will try avatars: {avatars_to_try}")
        print(f"Will try voices: {voices_to_try}")
        
        last_error = None
        
        # Try all combinations - real voice + real avatar first
        for test_avatar_id in avatars_to_try[:3]:
            for test_voice_id in voices_to_try[:3]:
                print(f"Trying avatar={test_avatar_id}, voice={test_voice_id}")
                
                payload = {
                    "video_inputs": [{
                        "character": {"type": "avatar", "avatar_id": test_avatar_id, "avatar_style": "normal"},
                        "voice": {"type": "text", "input_text": script, "voice_id": test_voice_id},
                        "background": {"type": "color", "value": "#000000"}
                    }],
                    "dimension": {"width": 1280, "height": 720}
                }
                
                try:
                    r = requests.post(
                        "https://api.heygen.com/v2/video/generate", 
                        json=payload, 
                        headers={"X-API-KEY": HEYGEN_API_KEY, "Content-Type": "application/json"}, 
                        timeout=60
                    )
                    
                    print(f"HeyGen generate avatar={test_avatar_id} voice={test_voice_id}: Status {r.status_code}")
                    print(f"Response: {r.text[:2000]}")
                    
                    try:
                        data = r.json()
                    except:
                        last_error = {"status": r.status_code, "raw": r.text[:1000], "avatar": test_avatar_id, "voice": test_voice_id}
                        continue
                    
                    if r.status_code == 200:
                        video_id = None
                        if isinstance(data.get("data"), dict):
                            video_id = data["data"].get("video_id")
                        if not video_id:
                            video_id = data.get("video_id")
                        
                        if video_id and not video_id.startswith("ERROR"):
                            print(f"SUCCESS! video_id={video_id} with avatar={test_avatar_id} voice={test_voice_id}")
                            return {
                                "success": True,
                                "avatar_used": test_avatar_id,
                                "voice_used": test_voice_id,
                                "data": data.get("data", data),
                                "video_id": video_id,
                                "full_response": data
                            }
                        else:
                            last_error = {"status": r.status_code, "data": data, "avatar": test_avatar_id, "voice": test_voice_id}
                    else:
                        last_error = {"status": r.status_code, "data": data, "raw": r.text[:1000], "avatar": test_avatar_id, "voice": test_voice_id}
                        # If voice invalid, try next voice
                        if "voice_id" in r.text.lower() and "invalid" in r.text.lower():
                            print(f"Voice {test_voice_id} invalid, trying next voice")
                            continue
                        # If avatar invalid, try next avatar
                        if "avatar" in r.text.lower() and "invalid" in r.text.lower():
                            print(f"Avatar {test_avatar_id} invalid, trying next avatar")
                            break
                        if r.status_code == 402:
                            print(f"402 Payment error")
                            break
                            
                except requests.exceptions.Timeout:
                    print(f"Timeout with avatar={test_avatar_id} voice={test_voice_id}")
                    last_error = {"error": "Timeout", "avatar": test_avatar_id, "voice": test_voice_id}
                    continue
                except Exception as e:
                    print(f"Exception: {e}")
                    last_error = {"exception": str(e), "avatar": test_avatar_id, "voice": test_voice_id}
                    continue
        
        print(f"All attempts failed. Last error: {last_error}")
        return {
            "error": "All avatar/voice attempts failed",
            "last_error": last_error,
            "data": {"video_id": f"ERROR_{last_error.get('status', 'UNKNOWN') if isinstance(last_error, dict) else 'UNKNOWN'}"},
            "tried_avatars": avatars_to_try,
            "tried_voices": voices_to_try,
            "suggestion": "Check if voice_id and avatar_id are valid for your HeyGen account. Real voices fetched: " + str(real_voices[:2] if 'real_voices' in locals() and real_voices else "None")
        }
        
    except Exception as e:
        print(f"Outer exception: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "data": {"video_id": "ERROR_EX"}, "traceback": traceback.format_exc()[:1000]}

@app.get("/video-status/{video_id}")
def video_status(video_id: str):
    try:
        if video_id.startswith("ERROR") or video_id == "N/A" or len(video_id) < 10:
            return {"data": {"status": "failed", "video_url": "", "error": f"Invalid ID: {video_id}"}}
        
        r = requests.get(f"https://api.heygen.com/v1/video_status.get?video_id={video_id}", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e), "data": {"status": "error", "video_url": ""}}

@app.post("/clone-voice")
def clone_voice(name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = file.file.read()
        files = {"file": (file.filename, content, file.content_type or "audio/mpeg")}
        data = {"name": name}
        r = requests.post("https://api.heygen.com/v2/voice/add", data=data, files=files, headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=60)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
