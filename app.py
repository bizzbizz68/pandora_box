import os
import hashlib
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, emit
from drive_store import load_data, save_data

try:
    load_data()
    print("[BOOT] Drive OK", flush=True)
except Exception as e:
    print("[BOOT ERROR]", e, flush=True)
app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"   # ✅ CHUẨN RENDER
)

rooms = {}  # room_hash -> set(socket_id)


def hash_room(room):
    return hashlib.sha256(room.encode()).hexdigest()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat/<room>")
def chat(room):
    return render_template("chat.html", room=room)


@app.route("/history/<room>")
def history(room):
    data = load_data()
    h = hash_room(room)
    return jsonify(data.get(h, []))


@app.route("/check", methods=["POST"])
def check():
    q = request.json.get("q", "").strip()
    h = hashlib.sha256(q.encode()).hexdigest()

    KEYWORDS = {
        "8fcb25879a66b007def5cf63d7960fdfa2ee1f2b056d9e8e6008e7873a7af202": "room_x",
        "fbf4210de0797bb8c6ad387c9254fddfabcbef22e41be691d071af97a9bbafbb": "room_x"
    }

    if h in KEYWORDS:
        return jsonify({"type": "chat", "room": KEYWORDS[h]})

    return jsonify({"type": "google"})


# ================= SOCKET =================

@socketio.on("join")
def on_join(data):
    h = hash_room(data["room"])
    rooms.setdefault(h, set())

    if len(rooms[h]) >= 2:
        emit("blocked")
        return

    rooms[h].add(request.sid)
    join_room(h)
    emit("presence", len(rooms[h]), room=h)


@socketio.on("message")
def on_message(data):
    h = hash_room(data["room"])
    cipher = data["cipher"]

    store = load_data()
    store.setdefault(h, []).append(cipher)
    save_data(store)

    emit("message", cipher, room=h)


@socketio.on("disconnect")
def on_disconnect():
    for h, users in list(rooms.items()):
        if request.sid in users:
            users.remove(request.sid)
            emit("presence", len(users), room=h)
            if not users:
                del rooms[h]


# ================= ENTRY =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True  # ✅ CHỈ DÙNG LOCAL
    )
