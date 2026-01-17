(function () {
  const root = document.documentElement;

  // load theme đã lưu
  const saved = localStorage.getItem("theme");
  if (saved) root.dataset.theme = saved;

  document.addEventListener("click", e => {
    const btn = e.target.closest("#themeToggle");
    if (!btn) return;

    const next = root.dataset.theme === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    localStorage.setItem("theme", next);
  });
})();
