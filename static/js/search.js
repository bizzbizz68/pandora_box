async function submitSearch() {
  const input = document.getElementById("q");
  if (!input) {
    alert("❌ Không tìm thấy input");
    return;
  }

  const q = input.value.trim();
  if (!q) return;

  const res = await fetch("/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ q })
  });

  const data = await res.json();

  if (data.type === "chat") {
    location.href = "/chat/" + encodeURIComponent(data.room);
  } else {
    location.href =
      "https://www.google.com/search?q=" + encodeURIComponent(q);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("searchBtn");
  const input = document.getElementById("q");

  if (!btn || !input) {
    alert("❌ Không gắn được sự kiện search");
    return;
  }

  btn.addEventListener("click", submitSearch);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") submitSearch();
  });
});
