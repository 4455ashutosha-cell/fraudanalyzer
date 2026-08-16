
"""
WebGuard AI - WhatsApp Bot via Twilio Sandbox
Real Problem: WhatsApp pe fake job + betting links forward hote hain family groups me
Run: pip install flask twilio requests
Twilio Sandbox: whatsapp:+14155238886
"""
from flask import Flask, request
import requests, os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    import re
    urls = re.findall(r'https?://\S+|\S+\.\S+', incoming_msg)
    if not urls:
        msg.body("🛡️ WebGuard AI\nLink bhejo, main check karunga. Example: google-login-verify.com\n\nPrivacy: IP trace nahi hota.")
        return str(resp)

    url = urls[0]
    if not url.startswith("http"):
        url = "https://" + url

    try:
        r = requests.get(f"{BACKEND_URL}/scan", params={"url": url}, timeout=8).json()
        emoji = "🔴" if r["verdict"]=="RED" else "🟡" if r["verdict"]=="YELLOW" else "🟢"
        reasons = "\n".join(r["reasons"][:4])
        body = (
            f"{emoji} {r['verdict']} - {r['trust']}/100\n"
            f"{url}\n\n"
            f"Reason:\n{reasons}\n\n"
            f"Adult: {'Yes - Blocked' if r['flags']['adult'] else 'No'} | Betting: {'Yes - Blocked' if r['flags']['betting'] else 'No'}\n\n"
            f"IP Privacy: Tumhara IP log nahi hua.\n"
            f"Extension: webguard-ai.vercel.app"
        )
        msg.body(body)
    except Exception as e:
        msg.body(f"Error scanning: {e}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
