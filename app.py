from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, emit
import sqlite3, hashlib

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# -------- DB --------
def get_db():
    return sqlite3.connect("chat.db", check_same_thread=False)

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            room_hash TEXT,
            content TEXT,
            sender TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

def hash_room(room):
    return hashlib.sha256(room.encode()).hexdigest()

# -------- ROUTES --------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat/<room>")
def chat(room):
    return render_template("chat.html", room=room)

@app.route("/history/<room>")
def history(room):
    h = hash_room(room)
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT content, sender FROM messages WHERE room_hash=? ORDER BY created_at",
        (h,)
    )
    return jsonify([
        {"cipher": r[0], "sender": r[1]}
        for r in cur.fetchall()
    ])

@app.route("/check", methods=["POST"])
def check_keyword():
    q = request.get_json().get("q", "").strip()
    q_hash = hashlib.sha256(q.encode()).hexdigest()

    KEYWORD_TO_ROOM = {
        "8fcb25879a66b007def5cf63d7960fdfa2ee1f2b056d9e8e6008e7873a7af202": "room_x",
        "fbf4210de0797bb8c6ad387c9254fddfabcbef22e41be691d071af97a9bbafbb": "room_x",
    }

    if q_hash in KEYWORD_TO_ROOM:
        return jsonify({"type": "chat", "room": KEYWORD_TO_ROOM[q_hash]})

    return jsonify({"type": "google"})

# -------- SOCKET --------
@socketio.on("connect")
def on_connect():
    room = request.args.get("room")
    if not room:
        return

    h = hash_room(room)
    join_room(h)

    # đếm user trong room (Socket.IO internal)
    count = len(socketio.server.manager.rooms["/"].get(h, []))
    emit("presence", count, room=h)

@socketio.on("message")
def on_message(data):
    h = hash_room(data["room"])
    cipher = data["cipher"]
    sender = request.sid

    db = get_db()
    db.execute(
        "INSERT INTO messages (room_hash, content, sender) VALUES (?, ?, ?)",
        (h, cipher, sender)
    )
    db.commit()

    emit("message", {
        "cipher": cipher,
        "sender": sender
    }, room=h)

@socketio.on("disconnect")
def on_disconnect():
    # broadcast lại presence cho tất cả room user từng ở
    for h, sids in socketio.server.manager.rooms["/"].items():
        if request.sid in sids:
            emit("presence", len(sids) - 1, room=h)

# -------- TẠO SEVER TEST --------
# if __name__ == "__main__":
#     init_db()
#     socketio.run(
#         app,
#         host="127.0.0.1",
#         port=5001,
#         debug=False,
#         allow_unsafe_werkzeug=True
#     )
import os

if __name__ == "__main__":
    init_db()
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
