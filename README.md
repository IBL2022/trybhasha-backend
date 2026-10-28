# Trybhasha Backend - IBL International LLC
Full Functional AI Video Platform Backend

## Deploy to Render.com
1. Fork this repo
2. Go to render.com > New Web Service > Connect this repo
3. Add Env Variables:
   - HEYGEN_API_KEY
   - OPENAI_API_KEY
4. Build: pip install -r requirements.txt
5. Start: uvicorn main:app --host 0.0.0.0 --port 10000

## API Endpoints
- GET / -> Check status
- POST /generate-script -> Topic to Script
- POST /clone-voice -> 5/6 min voice upload
- POST /generate-video -> 60 sec video
- GET /list-avatars -> Your presenter avatars
- GET /list-voices -> Your cloned voices
- GET /video-status/{video_id} -> Check video ready

Built for Trybhasha.com - Billion Dollar Company
