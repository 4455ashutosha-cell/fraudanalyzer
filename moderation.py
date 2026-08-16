
from sqlalchemy.orm import Session
from models import UserReport, User, ThreatLink
import json
from threat_intel import update_from_user_report

def calculate_credibility(db: Session, reporter_id: int):
    """ML: Predict if report is credible based on user history"""
    reports = db.query(UserReport).filter(UserReport.reporter_id==reporter_id).all()
    if not reports:
        return 0.5
    approved = sum(1 for r in reports if r.status=="approved")
    total = len(reports)
    credibility = approved / total if total>0 else 0.5
    # Boost if high votes
    avg_votes = sum(r.votes_up for r in reports)/max(1,total)
    credibility = min(0.95, credibility + (avg_votes*0.05))
    return credibility

def submit_report(db: Session, telegram_id: str, url: str, category: str, description: str=""):
    user = db.query(User).filter(User.telegram_id==telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    report = UserReport(
        url=url,
        reporter_id=user.id,
        category=category,
        description=description,
        credibility=calculate_credibility(db, user.id)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def vote_report(db: Session, report_id: int, up: bool=True):
    report = db.query(UserReport).filter(UserReport.id==report_id).first()
    if not report:
        return None
    if up:
        report.votes_up+=1
    else:
        report.votes_down+=1
    # Auto approval logic
    if report.votes_up>=3 and report.votes_up > report.votes_down*2:
        report.status="approved"
        # Auto-update threat DB
        update_from_user_report(db, report.url, report.category)
    elif report.votes_down>=3 and report.votes_down > report.votes_up:
        report.status="rejected"
    db.commit()
    return report

def get_moderation_queue(db: Session):
    return db.query(UserReport).filter(UserReport.status=="pending").order_by(UserReport.credibility.desc()).all()
