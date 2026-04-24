from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = "members.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("❌ DB ERROR:", e)
        return {}


def save_db(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("❌ SAVE ERROR:", e)


@app.route("/save", methods=["POST"])
def save():
    try:
        data = request.json
        chat_id = str(data["chat_id"])
        users = data["users"]

        db = load_db()

        if chat_id not in db:
            db[chat_id] = {}

        for u in users:
            db[chat_id][str(u["id"])] = u["name"]

        save_db(db)

        print(f"💾 SAVE {chat_id} | {len(users)} user")

        return {"status": "ok"}

    except Exception as e:
        print("❌ SAVE ERROR:", e)
        return {"status": "error"}


@app.route("/get", methods=["GET"])
def get():
    try:
        chat_id = request.args.get("chat_id")
        db = load_db()

        result = db.get(chat_id, {})

        print(f"📡 GET {chat_id} | {len(result)} user")

        return jsonify(result)

    except Exception as e:
        print("❌ GET ERROR:", e)
        return jsonify({})


if __name__ == "__main__":
    print("🚀 API RUNNING ON PORT 5000")
    app.run(host="0.0.0.0", port=5000)
