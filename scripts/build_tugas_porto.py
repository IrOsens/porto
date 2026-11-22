"""Regenerate the web slides and PPTX. Requires python-pptx and FFmpeg."""
from html import escape
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tugas-porto"
SITE = "https://irosens.github.io/porto/"

PROJECTS = [
    ("WARNETRA", "Juli 2024 · TSA Game Fest", "2D Artist. Membuat aset visual bersama tim untuk prototipe yang dikerjakan dalam 10 hari.", "warnetra.mp4", "https://wyynnn.itch.io/warnetra"),
    ("Crossing the Road", "Maret 2025 · Proyek pribadi", "Solo developer. Merancang game kasual 3D, memprogram gerak karakter, dan membuat sistem kemunculan rintangan.", "crossing-road.mp4", "https://iroo.itch.io/crossing-the-road-project"),
    ("Precision Shooter", "Mei 2025 · Proyek ujian akhir", "Solo developer. Membuat prototipe FPS dengan fokus pada mekanik menembak dalam dua minggu.", "precision-shooter.mp4", "https://iroo.itch.io/project-uas"),
    ("Project Parkour-Shooter", "Mei 2025 · Proyek pribadi", "Solo developer. Mengembangkan proyek dari konsep hingga demo itch.io, dengan fokus pada pergerakan parkour dan sistem menembak.", "parkour-shooter.mp4", "https://iroo.itch.io/parkour-shooter"),
    ("Bathara Mask", "Januari 2026 · Global Game Jam Malang", "Lead 2D Artist dan Game Developer. Membuat aset pixel art dan membantu pemrograman gameplay selama game jam.", "ggj-2026.mp4", "https://globalgamejam.org/games/2026/bathara-mask-7"),
    ("Hidden Gem", "2025–2026 · Roblox / Lua", "Mengembangkan mekanik gameplay untuk LET’S PLAY INDONESIA, sebuah gim edukasi yang mengenalkan budaya Indonesia melalui eksplorasi.", "hidden-gem.mp4", "https://www.roblox.com/games/83942627805508/Hidden-Gem"),
    ("Lantai Tujuh", "2026 · COMPFEST 18", "Prototipe survival horror dari tim Rajin Menabung. Pemain mencari skripsi yang tertinggal sambil memecahkan teka-teki panel listrik dan menghemat daya senter.", "lantai-tujuh.mp4", "https://iroo.itch.io/compfest-18"),
    ("Fish and Monsters", "Losi Studio · Roblox", "Gim memancing dan menjelajahi pulau. Peran saya: UI Artist, Marketing, Assistant Programmer, dan QA.", "fish-and-monsters.png", "https://www.roblox.com/games/111385005478215/Fish-And-Monsters"),
    ("Hotel Anomaly", "Losi Studio · Roblox", "Gim survival horror tentang sif malam di hotel yang dihuni anomali. Peran saya: Marketing, Assistant Programmer, dan QA.", "hotel-anomaly.webm", "https://www.roblox.com/games/70575351571626/HOTEL-ANOMALY"),
    ("Spider Robot", "Raspberry Pi Pico / Pico W · Repository Program", "Robot laba-laba dengan 12 servo yang bisa berjalan, berputar, dan menjaga posisi badan tetap rata. Versi Pico W juga mendukung kendali via browser ponsel.", "spider-pico.mp4", "https://github.com/IrOsens/spider-pico"),
    ("Semester Terakhir", "Unity / C# · In Progress", "RPG berlatar kampus Indonesia dengan eksplorasi, misi, dan pertarungan bergelombang yang memakai mekanik mengetik.", "semester-terakhir.mp4", ""),
]

