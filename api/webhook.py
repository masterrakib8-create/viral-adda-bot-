
def setup_page():
    results = {}
    results["token_check"] = graph_get("me?fields=id,name")
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


def process_event(data: dict):
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


app = Flask(__name__)


def handle_get():
    if request.args.get("setup") == "1":
        if request.args.get("token") != VERIFY_TOKEN or not PAGE_ACCESS_TOKEN:
            return "forbidden", 403
        try:
            result = setup_page()
            return jsonify(result)
        except Exception as e:
            return f"setup failed: {e}", 500
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(challenge, mimetype="text/plain")
    return "forbidden", 403


def handle_post():
    data = request.get_json(force=True, silent=True) or {}
    process_event(data)
    return "ok", 200


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return handle_get()
    return handle_post()


@app.route("/api/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return handle_get()
    return handle_post()
