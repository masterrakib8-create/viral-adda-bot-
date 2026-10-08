

- ⏰ *Availability* — সকাল ৯টা–রাত ১১টা অনলাইন; এর বাইরে মেসেজ এলে ভদ্র "away" মেসেজ পাঠাবে (সময় আপনি বদলাতে পারবেন)
- 👋 *Get Started বাটন + ওয়েলকাম মেসেজ* — নতুন কেউ মেসেজ করলে সুন্দর স্বাগতম
- 🔘 *Quick Reply বাটন* — 😂 মজার গল্প / ❤️ ভালোবাসার গল্প / 💰 ইনকাম টিপস — চাপলেই AI কনটেন্ট বানিয়ে দেবে
- 📋 *স্থায়ী মেনু* — মেসেঞ্জারের নিচে সবসময় থাকবে
- ⚡ *FAQ কীওয়ার্ড* — "সময়", "যোগাযোগ" লিখলে সাথে সাথে উত্তর (AI খরচ বাঁচে)
- 👤 *এডমিন ডাক* — "এডমিন" লিখলে বিশেষ উত্তর
- ⌨️ *typing...* — উত্তর লেখার সময় টাইপিং দেখাবে

*আপনার কাজ:* GitHub-এ আগের কোডের বদলে *এই নতুন কোডটা* পেস্ট করে Commit করুন (আগেরটা commit করে থাকলে ফাইলটা এডিট করে রিপ্লেস করুন):
```
ভাইরাল আড্ডা — ফ্রি AI মেসেঞ্জার বট (Vercel) v2

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
PAGE_NAME = os.environ.get("PAGE_NAME", "ভাইরাল আড্ডা")

ACTIVE_FROM = int(os.environ.get("ACTIVE_FROM", "9"))
ACTIVE_TO = int(os.environ.get("ACTIVE_TO", "23"))
AWAY_MESSAGE = os.environ.get(
    "AWAY_MESSAGE",
    "🌙 এখন আমরা অনলাইনে নেই।\n"
    "আমাদের সময়: সকাল ৯টা – রাত ১১টা।\n"
    "আপনার মেসেজ লিখে রাখুন, সকালে উত্তর দেব ইনশাআল্লাহ! 🙏",
)

FAQ = {
    "সময়": "⏰ আমাদের অনলাইন সময়: প্রতিদিন সকাল ৯টা – রাত ১১টা।",
    "খোলা": "⏰ আমাদের অনলাইন সময়: প্রতিদিন সকাল ৯টা – রাত ১১টা।",
    "যোগাযোগ": "📩 এই পেজেই মেসেজ করুন — এডমিন দেখে উত্তর দেবেন।",
    "ফোন": "📩 ফোনে নয়, এই পেজে মেসেজ করুন — দ্রুত উত্তর পাবেন।",
    "নাম্বার": "📩 ফোনে নয়, এই পেজে মেসেজ করুন — দ্রুত উত্তর পাবেন।",
    "ভিডিও": "🎬 নতুন মজার ভিডিও পেতে পেজটা ফলো করে রাখুন! ❤️",
    "টিপস": "💰 অনলাইন ইনকাম টিপস পেতে নিচের বাটনে চাপুন 👇",
}

HUMAN_KEYWORDS = ["মানুষ", "এডমিন", "admin", "লোক", "কথা বলব", "সরাসরি"]
HUMAN_REPLY = (
    "👤 ঠিক আছে! আপনার মেসেজটা এডমিনের কাছে পৌঁছে দিচ্ছি।\n"
    "একটু অপেক্ষা করুন, দ্রুত উত্তর দেওয়ার চেষ্টা করব 🙏"
)

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", """তুমি 'ভাইরাল আড্ডা' ফেসবুক পেজের বন্ধুসুলভ AI সহকারী।
- দর্শক যে ভাষায় লিখবে (বাংলা/ইংরেজি), সেই ভাষায় উত্তর দাও। ডিফল্ট বাংলা।
- উত্তর ছোট রাখো — মেসেঞ্জার চ্যাটের মতো, ২-৪ লাইন।
- উষ্ণ, মজার ও সহায়ক হও। ইমোজি মাঝে মাঝে ব্যবহার করো।
- পেজটা বিনোদন (মজার ভিডিও), ভালোবাসার গল্প, আর অনলাইন ইনকাম টিপস নিয়ে।
- ভুল তথ্য দিও না। না জানলে সৎভাবে বলো যে জানো না।
- কখনো বলো না তুমি কোন AI মডেল — তুমি ভাইরাল আড্ডার সহকারী।""")

CATEGORY_PROMPTS = {
    "MENU_FUN": "ভাইরাল আড্ডা পেজের দর্শকের জন্য বাংলায় একটা মজার ছোট জোকস বা মজার গল্প লেখো (৩-৫ লাইন, ইমোজি সহ)।",
    "MENU_LOVE": "ভাইরাল আড্ডা পেজের দর্শকের জন্য বাংলায় একটা ছোট আবেগি ভালোবাসার গল্প বা উক্তি লেখো (৩-৫ লাইন, ইমোজি সহ)।",
    "MENU_INCOME": "ভাইরাল আড্ডা পেজের দর্শকের জন্য বাংলায় একটা সত্যিকারের অনলাইন ইনকাম টিপস দাও (৩-৫ লাইন, সহজ ভাষায়, কোনো ভুয়া প্রতিশ্রুতি নয়)।",
}

QUICK_REPLIES = [
    {"content_type": "text", "title": "😂 মজার গল্প", "payload": "MENU_FUN"},
    {"content_type": "text", "title": "❤️ ভালোবাসার গল্প", "payload": "MENU_LOVE"},
    {"content_type": "text", "title": "💰 ইনকাম টিপস", "payload": "MENU_INCOME"},
]

WELCOME_TEXT = (
    f"🎉 {PAGE_NAME}-তে স্বাগতম!\n"
    "আমি এই পেজের AI সহকারী। নিচ থেকে বেছে নিন, বা যেকোনো প্রশ্ন লিখুন 👇"
)


def dhaka_now():
    return datetime.now(timezone(timedelta(hours=6)))


def is_active_hours() -> bool:
    h = dhaka_now().hour
    if ACTIVE_FROM <= ACTIVE_TO:
        return ACTIVE_FROM <= h < ACTIVE_TO
    return h >= ACTIVE_FROM or h < ACTIVE_TO


def graph_post(path: str, payload: dict, timeout: int = 8):
    url = f"https://graph.facebook.com/v19.0/me/{path}?access_token={PAGE_ACCESS_TOKEN}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.load(res)


def send_text(psid: str, text: str):
    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)] or ["..."]
    for chunk in chunks:
        graph_post("messages", {
            "recipient": {"id": psid},
            "message": {"text": chunk},
        })


def send_with_quick_replies(psid: str, text: str):
    graph_post("messages", {
        "recipient": {"id": psid},
        "message": {"text": text, "quick_replies": QUICK_REPLIES},
    })


def send_action(psid: str, action: str):
    try:
        graph_post("messages", {
            "recipient": {"id": psid},
            "sender_action": action,
        })
    except Exception:
        pass


def gemini_reply(user_text: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = json.dumps({
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_text}]}],
        "generationConfig": {"maxOutputTokens": 500, "temperature": 0.7},
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    })
    with urllib.request.urlopen(req, timeout=8) as res:
        data = json.load(res)
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def ai_answer(psid: str, prompt: str):
    send_action(psid, "typing_on")
    try:
        reply = gemini_reply(prompt)
        send_action(psid, "typing_off")
        send_with_quick_replies(psid, reply)
    except Exception as e:
        print("Gemini error:", e)
        send_action(psid, "typing_off")
        send_text(psid, "😅 একটু সমস্যা হচ্ছে, আবার লিখুন প্লিজ 🙏")


def check_faq(text: str):
    for keyword, answer in FAQ.items():
        if keyword in text:
            return answer
    return None


def handle_text(psid: str, text: str):
    t = text.strip()
    if any(k in t for k in HUMAN_KEYWORDS):
        send_text(psid, HUMAN_REPLY)
        return
    faq = check_faq(t)
    if faq:
        send_with_quick_replies(psid, faq)
        return
    if not is_active_hours():
        send_text(psid, AWAY_MESSAGE)
        return
    ai_answer(psid, t)


def handle_payload(psid: str, payload: str):
    if payload == "GET_STARTED":
        send_with_quick_replies(psid, WELCOME_TEXT)
    elif payload in CATEGORY_PROMPTS:
        ai_answer(psid, CATEGORY_PROMPTS[payload])
    else:
        ai_answer(psid, "হাই!")


def handle_attachment(psid: str):
    send_with_quick_replies(
        psid,
        "📎 পেয়েছি! ছবি/ফাইলের উত্তর আমি দিতে পারি না, "
        "তবে কিছু জানতে চাইলে লিখে পাঠান 😊",
    )


def setup_page():
    results = {}
    results["get_started"] = graph_post("messenger_profile", {
        "get_started": {"payload": "GET_STARTED"},
    })
    results["greeting"] = graph_post("messenger_profile", {
        "greeting": [{"locale": "default",
                      "text": f"{PAGE_NAME} — মজা, গল্প আর ইনকাম টিপস! 💬"}],
    })
    results["menu"] = graph_post("messenger_profile", {
        "persistent_menu": [{
            "locale": "default",
            "composer_input_disabled": False,
            "call_to_actions": [
                {"type": "postback", "title": "😂 মজার গল্প", "payload": "MENU_FUN"},
                {"type": "postback", "title": "❤️ ভালোবাসার গল্প", "payload": "MENU_LOVE"},
                {"type": "postback", "title": "💰 ইনকাম টিপস", "payload": "MENU_INCOME"},
            ],
        }],
    })
    return results


class handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes = b"",
              ctype: str = "text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        if q.get("setup", [""])[0] == "1":
            if q.get("token", [""])[0] != VERIFY_TOKEN or not PAGE_ACCESS_TOKEN:
                self._send(403, b"forbidden")
                return
            try:
                result = setup_page()
                self._send(200, json.dumps(result, ensure_ascii=False).encode(),
                            "application/json")
            except Exception as e:
                self._send(500, f"setup failed: {e}".encode())
            return
        mode = q.get("hub.mode", [""])[0]
        token = q.get("hub.verify_token", [""])[0]
        challenge = q.get("hub.challenge", [""])[0]
        if mode == "subscribe" and token == VERIFY_TOKEN:
            self._send(200, challenge.encode())
        else:
            self._send(403, b"forbidden")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
        try:
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    psid = event["sender"]["id"]
                    postback = event.get("postback")
                    if postback:
                        handle_payload(psid, postback.get("payload", ""))
                        continue
                    message = event.get("message", {})
                    if message.get("is_echo"):
                        continue
                    qr = message.get("quick_reply")
                    if qr:
                        handle_payload(psid, qr.get("payload", ""))
                        continue
                    if "text" in message:
                        send_action(psid, "mark_seen")
                        handle_text(psid, message["text"])
                    elif "attachments" in message:
                        handle_attachment(psid)
        except Exception as e:
            print("Bot error:", e)
        self._send(200, b"ok")
```
