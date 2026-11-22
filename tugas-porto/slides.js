const slides = Array.from(document.querySelectorAll(".slide"));
const picker = document.querySelector("#slide-picker");
const previous = document.querySelector("#previous");
const next = document.querySelector("#next");
const counter = document.querySelector("#counter");
const progress = document.querySelector("#progress");
let current = -1;

function showSlide(index, focus = false) {
  if (index === current) return;
  const previousVideo = slides[current]?.querySelector("video");
  if (previousVideo) {
    previousVideo.pause();
    previousVideo.removeAttribute("src");
    previousVideo.load();
  }
  current = index;
  slides.forEach((slide, position) => {
    slide.hidden = position !== index;
    slide.classList.toggle("is-entering", position === index);
  });
  const slide = slides[index];
  const video = slide.querySelector("video");
  if (video) {
    if (!video.hasAttribute("src")) video.src = video.dataset.src;
    video.muted = true;
    // Native controls remain available when the browser blocks autoplay.
    video.play().catch(() => {});
  }
  picker.value = String(index + 1);
  counter.value = `${String(index + 1).padStart(2, "0")} / ${slides.length}`;
  progress.value = index + 1;
  previous.disabled = index === 0;
  next.disabled = index === slides.length - 1;
  if (focus) slide.querySelector("h2").focus({ preventScroll: true });
}

function followHash(focus = false) {
  const index = slides.findIndex(slide => `#${slide.id}` === location.hash);
  showSlide(Math.max(0, index), focus);
}

function go(index) {
  if (index < 0 || index >= slides.length || index === current) return;
  history.pushState(null, "", `#${slides[index].id}`);
  showSlide(index, true);
}

previous.addEventListener("click", () => go(current - 1));
next.addEventListener("click", () => go(current + 1));
picker.addEventListener("change", () => go(Number(picker.value) - 1));
window.addEventListener("hashchange", () => followHash(true));
document.addEventListener("keydown", event => {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
      event.target.closest("select, video, input, textarea, [contenteditable]")) return;
  const targets = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 };
  if (Object.hasOwn(targets, event.key)) {
    event.preventDefault();
    go(targets[event.key]);
  }
});
previous.setAttribute("aria-label", "Slide sebelumnya");
next.setAttribute("aria-label", "Slide berikutnya");
document.querySelector("#navigation").hidden = false;
followHash();

const canvas = document.querySelector("#matrix");
const context = canvas.getContext("2d");
const motion = document.querySelector("#motion");
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
const fullscreen = document.querySelector("#fullscreen");
function updateIcon(button, label, symbol) {
  button.setAttribute("aria-label", label);
  button.title = label;
  button.firstElementChild.textContent = symbol;
}

if (document.fullscreenEnabled) {
  fullscreen.hidden = false;
  fullscreen.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      fullscreen.hidden = true;
    }
  });
  document.addEventListener("fullscreenchange", () => {
    updateIcon(fullscreen, document.fullscreenElement ? "Keluar layar penuh" : "Layar penuh", document.fullscreenElement ? "↙" : "⛶");
  });
}

const alphabet = "0123456789ABCDEF<>:[]";
const cell = 19;
let streams = [];
let timer;
let paused = false;

function resizeMatrix() {
  canvas.width = innerWidth;
  canvas.height = innerHeight;
  const rows = Math.ceil(canvas.height / cell);
  streams = Array.from({ length: Math.ceil(canvas.width / cell) }, (_, index) => ({
    x: index * cell,
    head: Math.random() * (rows + 16),
    speed: .24 + Math.random() * .48,
    trail: 5 + Math.floor(Math.random() * 12),
    symbols: Array.from({ length: 32 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]),
  }));
  drawMatrix();
}

function drawMatrix() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = "14px monospace";
  const rows = Math.ceil(canvas.height / cell);
  for (const stream of streams) {
    const row = Math.floor(stream.head);
    for (let offset = stream.trail; offset >= 0; offset--) {
      const y = (stream.head - offset) * cell;
      if (y < 0 || y > canvas.height + cell) continue;
      context.globalAlpha = .56 * (1 - offset / stream.trail);
      context.fillStyle = offset === 0 ? "#d0fff5" : "#24eca3";
      const glyph = stream.symbols[(row - offset + 32) % 32];
      context.fillText(glyph, stream.x, y);
    }
    stream.head = (stream.head + stream.speed) % (rows + stream.trail);
  }
  context.globalAlpha = 1;
}

function syncMotion() {
  clearInterval(timer);
  motion.hidden = false;
  updateIcon(motion, paused ? "Lanjutkan efek" : "Jeda efek", paused ? "▶" : "Ⅱ");
  if (!paused && !document.hidden) {
    drawMatrix();
    timer = setInterval(drawMatrix, 42);
  }
}

if (context) {
  resizeMatrix();
  syncMotion();
  window.addEventListener("resize", resizeMatrix);
  reducedMotion.addEventListener("change", () => {
    paused = reducedMotion.matches;
    syncMotion();
  });
  document.addEventListener("visibilitychange", syncMotion);
  motion.addEventListener("click", () => { paused = !paused; syncMotion(); });
}
