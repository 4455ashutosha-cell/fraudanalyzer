
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, index=True)
    risk_score = Column(Float, default=0.0)  # 0-100
    total_checks = Column(Integer, default=0)
    phishing_checks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatLink(Base):
    __tablename__ = "threat_links"
    id = Column(Integer, primary_key=True)
    url = Column(String, index=True, unique=True)
    source = Column(String)  # virustotal, urlhaus, phishtank, user_report
    threat_type = Column(String)  # phishing, betting, adult, payment_fraud
    score = Column(Float)  # 0-100 malicious
    metadata_json = Column(Text)
    first_seen = Column(DateTime, default=datetime.utcnow)
    votes = Column(Integer, default=0)

class CheckedLink(Base):
    __tablename__ = "checked_links"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String, index=True)
    result_verdict = Column(String)  # RED/YELLOW/GREEN
    result_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True)
    url = Column(String, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)  # phishing, betting, adult, fake_job
    description = Column(Text)
    votes_up = Column(Integer, default=0)
    votes_down = Column(Integer, default=0)
    credibility = Column(Float, default=0.5)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatEvent(Base):
    __tablename__ = "threat_events"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    event_type = Column(String)  # new_threat, similar_threat
    notified_users = Column(Text)  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)