OPENING = [
    ("Tugas Portofolio", "Riovaldo Arion Darendra", [
        "Game Developer · Losi Studio",
        "Mahasiswa tingkat akhir D4 Animasi · Universitas Negeri Malang · IPK 3,79",
        "Saya mengembangkan gim Roblox dan prototipe Unity, dengan fokus pada mekanik gameplay menggunakan Lua dan C#.",
    ]),
    ("Jenis portofolio", "Dua cara melihat karya saya", [
        "Playable Prototype — itch.io dan Roblox memberi akses ke karya yang dapat dicoba. Lantai Tujuh menunjukkan eksplorasi dan teka-teki, sementara Hidden Gem menggunakan gameplay untuk mengenalkan budaya Indonesia.",
        "Repository Program — repo Spider Robot menunjukkan kode firmware, dokumentasi kendali dan perakitan, serta demo robot. Semester Terakhir memperlihatkan perkembangan prototipe Unity yang masih dikerjakan.",
    ]),
]
CLOSING = [
    ("Evaluasi", "Kelebihan dan kekurangan", [
        "Kelebihan — Demo memperlihatkan cara kerja proyek. Beberapa karya dapat dicoba langsung, dan entri Losi Studio menjelaskan kontribusi saya dalam tim.",
        "Kekurangan — Tanggal dan rincian kontribusi belum lengkap pada beberapa karya. Instruksi bermain dan dokumentasi teknis belum konsisten. Fish and Monsters memiliki gambar pratinjau, sedangkan Semester Terakhir masih dikembangkan.",
    ]),
    ("Pengembangan", "Rencana perbaikan", [
        "Lengkapi tanggal, kontribusi pribadi, dan kredit tim pada tiap karya.",
        "Tambahkan petunjuk kontrol dan tujuan permainan, lalu minta orang lain mencoba build dan catat kendalanya.",
        "Perkuat README dengan langkah menjalankan, ringkasan arsitektur, dan demo singkat. Perbarui demo Semester Terakhir setelah sistem utamanya stabil.",
    ]),
]

def media_path(name):
    directory = "images" if name.endswith(".png") else "videos"
    return f"assets/{directory}/{name}"

def slides():
    for label, title, paragraphs in OPENING:
        yield label, title, paragraphs, "", ""
    for title, subtitle, description, media, link in PROJECTS:
        yield "Penjelasan karya", title, [subtitle, description], media, link
    for label, title, paragraphs in CLOSING:
        yield label, title, paragraphs, "", ""

def build_web(records):
    deck = []
    options = []
    for number, (label, title, paragraphs, media, link) in enumerate(records, 1):
        options.append(f'<option value="{number}">{number:02} — {escape(title)}</option>')
        copy = "".join(f"<p>{escape(line)}</p>" for line in paragraphs)
        visual = ""
        layout = "project" if media else "editorial"
        if number == 1:
            layout = "identity"
            visual = '<img src="../assets/images/profile-pic.png" alt="Foto Riovaldo Arion Darendra" fetchpriority="high">'
        if media:
            source = "../" + media_path(media)
            if media.endswith(".png"):
                visual = f'<img src="{source}" alt="Gambar resmi {escape(title)}">'
            else:
                poster = f"posters/{Path(media).stem}.webp"
                visual = f'<video controls muted loop playsinline preload="none" poster="{poster}" data-src="{source}" aria-label="Demo {escape(title)}"></video>'
        if link:
            action = "Buka repository" if "github.com" in link else "Buka halaman proyek"
            copy += f'<a class="action" href="{escape(link)}" target="_blank" rel="noopener">{action} ↗</a>'
        deck.append(f"""
        <section class="slide {layout}" id="slide-{number}" aria-labelledby="title-{number}">
          <div class="copy"><p class="label">{label}</p><h2 id="title-{number}" tabindex="-1">{escape(title)}</h2>{copy}</div>
        {f'<div class="media">{visual}</div>' if visual else ''}
        </section>""")
    html = f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tugas Portofolio · Riovaldo Arion Darendra</title>
<link rel="stylesheet" href="slides.css?v=aurora2">
<script src="slides.js?v=aurora2" defer></script>
</head>
<body>
<canvas id="matrix" aria-hidden="true"></canvas>
<div class="shell">
  <header class="bar">
    <a class="brand" href="../">← Portofolio utama</a>
    <div class="tools">
      <button id="fullscreen" type="button" hidden>Layar penuh</button>
      <button id="motion" type="button" hidden>Jeda efek</button>
      <a class="download" href="portofolio-riovaldo.pptx" download>Unduh PPTX ↓</a>
    </div>
  </header>
  <main id="deck" aria-label="Presentasi tugas portofolio">{''.join(deck)}
  </main>
  <nav id="navigation" class="bar" aria-label="Navigasi slide" hidden>
    <button id="previous" type="button">← <span>Sebelumnya</span></button>
    <div class="position">
      <output id="counter" for="slide-picker" aria-live="polite"></output>
      <select id="slide-picker" aria-label="Pilih slide">{''.join(options)}</select>
    </div>
    <button id="next" type="button"><span>Berikutnya</span> →</button>
    <progress id="progress" aria-label="Posisi slide" max="{len(records)}" value="1"></progress>
  </nav>
