const slides = Array.from(document.querySelectorAll(".slide"));
const picker = document.querySelector("#slide-picker");
const previous = document.querySelector("#previous");
const next = document.querySelector("#next");
const counter = document.querySelector("#counter");
const progress = document.querySelector("#progress");
let current = -1;

function showSlide(index, focus = false) {
  if (index === current) return;
  slides[current]?.querySelector("video")?.pause();
  current = index;
  slides.forEach((slide, position) => {
    slide.hidden = position !== index;
    slide.classList.toggle("is-entering", position === index);
  });
  const slide = slides[index];
  const video = slide.querySelector("video");
  if (video && !video.hasAttribute("src")) video.src = video.dataset.src;
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
const symbols = "01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ<>/[]";
const cell = 18;
let columns = [];
let timer;
let paused = false;

function resizeMatrix() {
  canvas.width = innerWidth;
  canvas.height = innerHeight;
  columns = Array.from({ length: Math.ceil(canvas.width / cell) },
    () => Math.floor(Math.random() * (canvas.height / cell + 24)) - 24);
}

function drawMatrix() {
  context.fillStyle = "rgba(7,11,9,.17)";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.font = "14px monospace";
  columns.forEach((row, index) => {
    const glyph = symbols[Math.floor(Math.random() * symbols.length)];
    context.fillStyle = "#39da80";
    context.fillText(glyph, index * cell, (row - 1) * cell);
    context.fillStyle = "#a8ffcf";
    context.fillText(glyph, index * cell, row * cell);
    columns[index] = row * cell > canvas.height && Math.random() > .91 ? 0 : row + 1;
  });
}

function syncMotion() {
  clearInterval(timer);
  motion.hidden = reducedMotion.matches;
  motion.textContent = paused ? "Lanjutkan efek" : "Jeda efek";
  if (!paused && !reducedMotion.matches && !document.hidden) {
    drawMatrix();
    timer = setInterval(drawMatrix, 80);
  }
}

if (context) {
  resizeMatrix();
  syncMotion();
  window.addEventListener("resize", resizeMatrix);
  reducedMotion.addEventListener("change", syncMotion);
  document.addEventListener("visibilitychange", syncMotion);
  motion.addEventListener("click", () => { paused = !paused; syncMotion(); });
}
