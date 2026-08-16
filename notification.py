
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from models import ThreatLink, CheckedLink, ThreatEvent, User
import json

scheduler = BackgroundScheduler()

def check_new_threats_and_notify(db: Session, bot=None):
    """Job queue: When new threat detected -> notify all users who checked similar links"""
    # Get recent threats (last hour)
    new_threats = db.query(ThreatLink).order_by(ThreatLink.first_seen.desc()).limit(5).all()
    for threat in new_threats:
        # Find users who checked similar domain
        similar_users = db.query(CheckedLink).filter(CheckedLink.url.contains(threat.url.split("/")[2][:10])).all()
        user_ids = list(set([c.user_id for c in similar_users]))
        if user_ids:
            # Create threat event
            event = ThreatEvent(
                url=threat.url,
                event_type="similar_threat",
                notified_users=json.dumps(user_ids)
            )
            db.add(event)
            db.commit()
            print(f"[NOTIFY] Threat {threat.url} -> Notifying {len(user_ids)} users")
            # In production: send Telegram message via bot
            # for uid in user_ids:
            #     user = db.query(User).filter(User.id==uid).first()
            #     bot.send_message(chat_id=user.telegram_id, text=f"⚠️ New threat similar to link you checked: {threat.url}")
    db.commit()

def start_scheduler(db_factory):
    def job():
        db = db_factory()
        try:
            check_new_threats_and_notify(db)
        finally:
            db.close()
    scheduler.add_job(job, "interval", minutes=60)
    scheduler.start()
    print("Notification pipeline started - checks every 60 min")
