
import requests, csv, io, json
from datetime import datetime
from sqlalchemy.orm import Session
from models import ThreatLink
import os

# Simulated aggregation - In production, use real API keys
# VirusTotal API: https://www.virustotal.com/api/v3/urls/
# URLhaus: https://urlhaus.abuse.ch/downloads/csv_recent/
# PhishTank: http://data.phishtank.com/data/online-valid.csv

MOCK_THREATS = [
    {"url": "http://google-login-verify.tk", "source": "phishtank", "type": "phishing", "score": 92},
    {"url": "https://1xbet-aviator-win.com", "source": "urlhaus", "type": "betting", "score": 88},
    {"url": "http://onlyfans-leak-free.xyz", "source": "virustotal", "type": "adult", "score": 85},
    {"url": "https://telegram-job-50k-paytm-fee.com", "source": "user_report", "type": "fake_job", "score": 95},
    {"url": "http://upi-betting-100win.ml", "source": "urlhaus", "type": "payment_fraud", "score": 90},
]

def aggregate_threats(db: Session):
    """Aggregate from 3-4 sources + weighted scoring"""
    count=0
    for item in MOCK_THREATS:
        existing = db.query(ThreatLink).filter(ThreatLink.url==item["url"]).first()
        if not existing:
            # Weighted scoring: VirusTotal 0.4, URLhaus 0.3, PhishTank 0.3, UserReport 0.5 boost
            weights = {"virustotal":0.4, "urlhaus":0.3, "phishtank":0.3, "user_report":0.5}
            final_score = item["score"] * weights.get(item["source"],0.3)
            tl = ThreatLink(
                url=item["url"],
                source=item["source"],
                threat_type=item["type"],
                score=final_score,
                metadata_json=json.dumps({"original_score":item["score"],"aggregated":True}),
                first_seen=datetime.utcnow()
            )
            db.add(tl)
            count+=1
    db.commit()
    return count

def get_threat_score(db: Session, url: str):
    """Check custom DB - 100k+ links concept"""
    # Normalize
    u = url.lower().strip()
    # Exact + substring match
    threat = db.query(ThreatLink).filter(ThreatLink.url.contains(u.split("/")[2] if "://" in u else u[:20])).first()
    if threat:
        return {"found":True, "score":threat.score, "type":threat.threat_type, "source":threat.source}
    # Also check mock list
    for m in MOCK_THREATS:
        if m["url"].split("/")[2] in u or m["url"] in u:
            return {"found":True, "score":m["score"], "type":m["type"], "source":m["source"]}
    return {"found":False, "score":0}

def update_from_user_report(db: Session, url: str, category: str):
    """User-reported links -> DB update"""
    existing = db.query(ThreatLink).filter(ThreatLink.url==url).first()
    if existing:
        existing.votes+=1
        existing.score = min(98, existing.score+5)
    else:
        db.add(ThreatLink(url=url, source="user_report", threat_type=category, score=75, metadata_json=json.dumps({"user_reported":True})))
    db.commit()
