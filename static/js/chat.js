/* =====================================================
   CHAT CLIENT LOGIC (FINAL)
   - AES end-to-end
   - phân trái / phải chuẩn
   - KHÔNG emit join
   - room quyết định ở server khi connect
===================================================== */

(function () {
  if (!window.ROOM) {
    console.error("❌ ROOM chưa được set");
    return;
  }

  const ROOM = window.ROOM;
  const KEY = ROOM;

  // 🔑 TRUYỀN ROOM NGAY LÚC CONNECT
  const socket = io({
    query: { room: ROOM }
  });

  let log, input, sendBtn;
  let MY_ID = null;

  /* ================= CONNECT ================= */
  socket.on("connect", () => {
    MY_ID = socket.id;
  });

  /* ================= DOM READY ================= */
  window.addEventListener("DOMContentLoaded", () => {
    log = document.getElementById("chat-log");
    input = document.getElementById("msg");
    sendBtn = document.getElementById("sendBtn");

    if (!log || !input || !sendBtn) {
      alert("❌ Thiếu chat-log / msg / sendBtn");
      return;
    }

    bindEvents();
    loadHistory();
  });

  /* ================= SCROLL ================= */
  function scrollBottom(delay = 0) {
    setTimeout(() => {
      log.scrollTop = log.scrollHeight;
    }, delay);
  }

  /* ================= ADD MESSAGE ================= */
  function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "msg " + type;

    const content = document.createElement("div");
    content.textContent = text;

    const time = document.createElement("div");
    time.className = "time";
    const now = new Date();
    time.textContent =
      now.getHours().toString().padStart(2, "0") + ":" +
      now.getMinutes().toString().padStart(2, "0");

    div.appendChild(content);
    div.appendChild(time);

    log.appendChild(div);
    scrollBottom(50);
  }

  /* ================= LOAD HISTORY ================= */
  function loadHistory() {
    fetch("/history/" + ROOM)
      .then(r => r.json())
      .then(list => {
        list.forEach(m => {
          const text = CryptoJS.AES.decrypt(m.cipher, KEY)
            .toString(CryptoJS.enc.Utf8);

          const type = (m.sender === MY_ID) ? "me" : "other";
          addMessage(text, type);
        });
        scrollBottom(100);
      });
  }

  /* ================= SEND ================= */
  function send() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "me");

    const cipher = CryptoJS.AES.encrypt(text, KEY).toString();

    socket.emit("message", {
      room: ROOM,
      cipher: cipher
    });

    input.value = "";
  }

  /* ================= EVENTS ================= */
  function bindEvents() {
    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") send();
    });
    input.addEventListener("focus", () => scrollBottom(300));
  }

  /* ================= RECEIVE ================= */
  socket.on("message", data => {
    if (data.sender === MY_ID) return;

    const text = CryptoJS.AES.decrypt(data.cipher, KEY)
      .toString(CryptoJS.enc.Utf8);

    addMessage(text, "other");
  });

  /* ================= ONLINE / OFFLINE ================= */
  const onlineStatusEl = document.getElementById("onlineStatus");

  socket.on("presence", count => {
    if (!onlineStatusEl) return;

    if (count >= 2) {
      onlineStatusEl.textContent = "Online";
      onlineStatusEl.className = "status online";
    } else {
      onlineStatusEl.textContent = "Offline";
      onlineStatusEl.className = "status offline";
    }
  });

  /* ================= BLOCK ================= */
  socket.on("blocked", () => {
    alert("Room đã bị khóa");
    location.href = "/";
  });

})();
