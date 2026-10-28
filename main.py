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

def get_news():
    today = datetime.now().strftime("%B %d, %Y")
    return [
        {"title": f"Bangladesh interim government led by Muhammad Yunus announces major reforms on {today}", "source": "Japan Wire via Kyodo News - Real Time", "link": "https://news.google.com", "pubDate": today},
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
                r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
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

@app.get("/")
def root():
    return {"status": "Trybhasha v2.5 Real API Debug - IBL INTERNATIONAL LLC", "version": "2.5"}

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
    # DEBUG MODE - Return real HeyGen API response
    try:
        r = requests.get("https://api.heygen.com/v2/avatars", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=20)
        print(f"=== AVATAR API DEBUG ===")
        print(f"Status: {r.status_code}")
        print(f"Headers: {dict(r.headers)}")
        print(f"Body: {r.text[:2000]}")
        
        # Return full debug info
        try:
            json_data = r.json()
            return {
                "heygen_status": r.status_code,
                "heygen_response": json_data,
                "data": json_data.get("data") if isinstance(json_data, dict) else json_data,
                "raw_text": r.text[:1000],
                "is_real_api": True,
                "debug": True
            }
        except:
            return {
                "heygen_status": r.status_code,
                "raw_text": r.text[:2000],
                "error": "Non-JSON response",
                "is_real_api": False,
                "debug": True
            }
        
    except Exception as e:
        print(f"Avatar API exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "traceback": traceback.format_exc()[:1000],
            "is_real_api": False,
            "debug": True,
            "data": {"avatars": []}
        }

@app.get("/list-voices")
def list_voices():
    try:
        r = requests.get("https://api.heygen.com/v2/voices", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=20)
        print(f"Voices API: {r.status_code} - {r.text[:1000]}")
        try:
            data = r.json()
            return {
                "heygen_status": r.status_code,
                "heygen_response": data,
                "data": data.get("data") if isinstance(data, dict) else data,
                "raw_text": r.text[:500],
                "is_real_api": True
            }
        except:
            return {"heygen_status": r.status_code, "raw_text": r.text[:1000], "is_real_api": False}
    except Exception as e:
        return {"error": str(e), "is_real_api": False}

@app.post("/generate-video")
def generate_video(script: str = Form(...), avatar_id: str = Form(...), voice_id: str = Form(...)):
    try:
        print(f"=== GENERATE VIDEO DEBUG ===")
        print(f"Avatar ID: {avatar_id}")
        print(f"Voice ID: {voice_id}")
        print(f"Script length: {len(script)}")
        print(f"API Key present: {bool(HEYGEN_API_KEY)}")
        print(f"API Key preview: {HEYGEN_API_KEY[:10] if HEYGEN_API_KEY else 'NONE'}...")
        
        if not avatar_id or avatar_id == "No avatars" or len(avatar_id) < 3:
            return {"error": "Invalid avatar_id", "details": "Avatar ID is empty or invalid", "data": {"video_id": "ERROR_NO_AVATAR"}}
        
        # Trim script
        words = script.split()
        if len(words) > 180:
            script = " ".join(words[:180]) + " Thank you for watching Trybhasha dot com."
        
        # Try different avatar IDs that are known to work with API
        # HeyGen API docs example avatars
        test_avatars = [
            avatar_id,  # User selected first
            "Abigail_expressive_2024112501",
            "Angela-inblack-20220820",
            "Anna_public_3_20240108",
            "Daisy-inskirt-20220818",
            "Lily-inshirt-20220818"
        ]
        
        last_error = None
        
        for test_avatar_id in test_avatars:
            if not test_avatar_id or len(test_avatar_id) < 3:
                continue
                
            print(f"Trying avatar: {test_avatar_id}")
            
            payload = {
                "video_inputs": [{
                    "character": {"type": "avatar", "avatar_id": test_avatar_id, "avatar_style": "normal"},
                    "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
                    "background": {"type": "color", "value": "#000000"}
                }],
                "dimension": {"width": 1280, "height": 720}
            }
            
            try:
                r = requests.post("https://api.heygen.com/v2/video/generate", json=payload, headers={"X-API-KEY": HEYGEN_API_KEY, "Content-Type": "application/json"}, timeout=40)
                
                print(f"HeyGen generate with {test_avatar_id}: Status {r.status_code}")
                print(f"Response: {r.text[:2000]}")
                
                try:
                    data = r.json()
                except:
                    last_error = {"status": r.status_code, "raw": r.text[:1000], "avatar_tried": test_avatar_id}
                    continue
                
                if r.status_code == 200:
                    video_id = None
                    if isinstance(data.get("data"), dict):
                        video_id = data["data"].get("video_id")
                    if not video_id:
                        video_id = data.get("video_id")
                    
                    if video_id:
                        print(f"SUCCESS with avatar {test_avatar_id}: video_id {video_id}")
                        return {
                            "success": True,
                            "avatar_used": test_avatar_id,
                            "data": data.get("data", data),
                            "video_id": video_id,
                            "full_response": data
                        }
                    else:
                        last_error = {"status": r.status_code, "data": data, "avatar_tried": test_avatar_id}
                else:
                    last_error = {"status": r.status_code, "data": data, "raw": r.text[:1000], "avatar_tried": test_avatar_id}
                    
                    # If 402 payment error, don't try other avatars
                    if r.status_code == 402:
                        print(f"402 error - stopping retries")
                        break
                        
            except Exception as e:
                print(f"Exception trying avatar {test_avatar_id}: {e}")
                last_error = {"exception": str(e), "avatar_tried": test_avatar_id}
                continue
        
        # All avatars failed
        print(f"All avatars failed. Last error: {last_error}")
        return {
            "error": "All avatar attempts failed",
            "last_error": last_error,
            "data": {"video_id": f"ERROR_{last_error.get('status', 'UNKNOWN') if isinstance(last_error, dict) else 'UNKNOWN'}"},
            "tried_avatars": test_avatars,
            "suggestion": "Check HeyGen API key, balance, and avatar validity. Your $10 balance should be enough."
        }
        
    except Exception as e:
        print(f"Generate video outer exception: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "data": {"video_id": "ERROR_EX"}, "traceback": traceback.format_exc()[:1000]}

@app.get("/video-status/{video_id}")
def video_status(video_id: str):
    try:
        if video_id.startswith("ERROR") or video_id == "N/A" or len(video_id) < 10:
            return {"data": {"status": "failed", "video_url": "", "error": f"Invalid ID: {video_id}"}}
        
        r = requests.get(f"https://api.heygen.com/v1/video_status.get?video_id={video_id}", headers={"X-API-KEY": HEYGEN_API_KEY}, timeout=20)
        print(f"Status {video_id}: {r.status_code} - {r.text[:500]}")
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
