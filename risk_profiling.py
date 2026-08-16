
from sqlalchemy.orm import Session
from models import User, CheckedLink
from datetime import datetime, timedelta

def get_or_create_user(db: Session, telegram_id: str):
    user = db.query(User).filter(User.telegram_id==telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def log_checked_link(db: Session, telegram_id: str, url: str, verdict: str, score: float):
    user = get_or_create_user(db, telegram_id)
    user.total_checks+=1
    if verdict=="RED":
        user.phishing_checks+=1
    # Risk score = phishing ratio
    if user.total_checks>0:
        user.risk_score = (user.phishing_checks / user.total_checks) * 100
    
    cl = CheckedLink(user_id=user.id, url=url, result_verdict=verdict, result_score=score)
    db.add(cl)
    db.commit()
    return user

def get_user_dashboard(db: Session, telegram_id: str):
    user = db.query(User).filter(User.telegram_id==telegram_id).first()
    if not user:
        return {"exists":False}
    # Compare to avg
    avg_phishing_rate = 15  # avg user checks 15% phishing
    user_rate = (user.phishing_checks / max(1,user.total_checks))*100
    more_likely = user_rate - avg_phishing_rate
    return {
        "telegram_id": telegram_id,
        "total_checks": user.total_checks,
        "phishing_checks": user.phishing_checks,
        "risk_score": round(user.risk_score,2),
        "message": f"You are {round(more_likely,1)}% more likely to click phishing than avg user" if more_likely>0 else "You are safer than average",
        "risk_level": "HIGH" if user.risk_score>40 else "MEDIUM" if user.risk_score>15 else "LOW"
    }
