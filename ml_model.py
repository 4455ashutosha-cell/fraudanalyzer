
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import pickle, os

# Feature engineering for URL + page content
def extract_features(url: str, page_text: str=""):
    text = (url + " " + page_text).lower()
    features = {
        "url_length": len(url),
        "dash_count": url.count("-"),
        "has_at": 1 if "@" in url else 0,
        "has_ip": 1 if re.search(r"\d+\.\d+\.\d+\.\d+", url) else 0,
        "suspicious_tld": 1 if any(t in url for t in [".tk",".ml",".xyz",".ga"]) else 0,
        "punycode": 1 if "xn--" in url or "g00gle" in url else 0,
        "betting_kw": 1 if any(k in text for k in ["aviator","double money","betting","casino"]) else 0,
        "adult_kw": 1 if any(k in text for k in ["porn","xxx","nude","onlyfans"]) else 0,
        "job_scam_kw": 1 if any(k in text for k in ["telegram pe contact","registration fee","work from home 50000"]) else 0,
        "payment_kw": 1 if any(k in text for k in ["upi","paytm","phonepe"]) and "fee" in text else 0,
    }
    return features

# Training dataset - PhishTank + custom
TRAIN_DATA = [
    ("http://google-login-verify.tk", "verify your google account login", 1),
    ("https://secure-update-faceb00k.com", "facebook secure update needed", 1),
    ("https://1xbet-aviator-win.com/predictor", "double your money 100% winning trick aviator", 1),
    ("http://onlyfans-leak-free.xyz", "free nudes onlyfans leak download", 1),
    ("https://telegram-job-50k-paytm-fee.com", "work from home 50000 telegram pe contact karo registration fee 499 paytm", 1),
    ("http://upi-betting-100win.ml", "upi betting play and earn quick money", 1),
    ("https://www.irctc.co.in", "indian railway catering and tourism", 0),
    ("https://www.google.com", "search engine", 0),
    ("https://www.amazon.in", "online shopping", 0),
    ("https://www.wikipedia.org", "encyclopedia", 0),
]

def train_model():
    X_text = [url + " " + txt for url, txt, _ in TRAIN_DATA]
    y = [label for _, _, label in TRAIN_DATA]
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=200, ngram_range=(1,2))),
        ("clf", RandomForestClassifier(n_estimators=50, random_state=42))
    ])
    pipeline.fit(X_text, y)
    # Save
    with open("ml_model.pkl","wb") as f:
        pickle.dump(pipeline, f)
    return pipeline

def load_model():
    if os.path.exists("ml_model.pkl"):
        with open("ml_model.pkl","rb") as f:
            return pickle.load(f)
    return train_model()

def predict_scam(url: str, page_text: str=""):
    try:
        model = load_model()
        prob = model.predict_proba([url + " " + page_text])[0]
        # prob[1] = phishing probability
        is_scam = prob[1] > 0.6
        # QR code phishing detection placeholder
        qr_risk = 0
        if "qr" in page_text.lower() or "scan qr" in page_text.lower():
            qr_risk = 20  # Add risk if QR involved
        return {
            "is_scam": bool(is_scam),
            "phishing_prob": float(prob[1]),
            "qr_phishing_risk": qr_risk,
            "features": extract_features(url, page_text)
        }
    except Exception as e:
        return {"is_scam": False, "phishing_prob":0.0, "error":str(e), "features":extract_features(url, page_text)}

# Train on import
if not os.path.exists("ml_model.pkl"):
    train_model()
