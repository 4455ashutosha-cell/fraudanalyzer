
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from datetime import datetime

app = FastAPI(title="WebGuard AI 2.0 API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ScanRequest(BaseModel):
    url: str

BLOCK_DOMAINS = ["1xbet","parimatch","stake","xvideos","pornhub","onlyfans","bet365","dream11-fake","aviator"]
BETTING_KW = ["aviator","double money","quick money","betting","casino","rummy","1xbet"]
ADULT_KW = ["porn","xxx","nude","sex video","onlyfans"]
PHISH_KW = ["login-verify","secure-update","wallet-connect"]

def analyze_url(url: str):
    u = url.lower()
    score = 90
    reasons = []
    flags = {"adult":False,"betting":False,"phishing":False,"ads":False,"fakejob":False}
    risk = 0

    # Domain checks
    if any(d in u for d in BLOCK_DOMAINS):
        score = 12
        reasons.append(f"Blocked domain detected: {u}")
        if any(k in u for k in ADULT_KW): flags["adult"]=True; reasons.append("Adult content category")
        if any(k in u for k in BETTING_KW): flags["betting"]=True; reasons.append("Betting/Gambling category")
        risk+=50
    if len(re.findall(r"-", u))>3 or "g00gle" in u or "amaz0n" in u:
        score -= 35; flags["phishing"]=True; reasons.append("Punycode / typosquatting detected")
        risk+=30
    if any(k in u for k in BETTING_KW):
        score = min(score, 22); flags["betting"]=True; reasons.append("Betting keyword: 'double money / aviator'")
        risk+=25
    if any(k in u for k in ADULT_KW):
        score = min(score, 18); flags["adult"]=True; reasons.append("Adult keyword detected")
        risk+=25
    if any(k in u for k in PHISH_KW):
        score -= 40; flags["phishing"]=True; reasons.append("Phishing pattern detected")
        risk+=30
    if "http://" in u:
        score -= 10; reasons.append("Insecure HTTP")
    if not reasons:
        reasons.append("No major threats found. Domain looks clean.")
    
    final = max(5, min(95, score))
    verdict = "RED" if final<40 else "YELLOW" if final<70 else "GREEN"
    return {"url":url,"score":final,"verdict":verdict,"reasons":reasons,"flags":flags,"risk":risk,"scanned_at":datetime.utcnow().isoformat()}

@app.get("/")
def root():
    return {"status":"WebGuard AI 2.0 API Running","version":"2.0"}

@app.post("/scan")
def scan(req: ScanRequest):
    return analyze_url(req.url)

@app.get("/scan")
def scan_get(url: str):
    return analyze_url(url)

# For bot
@app.get("/telegram")
def telegram_mock(url: str):
    data = analyze_url(url)
    text = f"🛡️ WebGuard AI Result\nScore: {data['score']}/100 - {data['verdict']}\n" + "\n".join(data['reasons'])
    return {"reply": text, "data": data}
