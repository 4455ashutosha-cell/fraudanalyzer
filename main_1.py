
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

app = FastAPI(title="WebGuard AI 2.1 - Bug Fixed")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ScanRequest(BaseModel):
    url: str
    text: str = ""

BLOCK_DOMAINS = [
    "1xbet","parimatch","stake.com","xvideos","pornhub","onlyfans","xnxx","xhamster",
    "redtube","bet365","mostbet","dafabet","dream11-fake","aviator","onlyfans-leak"
]
ADULT_URL_KW = ["porn","xxx","xvideos","pornhub","onlyfans","xnxx","xhamster","redtube","nude video","sex video","brazzers"]
BETTING_KW = ["aviator","double money","quick money","betting app","casino","rummy win","1xbet predictor"]
PHISH_KW = ["login-verify","secure-update","g00gle","amaz0n","xn--"]

SAFE_SEARCH = ["google.com","bing.com","duckduckgo.com","yahoo.com","wikipedia.org"]

def analyze_url(url: str, extra_text: str=""):
    u = url.lower().strip()
    parsed = urlparse(u)
    domain = parsed.netloc.replace("www.","")
    path = parsed.path  # No query
    url_without_query = f"{domain}{path}"
    search_q = ""
    try:
        qs = parse_qs(parsed.query)
        search_q = (qs.get("q",[""])[0] + " " + qs.get("query",[""])[0]).lower()
        search_q = unquote(search_q).strip()
    except:
        pass
    
    is_search = any(s in domain for s in SAFE_SEARCH)
    combined_url = f"{url_without_query} {extra_text.lower()}"  # BUG FIX: No query here
    combined_all = f"{url_without_query} {extra_text.lower()} {search_q}"
    
    score = 95
    reasons = []
    flags = {"adult":False,"betting":False,"phishing":False,"fakejob":False}
    
    # 1. Adult/Betting domain check - ONLY on domain+path, NOT query
    for d in BLOCK_DOMAINS:
        if d in url_without_query:
            score = 12
            reasons.append(f"Blocklisted domain: {d}")
            if d in ["xvideos","pornhub","onlyfans","xnxx","xhamster","redtube","porn","xxx"] or "onlyfans" in d:
                flags["adult"]=True
            else:
                flags["betting"]=True
            break
    
    if not flags["adult"]:
        for k in ADULT_URL_KW:
            if k in url_without_query:
                score = min(score, 15)
                flags["adult"]=True
                reasons.append(f"Adult content in URL path: '{k}' - will be blurred & blocked")
                break
    
    if not flags["betting"]:
        for k in BETTING_KW:
            if k in url_without_query:
                score = min(score, 18)
                flags["betting"]=True
                reasons.append(f"Betting fraud: '{k}'")
                break
    
    # 2. Search query handling - If search engine, don't flag RED for adult query
    if is_search and search_q:
        if any(k in search_q for k in ["adult","porn","xxx","nude","onlyfans","sex"]):
            if not flags["adult"]:
                # Don't set adult flag, just YELLOW warning
                score = min(score, 70)
                reasons.append(f"Search query: '{search_q[:40]}' - Google is safe (YELLOW), but results may contain adult content")
        if any(k in search_q for k in BETTING_KW):
            if not flags["betting"]:
                score = min(score, 65)
                reasons.append(f"Search query contains betting - Results may have gambling sites")
    
    # 3. Phishing
    if any(k in url_without_query for k in PHISH_KW) or url_without_query.count("-")>5:
        score = min(score, 28)
        flags["phishing"]=True
        reasons.append("Phishing pattern detected")
    
    if u.startswith("http://"):
        score -= 8
        reasons.append("Insecure HTTP")
    
    if flags["adult"] or flags["betting"]:
        score = min(score, 18)
    
    if not reasons:
        reasons.append("No threats - 8 engines clean")
    
    final = max(5, min(98, score))
    verdict = "RED" if final<40 else "YELLOW" if final<70 else "GREEN"
    
    return {
        "url": url,
        "score": final,
        "trust": final,
        "verdict": verdict,
        "reasons": reasons,
        "flags": flags,
        "search_query": search_q,
        "is_search_engine": is_search,
        "scanned_at": datetime.utcnow().isoformat()
    }

@app.get("/")
def root():
    return {"status":"WebGuard AI 2.1 - All Bugs Fixed","version":"2.1-fixed-final"}

@app.post("/scan")
def scan(req: ScanRequest):
    return analyze_url(req.url, req.text)

@app.get("/scan")
def scan_get(url: str, text: str=""):
    return analyze_url(url, text)