</div>
</body>
</html>
"""
    (OUT / "index.html").write_text("\n".join(line.rstrip() for line in html.splitlines()) + "\n", encoding="utf-8")

def text(slide, value, x, y, width, height, size, color, *, bold=False):
    shape = slide.shapes.add_textbox(*(Inches(n) for n in (x, y, width, height)))
    shape.text_frame.word_wrap = True
    paragraph = shape.text_frame.paragraphs[0]
    run = paragraph.add_run()
    run.text = value
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    return run

PREVIEW_SECONDS = {
    "precision-shooter.mp4": "12",
    "parkour-shooter.mp4": "12",
    "semester-terakhir.mp4": "25",
}

def build_pptx(records):
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    presentation.core_properties.title = "Portofolio Game Developer"
    presentation.core_properties.author = "Riovaldo Arion Darendra"
    posters = OUT / "posters"
    posters.mkdir(exist_ok=True)
    with TemporaryDirectory() as temporary:
        for number, (label, title, paragraphs, media, link) in enumerate(records, 1):
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string("0D1411")
            text(slide, label.upper(), .6, .45, 8, .35, 13, "9BFFC1", bold=True)
            text(slide, title, .6, 1.05, 12, 1, 38, "F3F9F5", bold=True)
            if media:
                text(slide, paragraphs[0], .6, 2.24, 4.25, .8, 17, "9BFFC1")
                text(slide, paragraphs[1], .6, 3.17, 4.25, 2.5, 22, "F3F9F5")
                poster = Path(temporary) / "preview.jpg"
                source = ROOT / media_path(media)
                seek = [] if media.endswith(".png") else ["-ss", PREVIEW_SECONDS.get(media, "1")]
                run(["ffmpeg", "-loglevel", "error", "-y", *seek, "-i", str(source),
                     "-frames:v", "1", "-vf",
                     "scale=960:540:force_original_aspect_ratio=decrease,pad=960:540:(ow-iw)/2:(oh-ih)/2,setsar=1",
                     str(poster)], check=True)
                if not media.endswith(".png"):
                    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(poster),
                         "-vf", "scale=800:-1", "-quality", "75",
                         str(posters / f"{Path(media).stem}.webp")], check=True)
                image = slide.shapes.add_picture(str(poster), Inches(5.18), Inches(2.22), width=Inches(7.55))
                destination = link if media.endswith(".png") else f"{SITE}tugas-porto/#slide-{number}"
                image.click_action.hyperlink.address = destination
                text(slide, "Klik gambar untuk membuka " + ("halaman proyek" if media.endswith(".png") else "demo"),
                     5.12, 6.5, 7.55, .35, 13, "9BFFC1").hyperlink.address = destination
            elif number == 1:
                for index, line in enumerate(paragraphs):
                    text(slide, line, .6, 2.22 + index * 1.1, 7.8, 1.05, 22, "F3F9F5")
                slide.shapes.add_picture(str(ROOT / "assets/images/profile-pic.png"),
                                         Inches(9.3), Inches(2.2), height=Inches(3.55))
            else:
                for index, line in enumerate(paragraphs):
                    text(slide, line, .6, 2.22 + index * 1.1, 11.7, 1.05, 22, "F3F9F5")
            text(slide, SITE, .6, 6.96, 8, .34, 12, "9BFFC1").hyperlink.address = SITE
            text(slide, f"{number:02} / {len(records):02}", 11.48, 6.96, 1.1, .34, 12, "9BFFC1")
    presentation.save(OUT / "portofolio-riovaldo.pptx")

if __name__ == "__main__":
    records = list(slides())
    build_web(records)
    build_pptx(records)
