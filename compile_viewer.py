#!/usr/bin/env python3
"""
Menggabungkan products_catalog.json, fabric_normals.js, dan Three.js viewer
menjadi file index.html yang 100% self-contained tanpa ketergantungan file lokal eksternal.
Mendukung:
1. UV projection lurus sempurna di tengah dada dan pinggang (u=0.5 di sumbu depan, phiStart=-PI)
2. Tanpa garis potongan atau bercak putih (seamless edge feathering & alpha segmentation)
3. Fitur Input / Unggah Foto Pakaian Sendiri dengan auto-segmentasi, pelurusan, dan slider presisi.
"""
import json, re

with open('products_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open('fabric_normals.js', 'r', encoding='utf-8') as f:
    normals_js = f.read()

# Ekstrak objek JSON dari fabric_normals.js
normals_match = re.search(r'window\.FABRIC_NORMALS\s*=\s*(\{.*?\});', normals_js, re.DOTALL)
if normals_match:
    normals = json.loads(normals_match.group(1))
else:
    normals = {}

html_content = f'''
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Gunakan: Visualisasi Body 3D Realistis</title>
<style>
:root{{
  --bg:#FFFFFF;--stage:#E2E6EC;--ink:#141316;--mut:#625c64;--line:#ded6cc;
  --brand:#6D001A;--onbrand:#FFFFFF;--panel:#FFFFFF;--gold:#B38728;
  --success:#1f8247;--warn:#d47e17;--danger:#bd3030;
  --stage-bg:radial-gradient(circle at 50% 38%, #F2F4F8 0%, #DFE4EC 55%, #C2C9D6 100%);
  box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)
}}
@media (prefers-color-scheme:dark){{
  :root:not([data-theme="light"]){{
    --bg:#121013;--stage:#18161b;--ink:#f6f1eb;--mut:#a49ba1;--line:#383136;
    --brand:#d84a6e;--onbrand:#121013;--panel:#1a1619;
    --stage-bg:radial-gradient(circle at 50% 38%, #28252d 0%, #17151b 60%, #0c0b0e 100%);
  }}
}}
:root[data-theme="dark"]{{
  --bg:#121013;--stage:#18161b;--ink:#f6f1eb;--mut:#a49ba1;--line:#383136;
  --brand:#d84a6e;--onbrand:#121013;--panel:#1a1619;
  --stage-bg:radial-gradient(circle at 50% 38%, #28252d 0%, #17151b 60%, #0c0b0e 100%);
}}
*{{box-sizing:border-box}}
html,body{{height:100%;margin:0;scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--ink);font-family:"Segoe UI",system-ui,-apple-system,sans-serif;font-size:13.5px;text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}}
.app{{display:grid;grid-template-columns:1fr 400px;height:100%}}
#stage{{
  position:relative;
  background:var(--stage-bg, radial-gradient(circle at 50% 38%, #F2F4F8 0%, #DFE4EC 55%, #C2C9D6 100%));
  min-height:50vh;
  overflow:hidden;
  transition:background .35s ease
}}
#stage canvas{{display:block;width:100%;height:100%}}

/* Floating Badges */
.stage-overlay{{position:absolute;left:14px;top:14px;right:14px;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;z-index:6}}
.fit-tags{{display:flex;gap:8px;flex-wrap:wrap;pointer-events:auto}}
.chip{{background:rgba(255,255,255,0.88);border:1px solid rgba(0,0,0,0.08);border-radius:999px;padding:6px 14px;font-size:12px;box-shadow:0 4px 16px rgba(0,0,0,0.06);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);display:inline-flex;align-items:center;gap:6px;transition:all .25s cubic-bezier(0.16, 1, 0.3, 1)}}
.chip b{{color:var(--brand)}}
.chip-status{{width:8px;height:8px;border-radius:50%;display:inline-block;transition:background .3s ease}}
.status-pas{{background:var(--success)}}
.status-ketat{{background:var(--danger)}}
.status-longgar{{background:var(--warn)}}

.studio-badge{{background:rgba(18,17,20,0.85);color:#fff;border-radius:999px;padding:6px 14px;font-size:11px;letter-spacing:0.5px;font-weight:600;display:flex;align-items:center;gap:6px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:0 4px 14px rgba(0,0,0,0.1)}}
.studio-badge span{{color:#FFD700}}

/* Floating Camera Quick View Toolbar */
.cam-pills{{position:absolute;bottom:46px;left:50%;transform:translateX(-50%);display:flex;gap:6px;background:rgba(255,255,255,0.86);padding:5px 8px;border-radius:999px;border:1px solid rgba(0,0,0,0.08);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 6px 20px rgba(0,0,0,0.08);z-index:5;max-width:92%;overflow-x:auto}}
.cam-pill{{border:0;background:transparent;color:var(--mut);padding:5px 12px;font-size:11.5px;font-weight:600;border-radius:999px;cursor:pointer;white-space:nowrap;transition:all 0.25s cubic-bezier(0.16, 1, 0.3, 1)}}
.cam-pill:hover{{color:var(--ink);background:rgba(0,0,0,0.05)}}
.cam-pill.on{{background:var(--brand);color:#fff;box-shadow:0 2px 8px rgba(109,0,26,0.25)}}

.hint{{position:absolute;left:50%;transform:translateX(-50%);bottom:12px;color:var(--mut);font-size:11px;pointer-events:none;background:rgba(255,255,255,0.84);padding:4px 14px;border-radius:999px;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);box-shadow:0 2px 8px rgba(0,0,0,0.03);white-space:nowrap;z-index:4}}

/* Aside Sidebar */
aside{{overflow-y:auto;padding:20px 22px;border-left:1px solid var(--line);background:var(--bg);scroll-behavior:smooth}}
h1{{font-size:21px;margin:0 0 4px;color:var(--brand);display:flex;align-items:center;gap:8px}}
.badge-prem{{font-size:10px;background:var(--brand);color:var(--onbrand);padding:2px 7px;border-radius:4px;letter-spacing:0.6px;font-weight:700}}
.sub{{color:var(--mut);margin:0 0 16px;font-size:12px;line-height:1.45}}

fieldset{{border:1px solid var(--line);border-radius:12px;margin:0 0 14px;padding:12px 14px;background:var(--panel);box-shadow:0 2px 8px rgba(0,0,0,0.02)}}
legend{{padding:0 8px;font-weight:700;color:var(--ink);font-size:11.5px;text-transform:uppercase;letter-spacing:0.6px}}

.row{{display:grid;grid-template-columns:84px 1fr 52px;align-items:center;gap:8px;margin:8px 0}}
.row label{{font-size:12.5px;color:var(--ink)}}
.row output{{text-align:right;color:var(--mut);font-variant-numeric:tabular-nums;font-weight:600}}

/* Sleek Smooth Range Sliders */
input[type=range]{{
  -webkit-appearance:none;appearance:none;width:100%;height:6px;background:#e2ddd5;border-radius:999px;outline:none;transition:background .2s ease
}}
input[type=range]::-webkit-slider-thumb{{
  -webkit-appearance:none;appearance:none;width:16px;height:16px;border-radius:50%;background:var(--brand);cursor:pointer;box-shadow:0 2px 6px rgba(109,0,26,0.3);transition:transform .15s cubic-bezier(0.16, 1, 0.3, 1),box-shadow .15s ease
}}
input[type=range]::-webkit-slider-thumb:hover{{
  transform:scale(1.18);box-shadow:0 3px 10px rgba(109,0,26,0.45)
}}
input[type=range]:active::-webkit-slider-thumb{{
  transform:scale(1.28)
}}

button,select{{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 12px;cursor:pointer;transition:all .2s cubic-bezier(0.16, 1, 0.3, 1)}}
button:focus-visible,select:focus-visible,input:focus-visible{{outline:2px solid var(--brand);outline-offset:2px}}
button.on{{background:var(--brand);color:var(--onbrand);border-color:var(--brand)}}

/* Product cards with real catalog photos */
.prods-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:10px 0 6px}}
.prod-card{{display:flex;flex-direction:column;border:1.5px solid var(--line);border-radius:10px;background:var(--panel);padding:6px;cursor:pointer;text-align:left;position:relative;transition:all .25s cubic-bezier(0.16, 1, 0.3, 1)}}
.prod-card:hover{{border-color:var(--brand);transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,0.06)}}
.prod-card.on{{border-color:var(--brand);box-shadow:0 0 0 2px var(--brand);background:rgba(109,0,26,0.02);transform:scale(1.02)}}
.prod-card .img-box{{width:100%;aspect-ratio:1/1;border-radius:8px;overflow:hidden;background:#f5f5f5;margin-bottom:6px;display:flex;align-items:center;justify-content:center}}
.prod-card img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s cubic-bezier(0.16, 1, 0.3, 1)}}
.prod-card:hover img{{transform:scale(1.05)}}
.prod-card .p-name{{font-size:11.5px;font-weight:600;line-height:1.25;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:29px}}
.prod-card .p-price{{font-size:11.5px;color:var(--brand);font-weight:700;margin-top:2px}}
.prod-desc-box{{font-size:11.5px;color:var(--mut);background:rgba(0,0,0,0.02);border-radius:8px;padding:8px 10px;margin-top:6px;line-height:1.45;border-left:3px solid var(--brand);transition:all .2s ease}}

.line{{display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap}}
.note{{font-size:11.5px;color:var(--mut);margin:8px 0 0;line-height:1.5}}
.btn-action{{padding:8px 14px;font-weight:600;border-radius:8px;font-size:12px}}

/* Toggle Tabs */
.seg-control{{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;margin-top:6px;background:var(--panel)}}
.seg-control button{{flex:1;border:0;border-radius:0;padding:6px 8px;font-size:11.5px;font-weight:600;background:transparent;color:var(--mut);transition:all .2s ease}}
.seg-control button.on{{background:var(--brand);color:#fff}}

/* Avatar Color Picker Swatches */
.color-picker-row{{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-top:2px}}
.color-dot{{width:22px;height:22px;border-radius:50%;cursor:pointer;border:2px solid transparent;transition:all .2s ease;box-shadow:0 1px 4px rgba(0,0,0,0.18);position:relative}}
.color-dot:hover{{transform:scale(1.15)}}
.color-dot.on{{transform:scale(1.18);box-shadow:0 0 0 2px var(--panel), 0 0 0 4px var(--brand)}}

.upload-zone{{
  border:2px dashed var(--line);
  border-radius:10px;
  padding:14px;
  text-align:center;
  background:rgba(0,0,0,0.015);
  cursor:pointer;
  transition:all .2s ease;
  margin-top:8px;
}}
.upload-zone:hover{{
  border-color:var(--brand);
  background:rgba(109,0,26,0.03);
}}

@media (max-width:760px){{
  .app{{grid-template-columns:1fr;grid-template-rows:55vh auto;height:auto}}
  aside{{border-left:0;border-top:1px solid var(--line)}}
  .cam-pills{{bottom:38px}}
}}
</style>
</head>
<body>
<div class="app">
  <!-- Area Panggung 3D -->
  <div id="stage">
    <div class="stage-overlay">
      <div class="fit-tags">
        <div class="chip"><span class="chip-status" id="dotTop"></span> Atasan: <b id="fitTop">-</b></div>
        <div class="chip"><span class="chip-status" id="dotBot"></span> Celana: <b id="fitBot">-</b></div>
      </div>
      <div class="studio-badge">
        <span>★</span> STUDIO 3D ULTRA-REALISTIK
      </div>
    </div>
    <div class="cam-pills" id="camPills">
      <button type="button" class="cam-pill on" data-angle="front">Depan</button>
      <button type="button" class="cam-pill" data-angle="side">Samping</button>
      <button type="button" class="cam-pill" data-angle="back">Belakang</button>
      <button type="button" class="cam-pill" data-angle="top">Fokus Baju</button>
      <button type="button" class="cam-pill" data-angle="bot">Fokus Celana</button>
      <button type="button" class="cam-pill" id="stageSpinBtn">Auto Putar</button>
    </div>
    <div class="hint">Geser mouse/layar untuk rotasi 360° • Scroll untuk zoom • Dobel-klik untuk reset kamera</div>
  </div>

  <!-- Sidebar Kontrol -->
  <aside>
    <h1>Gunakan 3D <span class="badge-prem">AVATAR 3D</span></h1>
    <p class="sub">Visualisasi fitting pakaian realistis pada karakter avatar 3D yang dapat dikustomisasi (rambut, kulit, wajah, sepatu) sesuai gaya dan postur tubuh Anda.</p>

    <!-- Kustomisasi Karakter Game (Avatar 3D) -->
    <fieldset>
      <legend>Karakter Avatar 3D (Game Customizer)</legend>
      <div class="row"><label>Tipe Karakter</label>
        <div class="seg-control" id="charGender" style="grid-column:span 2">
          <button type="button" class="on" data-val="male">Pria (Atletis)</button>
          <button type="button" data-val="female">Wanita (Slender)</button>
        </div>
      </div>
      <div class="row"><label>Warna Kulit</label>
        <div class="color-picker-row" id="skinTonePicker" style="grid-column:span 2"></div>
      </div>
      <div class="row"><label>Gaya Rambut</label>
        <div style="grid-column:span 2">
          <select id="hairStyleSelect" style="width:100%;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font-weight:600;cursor:pointer">
            <option value="undercut" selected>Modern Undercut Fade</option>
            <option value="curtain">K-Pop Curtain Part</option>
            <option value="crop">Messy Streetwear Crop</option>
            <option value="wavy">Wavy Flow / Panjang</option>
            <option value="buzz">Military Buzz Cut</option>
            <option value="bald">Botak / Shaved</option>
          </select>
        </div>
      </div>
      <div class="row"><label>Warna Rambut</label>
        <div class="color-picker-row" id="hairColorPicker" style="grid-column:span 2"></div>
      </div>
      <div class="row"><label>Kumis / Jenggot</label>
        <div class="seg-control" id="charBeard" style="grid-column:span 2">
          <button type="button" class="on" data-val="stubble">Stubble</button>
          <button type="button" data-val="clean">Bersih</button>
          <button type="button" data-val="goatee">Goatee</button>
          <button type="button" data-val="full">Jenggot</button>
        </div>
      </div>
      <div class="row"><label>Kacamata</label>
        <div class="seg-control" id="charGlasses" style="grid-column:span 2">
          <button type="button" class="on" data-val="none">Tanpa</button>
          <button type="button" data-val="wayfarer">Wayfarer</button>
          <button type="button" data-val="round">Metal Bulat</button>
        </div>
      </div>
      <div class="row"><label>Sepatu</label>
        <div class="seg-control" id="charShoes" style="grid-column:span 2">
          <button type="button" class="on" data-val="sneakers">Sneakers Putih</button>
          <button type="button" data-val="boots">Chelsea Boots</button>
          <button type="button" data-val="loafers">Loafers</button>
        </div>
      </div>
    </fieldset>

    <!-- Kontrol Visual & Pencahayaan -->
    <fieldset>
      <legend>Lingkungan Studio & Tekstur</legend>
      <div class="row"><label>Latar Studio</label>
        <div class="seg-control" id="bgPreset" style="grid-column:span 2">
          <button type="button" class="on" data-val="neutral">Abu-abu (Kontras)</button>
          <button type="button" data-val="minimal">Putih Studio</button>
          <button type="button" data-val="dark">Dark Noir</button>
        </div>
      </div>
      <div class="row"><label>Pencahayaan</label>
        <div class="seg-control" id="lightPreset" style="grid-column:span 2">
          <button type="button" class="on" data-val="softbox">Softbox Studio</button>
          <button type="button" data-val="editorial">Editorial Rim</button>
          <button type="button" data-val="bright">Clean Retail</button>
        </div>
      </div>
      <div class="row" style="margin-top:8px">
        <label>Detail Kain</label>
        <div style="grid-column:span 2;display:flex;align-items:center;gap:12px">
          <label style="font-size:12px;cursor:pointer"><input type="checkbox" id="wrinklesOn" checked> Lipatan & Tekstur Tenun 3D</label>
        </div>
      </div>
    </fieldset>

    <!-- Data Tubuh -->
    <fieldset>
      <legend>Ukuran Tubuh Pengguna</legend>
      <div class="row"><label for="H">Tinggi</label><input id="H" type="range" min="0" max="220" value="170"><output></output></div>
      <div class="row"><label for="W">Berat</label><input id="W" type="range" min="0" max="160" value="65"><output></output></div>
      <div class="row"><label for="C">Lingkar dada</label><input id="C" type="range" min="0" max="160" value="92"><output></output></div>
      <div class="row"><label for="P">Lingkar pinggang</label><input id="P" type="range" min="0" max="150" value="76"><output></output></div>
      <div class="row"><label for="B">Lebar bahu</label><input id="B" type="range" min="0" max="65" value="42"><output></output></div>
      <div style="margin:8px 0 6px 0;display:flex;align-items:center;gap:7px">
        <input type="checkbox" id="autoSyncBody" checked style="cursor:pointer;accent-color:var(--brand)">
        <label for="autoSyncBody" style="font-size:11.5px;color:var(--mut);cursor:pointer;user-select:none">Sesuaikan LD, LP, & Bahu otomatis dari TB & BB</label>
      </div>
      <div class="line"><button id="est" type="button" class="btn-action" style="width:100%">Hitung Ulang Estimasi dari TB & BB</button></div>
    </fieldset>

    <!-- Atasan -->
    <fieldset>
      <legend>Atasan (Foto Produk Asli)</legend>
      <div class="line" style="justify-content:space-between">
        <label style="font-weight:600;cursor:pointer"><input type="checkbox" id="topOn" checked> Tampilkan Atasan</label>
        <label>Size: <select id="topSize"></select></label>
      </div>
      <div class="prods-grid" id="topProds"></div>
      <div class="prod-desc-box" id="topDesc">-</div>
    </fieldset>

    <!-- Celana -->
    <fieldset>
      <legend>Celana (Foto Produk Asli)</legend>
      <div class="line" style="justify-content:space-between">
        <label style="font-weight:600;cursor:pointer"><input type="checkbox" id="botOn" checked> Tampilkan Celana</label>
        <label>Size: <select id="botSize"></select></label>
      </div>
      <div class="prods-grid" id="botProds"></div>
      <div class="prod-desc-box" id="botDesc">-</div>
    </fieldset>

    <!-- Fitur Input / Unggah Foto Pakaian Sendiri -->
    <fieldset>
      <legend>Input Foto Pakaian Sendiri</legend>
      <div style="font-size:12px;color:var(--mut);line-height:1.45;margin-bottom:6px">
        Unggah foto pakaian (kaos, kemeja, celana). Sistem secara otomatis menghapus background, meluruskan posisi grafis di tengah tubuh, dan memetakan tekstur tanpa potongan.
      </div>
      <div class="row">
        <label>Kategori</label>
        <div class="seg-control" id="customCategory" style="grid-column:span 2">
          <button type="button" class="on" data-val="top">Atasan (Baju)</button>
          <button type="button" data-val="bot">Bawahan (Celana)</button>
        </div>
      </div>
      <input type="file" id="customFileInput" accept="image/*" style="display:none">
      <div class="upload-zone" id="uploadZone">
        <div style="font-weight:600;color:var(--brand);margin-bottom:2px">Pilih / Drag Foto Pakaian</div>
        <div style="font-size:11px;color:var(--mut)">JPG, PNG, atau WEBP</div>
      </div>

      <!-- Slider Presisi Penataan Lurus -->
      <div id="tuneBox" style="display:none;margin-top:10px;padding-top:8px;border-top:1px dashed var(--line)">
        <div style="font-size:11.5px;font-weight:700;color:var(--brand);margin-bottom:6px">Pengaturan Presisi Posisi Lurus</div>
        <div class="row">
          <label style="font-size:11px">Geser X (Lurus)</label>
          <input id="tuneX" type="range" min="-0.25" max="0.25" step="0.005" value="0">
          <output id="tuneXOut">0%</output>
        </div>
        <div class="row">
          <label style="font-size:11px">Geser Y</label>
          <input id="tuneY" type="range" min="-0.25" max="0.25" step="0.005" value="0">
          <output id="tuneYOut">0%</output>
        </div>
        <div class="row">
          <label style="font-size:11px">Skala Ukuran</label>
          <input id="tuneScale" type="range" min="0" max="1.5" step="0.02" value="1.0">
          <output id="tuneScaleOut">100%</output>
        </div>
        <div class="line" style="margin-top:6px">
          <button id="btnResetTune" type="button" style="font-size:11px;padding:4px 8px;width:100%">Reset Posisi Lurus Default</button>
        </div>
      </div>
    </fieldset>

    <!-- Kontrol Kamera -->
    <div class="line">
      <button id="spin" type="button" class="btn-action">Putar 360°</button>
      <button id="reset" type="button" class="btn-action">Reset Kamera</button>
    </div>
    <p class="note">Transisi produk berjalan halus secara real-time. Manekin tetap stabil dan pakaian berganti seketika saat kartu produk ditekan.</p>
  </aside>
</div>

<!-- Three.js CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<!-- Embedded Inline Catalogs (100% Bebas CORS & Self-Contained) -->
<script>
window.PRODUCT_CATALOG = {json.dumps(catalog, ensure_ascii=False)};
window.FABRIC_NORMALS = {json.dumps(normals, ensure_ascii=False)};
</script>

<script>
(function(){{
"use strict";
const stage = document.getElementById('stage');
const SC = 0.01; // 1 cm = 0.01 unit scene

/* ---------- DATA UKURAN PAKAIAN ---------- */
const TOP_SIZES = {{XS:86, S:92, M:98, L:104, XL:110, "2XL":116, "3XL":122}};
const BOT_SIZES = {{XS:68, S:74, M:80, L:86, XL:92, "2XL":98, "3XL":104}};

const catalog = window.PRODUCT_CATALOG;
const normals = window.FABRIC_NORMALS;

const state = {{
  H: 170, W: 65, C: 92, P: 76, B: 42,
  top: 0, bot: 0,
  topSize: "M", botSize: "L",
  topOn: true, botOn: true,
  gender: "male",
  skinTone: "warm",
  hairStyle: "undercut",
  hairColor: "black",
  beard: "stubble",
  glasses: "none",
  shoes: "sneakers",
  bg: "neutral",
  light: "softbox",
  wrinkles: true,
  customCat: "top"
}};

/* ---------- Scene & Renderer Setup ---------- */
let renderer;
try {{
  renderer = new THREE.WebGLRenderer({{
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
    precision: "highp"
  }});
}} catch(e) {{
  stage.innerHTML = '<p style="padding:24px">Perangkat tidak mendukung WebGL.</p>';
  return;
}}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);

/* ---------- Studio Lighting System ---------- */
const keyLight = new THREE.DirectionalLight(0xfff6ea, 2.2);
keyLight.position.set(2.8, 3.8, 4.2);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.bias = -0.00015;
keyLight.shadow.radius = 3.2; // Bayangan sangat halus (soft shadow)
keyLight.shadow.camera.left = -1.2;
keyLight.shadow.camera.right = 1.2;
keyLight.shadow.camera.top = 2.4;
keyLight.shadow.camera.bottom = -0.5;
keyLight.shadow.camera.near = 0.5;
keyLight.shadow.camera.far = 8;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xd4e4ff, 1.15);
fillLight.position.set(-3.2, 2.0, 3.0);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffffff, 2.2);
rimLight.position.set(0, 3.2, -3.2);
scene.add(rimLight);

const kickerLight = new THREE.DirectionalLight(0xffeedd, 1.0);
kickerLight.position.set(2.4, 1.0, -2.4);
scene.add(kickerLight);

const kickerLeft = new THREE.DirectionalLight(0xddeeff, 1.0);
kickerLeft.position.set(-2.4, 1.0, -2.4);
scene.add(kickerLeft);

const hemiLight = new THREE.HemisphereLight(0xffffff, 0xc0c8d6, 0.95);
hemiLight.position.set(0, 4, 0);
scene.add(hemiLight);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
scene.add(ambientLight);

function setLightingPreset(preset){{
  state.light = preset;
  if(preset === 'softbox'){{
    keyLight.intensity = 2.2; fillLight.intensity = 1.15; rimLight.intensity = 2.0; kickerLight.intensity = 1.0; kickerLeft.intensity = 1.0;
    hemiLight.intensity = 0.95; ambientLight.intensity = 0.45;
  }} else if(preset === 'editorial'){{
    keyLight.intensity = 1.6; fillLight.intensity = 0.7; rimLight.intensity = 3.4; kickerLight.intensity = 1.8; kickerLeft.intensity = 1.8;
    hemiLight.intensity = 0.6; ambientLight.intensity = 0.25;
  }} else if(preset === 'bright'){{
    keyLight.intensity = 2.8; fillLight.intensity = 1.6; rimLight.intensity = 1.4; kickerLight.intensity = 0.7; kickerLeft.intensity = 0.7;
    hemiLight.intensity = 1.2; ambientLight.intensity = 0.65;
  }}
  renderer.render(scene, camera);
}}

/* Studio Shadow Plane */
const shadowGeo = new THREE.PlaneGeometry(14, 14);
const shadowMat = new THREE.ShadowMaterial({{opacity: 0.26}});
const shadowPlane = new THREE.Mesh(shadowGeo, shadowMat);
shadowPlane.rotation.x = -Math.PI / 2;
shadowPlane.position.y = -0.01;
shadowPlane.receiveShadow = true;
scene.add(shadowPlane);

/* Ambient Radial Contact Shadow Disk (Mulus & Alami) */
const contactCanvas = document.createElement('canvas');
contactCanvas.width = 256;
contactCanvas.height = 256;
const cCtx = contactCanvas.getContext('2d');
const cGrad = cCtx.createRadialGradient(128, 128, 20, 128, 128, 120);
cGrad.addColorStop(0, 'rgba(18, 15, 14, 0.42)');
cGrad.addColorStop(0.35, 'rgba(18, 15, 14, 0.20)');
cGrad.addColorStop(0.7, 'rgba(18, 15, 14, 0.05)');
cGrad.addColorStop(1, 'rgba(18, 15, 14, 0)');
cCtx.fillStyle = cGrad;
cCtx.fillRect(0, 0, 256, 256);
const contactTex = new THREE.CanvasTexture(contactCanvas);
const contactMat = new THREE.MeshBasicMaterial({{map: contactTex, transparent: true, opacity: 0.85, depthWrite: false}});
const contactPlane = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.75), contactMat);
contactPlane.rotation.x = -Math.PI / 2;
contactPlane.position.y = 0.001;
scene.add(contactPlane);

/* Controls */
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.rotateSpeed = 0.7;
controls.zoomSpeed = 0.75;
controls.autoRotateSpeed = 1.0;
controls.minDistance = 0.9;
controls.maxDistance = 6.0;
controls.maxPolarAngle = Math.PI / 2 + 0.04;
controls.target.set(0, 0.92, 0);

/* Main Scene Groups */
const world = new THREE.Group();
world.scale.set(SC, SC, SC);
scene.add(world);

const mannequinGroup = new THREE.Group();
const topGroup = new THREE.Group();
const botGroup = new THREE.Group();
world.add(mannequinGroup);
world.add(topGroup);
world.add(botGroup);

/* Smooth Camera Interpolation / Gliding */
let camAnim = null;
function smoothCameraTo(targetCamPos, targetLookAt, duration = 650){{
  if(camAnim) cancelAnimationFrame(camAnim);
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const startTime = performance.now();

  function step(now){{
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    // Smooth easeInOutCubic
    const ease = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;

    camera.position.lerpVectors(startPos, targetCamPos, ease);
    controls.target.lerpVectors(startTarget, targetLookAt, ease);
    controls.update();

    if(progress < 1){{
      camAnim = requestAnimationFrame(step);
    }} else {{
      camAnim = null;
    }}
  }}
  camAnim = requestAnimationFrame(step);
}}

function resetCam(smooth = true){{
  const h = state.H * SC;
  const targetLook = new THREE.Vector3(0, h * 0.52, 0);
  const targetPos = new THREE.Vector3(0, h * 0.56, h * 2.35);
  if(smooth){{
    smoothCameraTo(targetPos, targetLook, 650);
  }} else {{
    controls.target.copy(targetLook);
    camera.position.copy(targetPos);
    controls.update();
  }}
}}

function setCameraAngle(angle){{
  const h = state.H * SC;
  let targetLook = new THREE.Vector3(0, h * 0.52, 0);
  let targetPos;

  if(angle === 'front'){{
    targetPos = new THREE.Vector3(0, h * 0.56, h * 2.35);
  }} else if(angle === 'side'){{
    targetPos = new THREE.Vector3(h * 2.3, h * 0.56, 0);
  }} else if(angle === 'back'){{
    targetPos = new THREE.Vector3(0, h * 0.56, -h * 2.35);
  }} else if(angle === 'top'){{
    targetLook = new THREE.Vector3(0, h * 0.70, 0);
    targetPos = new THREE.Vector3(0, h * 0.73, h * 1.35);
  }} else if(angle === 'bot'){{
    targetLook = new THREE.Vector3(0, h * 0.35, 0);
    targetPos = new THREE.Vector3(0, h * 0.36, h * 1.55);
  }}
  if(targetPos){{
    smoothCameraTo(targetPos, targetLook, 700);
  }}
}}

function resize(){{
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}}
new ResizeObserver(resize).observe(stage);
stage.addEventListener('dblclick', resetCam);

/* ---------- Texture & Pre-compiled Materials Engine ---------- */
function loadTexture(src, isRepeat, rx, ry, ox){{
  if(!src) return null;
  const img = new Image();
  const tx = new THREE.Texture(img);
  tx.encoding = THREE.sRGBEncoding;
  tx.generateMipmaps = true;
  tx.minFilter = THREE.LinearMipmapLinearFilter;
  tx.magFilter = THREE.LinearFilter;
  if(typeof renderer !== 'undefined' && renderer && renderer.capabilities){{
    tx.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 16);
  }}
  if(isRepeat){{
    tx.wrapS = THREE.RepeatWrapping;
    tx.wrapT = THREE.RepeatWrapping;
    tx.repeat.set(rx || 1, ry || 1);
  }} else {{
    tx.wrapS = THREE.RepeatWrapping;
    tx.wrapT = THREE.ClampToEdgeWrapping;
    tx.repeat.set(rx || 1, ry || 1);
  }}
  tx.offset.x = (ox !== undefined) ? ox : 0;

  img.onload = function(){{
    tx.needsUpdate = true;
    if(typeof renderer !== 'undefined' && renderer && renderer.capabilities){{
      tx.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 16);
    }}
    if(typeof renderer !== 'undefined' && renderer) renderer.render(scene, camera);
  }};
  img.src = src;
  if(img.complete && img.naturalWidth > 0){{
    tx.needsUpdate = true;
  }}
  return tx;
}}

// Pre-load normal maps
const normalTextures = {{}};
Object.keys(normals).forEach(k => {{
  const isTiling = k.startsWith('fabric_');
  normalTextures[k] = loadTexture(normals[k], isTiling, isTiling ? 3 : 1, isTiling ? 3 : 1, 0);
}});

// Game Avatar Dictionaries & Materials
const SKIN_TONES = {{
  fair: {{ hex: 0xf6dbcf, css: '#f6dbcf', label: 'Cerah (Fair)' }},
  warm: {{ hex: 0xe6be9d, css: '#e6be9d', label: 'Langsat (Natural)' }},
  tan: {{ hex: 0xc69275, css: '#c69275', label: 'Sawo Matang (Tan)' }},
  bronze: {{ hex: 0x925f44, css: '#925f44', label: 'Eksotis (Bronze)' }},
  espresso: {{ hex: 0x583b2a, css: '#583b2a', label: 'Espresso (Deep)' }}
}};

const HAIR_COLORS = {{
  black: {{ hex: 0x181619, css: '#181619', label: 'Hitam Alami' }},
  darkbrown: {{ hex: 0x3d271d, css: '#3d271d', label: 'Cokelat Espresso' }},
  caramel: {{ hex: 0x764f35, css: '#764f35', label: 'Karamel Ash' }},
  blonde: {{ hex: 0xcbb17b, css: '#cbb17b', label: 'Blonde Emas' }},
  silver: {{ hex: 0xd4d8de, css: '#d4d8de', label: 'Silver Platinum' }},
  burgundy: {{ hex: 0x611524, css: '#611524', label: 'Merah Burgundy' }}
}};

const charSkinMat = new THREE.MeshStandardMaterial({{
  color: (SKIN_TONES[state.skinTone] || SKIN_TONES.warm).hex,
  roughness: 0.52,
  metalness: 0.02
}});

const charHairMat = new THREE.MeshStandardMaterial({{
  color: (HAIR_COLORS[state.hairColor] || HAIR_COLORS.black).hex,
  roughness: 0.44,
  metalness: 0.08
}});

const charEyebrowMat = new THREE.MeshStandardMaterial({{
  color: (HAIR_COLORS[state.hairColor] || HAIR_COLORS.black).hex,
  roughness: 0.65,
  metalness: 0.02
}});

const charEyeWhiteMat = new THREE.MeshStandardMaterial({{
  color: 0xf7f7fa,
  roughness: 0.15,
  metalness: 0.0
}});

const charIrisMat = new THREE.MeshStandardMaterial({{
  color: 0x342217,
  roughness: 0.22,
  metalness: 0.04
}});

const charPupilMat = new THREE.MeshBasicMaterial({{
  color: 0x050505
}});

const charUnderwearMat = new THREE.MeshStandardMaterial({{
  color: 0x1a1920,
  roughness: 0.82,
  metalness: 0.02
}});

function getMannequinMaterial(){{
  return charSkinMat;
}}

function updateCharacterSkin(){{
  const tone = SKIN_TONES[state.skinTone] || SKIN_TONES.warm;
  charSkinMat.color.setHex(tone.hex);
  charSkinMat.needsUpdate = true;
  buildAllGeometries();
  renderer.render(scene, camera);
}}

function updateCharacterHair(){{
  const hCol = HAIR_COLORS[state.hairColor] || HAIR_COLORS.black;
  charHairMat.color.setHex(hCol.hex);
  charHairMat.needsUpdate = true;
  charEyebrowMat.color.setHex(hCol.hex);
  charEyebrowMat.needsUpdate = true;
  buildAllGeometries();
  renderer.render(scene, camera);
}}

// Pre-create all product materials with correct textures (Lurus sempurna, ox=0)
const topMaterials = [];
catalog.tops.forEach((p, idx) => {{
  const fType = p.fabric_type || 'cotton';
  const torsoDiffuse = loadTexture(p.torso_b64 || p.torso_url, false, 1, 1, 0);
  const sleeveDiffuse = loadTexture(p.sleeve_b64 || p.sleeve_url, true, 2, 2, 0);

  const torsoMat = new THREE.MeshStandardMaterial({{
    color: new THREE.Color(p.color_hex || 0xffffff),
    map: torsoDiffuse,
    normalMap: normalTextures.top_wrinkles || null,
    normalScale: new THREE.Vector2(0.8, 0.8),
    roughness: 0.76,
    metalness: 0.03,
    polygonOffset: true,
    polygonOffsetFactor: -1.0,
    polygonOffsetUnits: -4.0,
    side: THREE.DoubleSide
  }});

  const sleeveMat = new THREE.MeshStandardMaterial({{
    color: new THREE.Color(p.color_hex || 0xffffff),
    map: sleeveDiffuse,
    normalMap: normalTextures['fabric_' + fType] || normalTextures.fabric_cotton || null,
    normalScale: new THREE.Vector2(0.9, 0.9),
    roughness: 0.76,
    metalness: 0.03,
    polygonOffset: true,
    polygonOffsetFactor: -1.0,
    polygonOffsetUnits: -4.0,
    side: THREE.DoubleSide
  }});

  topMaterials.push({{torso: torsoMat, sleeve: sleeveMat, mainTex: torsoDiffuse}});
}});

const botMaterials = [];
catalog.bottoms.forEach((p, idx) => {{
  const fType = p.fabric_type || 'denim';
  const waistDiffuse = loadTexture(p.waist_b64 || p.waist_url, false, 1, 1, 0);
  const legDiffuse = loadTexture(p.leg_b64 || p.leg_url, true, 2, 3, 0);

  const waistMat = new THREE.MeshStandardMaterial({{
    color: new THREE.Color(p.color_hex || 0xffffff),
    map: waistDiffuse,
    normalMap: normalTextures.pants_wrinkles || null,
    normalScale: new THREE.Vector2(0.85, 0.85),
    roughness: 0.80,
    metalness: 0.03,
    polygonOffset: true,
    polygonOffsetFactor: -1.0,
    polygonOffsetUnits: -4.0,
    side: THREE.DoubleSide
  }});

  const legMat = new THREE.MeshStandardMaterial({{
    color: new THREE.Color(p.color_hex || 0xffffff),
    map: legDiffuse,
    normalMap: normalTextures['fabric_' + fType] || normalTextures.fabric_denim || null,
    normalScale: new THREE.Vector2(0.9, 0.9),
    roughness: 0.80,
    metalness: 0.03,
    polygonOffset: true,
    polygonOffsetFactor: -1.0,
    polygonOffsetUnits: -4.0,
    side: THREE.DoubleSide
  }});

  botMaterials.push({{waist: waistMat, leg: legMat, mainTex: waistDiffuse}});
}});

/* ---------- Geometry Helpers ---------- */
const rad = c => c / (2 * Math.PI);
let SX = 1.18, SZ = 0.82;

/* LatheGeometry dengan phiStart=-Math.PI:
   - Sisi depan (facing camera +Z) berada tepat di u=0.5 (tengah horizontal tekstur)
   - Garis jahitan (seam u=0.0 / u=1.0) berada di belakang punggung (-Z) sehingga TIDAK TERLIHAT dari depan
   - Posisi grafis/resleting 100% LURUS tanpa miring dan tanpa potongan */
function createLatheMesh(pts, mat, sx, sz){{
  const curve = new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(p[0], p[1], 0)), false, 'catmullrom', 0.5);
  const v = curve.getPoints(96).map(p => new THREE.Vector2(Math.max(p.x, 0.1), p.y));
  const geo = new THREE.LatheGeometry(v, 96, -Math.PI, 2 * Math.PI);
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, mat);
  m.scale.set(sx || 1, 1, sz || 1);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}}

function createCylMesh(rt, rb, y0, y1, x, mat){{
  const h = Math.max(0.001, y1 - y0);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(Math.max(0.01, rt), Math.max(0.01, rb), h, 64, 1, true), mat);
  m.position.set(x, (y0 + y1) / 2, 0);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}}

function createTorusRing(rMajor, rMinor, y, mat, sx, sz){{
  const m = new THREE.Mesh(new THREE.TorusGeometry(Math.max(0.01, rMajor), Math.max(0.01, rMinor), 24, 64), mat);
  m.rotation.x = Math.PI / 2;
  m.position.y = y;
  m.scale.set(sx || 1, sz || 1, 1);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}}

function fitStatus(diff, tightLimit, looseLimit){{
  if(diff < tightLimit) return {{label: "Ketat (Slim)", class: "status-ketat"}};
  if(diff > looseLimit) return {{label: "Longgar (Relaxed)", class: "status-longgar"}};
  return {{label: "Pas (Ideal)", class: "status-pas"}};
}}

/* ---------- Character Avatar Generators ---------- */
function createCharacterHand(side, armR, H, skinMat){{
  const hg = new THREE.Group();
  hg.position.y = -0.325 * H;

  // Palm
  const palm = new THREE.Mesh(new THREE.BoxGeometry(armR * 0.88, armR * 1.15, armR * 0.42), skinMat);
  palm.position.set(0, -armR * 0.5, 0);
  palm.castShadow = true; palm.receiveShadow = true;
  hg.add(palm);

  // Thumb
  const thumb = new THREE.Mesh(new THREE.CylinderGeometry(armR * 0.18, armR * 0.22, armR * 0.72, 16), skinMat);
  thumb.rotation.set(0.35, 0, -side * 0.55);
  thumb.position.set(side * armR * 0.42, -armR * 0.35, armR * 0.25);
  thumb.castShadow = true; thumb.receiveShadow = true;
  hg.add(thumb);

  // 4 fingers
  const fingerWidths = [0.18, 0.19, 0.18, 0.16];
  const fingerLengths = [0.85, 0.95, 0.90, 0.75];
  for(let i = 0; i < 4; i++){{
    const fx = (i - 1.5) * armR * 0.24 * side;
    const fl = armR * fingerLengths[i];
    const finger = new THREE.Mesh(new THREE.CylinderGeometry(armR * fingerWidths[i] * 0.9, armR * fingerWidths[i], fl, 14), skinMat);
    finger.rotation.x = 0.22 + i * 0.04;
    finger.position.set(fx, -armR * 1.05 - fl * 0.45, (0.05 + i * 0.02) * armR);
    finger.castShadow = true; finger.receiveShadow = true;
    hg.add(finger);
  }}

  return hg;
}}

function createCharacterShoe(side, lx, ankle, H, state){{
  const sg = new THREE.Group();
  sg.position.set(side * lx, 0, 0.032 * H);

  if(state.shoes === 'boots'){{
    const leatherMat = new THREE.MeshStandardMaterial({{color: 0x1e1916, roughness: 0.35, metalness: 0.08}});
    const bootSoleMat = new THREE.MeshStandardMaterial({{color: 0x111111, roughness: 0.8, metalness: 0.0}});

    const sole = new THREE.Mesh(new THREE.BoxGeometry(ankle * 1.48, 0.024 * H, ankle * 2.85), bootSoleMat);
    sole.position.set(0, 0.012 * H, 0);
    sole.castShadow = true; sole.receiveShadow = true;
    sg.add(sole);

    const bootUpper = new THREE.Mesh(new THREE.BoxGeometry(ankle * 1.38, 0.035 * H, ankle * 2.65), leatherMat);
    bootUpper.position.set(0, 0.035 * H, 0);
    bootUpper.castShadow = true; bootUpper.receiveShadow = true;
    sg.add(bootUpper);

    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(ankle * 0.68, ankle * 0.72, 0.058 * H, 24), leatherMat);
    shaft.position.set(0, 0.068 * H, -ankle * 0.35);
    shaft.castShadow = true; shaft.receiveShadow = true;
    sg.add(shaft);

  }} else if(state.shoes === 'loafers'){{
    const loaferMat = new THREE.MeshStandardMaterial({{color: 0x3d2419, roughness: 0.32, metalness: 0.06}});
    const loaferSole = new THREE.Mesh(new THREE.BoxGeometry(ankle * 1.38, 0.016 * H, ankle * 2.7), new THREE.MeshStandardMaterial({{color: 0x221812, roughness: 0.6}}));
    loaferSole.position.set(0, 0.008 * H, 0);
    loaferSole.castShadow = true; loaferSole.receiveShadow = true;
    sg.add(loaferSole);

    const loaferUpper = new THREE.Mesh(new THREE.SphereGeometry(ankle * 0.72, 24, 18), loaferMat);
    loaferUpper.scale.set(0.92, 0.55, 1.7);
    loaferUpper.position.set(0, 0.026 * H, ankle * 0.25);
    loaferUpper.castShadow = true; loaferUpper.receiveShadow = true;
    sg.add(loaferUpper);

  }} else {{
    // Default: Clean White Sneakers
    const soleMat = new THREE.MeshStandardMaterial({{color: 0xf0f2f5, roughness: 0.65, metalness: 0.02}});
    const upperMat = new THREE.MeshStandardMaterial({{color: 0xffffff, roughness: 0.45, metalness: 0.02}});
    const accentMat = new THREE.MeshStandardMaterial({{color: 0x242426, roughness: 0.5, metalness: 0.05}});

    const sole = new THREE.Mesh(new THREE.BoxGeometry(ankle * 1.45, 0.022 * H, ankle * 2.8), soleMat);
    sole.position.set(0, 0.011 * H, 0);
    sole.castShadow = true; sole.receiveShadow = true;
    sg.add(sole);

    const upper = new THREE.Mesh(new THREE.BoxGeometry(ankle * 1.35, 0.032 * H, ankle * 2.6), upperMat);
    upper.position.set(0, 0.032 * H, -ankle * 0.05);
    upper.castShadow = true; upper.receiveShadow = true;
    sg.add(upper);

    const toeCap = new THREE.Mesh(new THREE.SphereGeometry(ankle * 0.68, 20, 16), upperMat);
    toeCap.scale.set(0.95, 0.55, 1.25);
    toeCap.position.set(0, 0.025 * H, ankle * 0.95);
    toeCap.castShadow = true; toeCap.receiveShadow = true;
    sg.add(toeCap);

    const collar = new THREE.Mesh(new THREE.CylinderGeometry(ankle * 0.65, ankle * 0.68, 0.026 * H, 24), accentMat);
    collar.position.set(0, 0.054 * H, -ankle * 0.45);
    collar.castShadow = true; collar.receiveShadow = true;
    sg.add(collar);

    const laces = new THREE.Mesh(new THREE.BoxGeometry(ankle * 0.72, 0.004 * H, ankle * 0.85), soleMat);
    laces.rotation.x = -0.32;
    laces.position.set(0, 0.046 * H, ankle * 0.28);
    laces.castShadow = true; laces.receiveShadow = true;
    sg.add(laces);
  }}

  return sg;
}}

function buildCharacterHead(headGroup, skinMat, hairMat, eyebrowMat, state){{
  const H = state.H;

  // 1. Cranium & Skull
  const cranium = new THREE.Mesh(new THREE.SphereGeometry(Math.max(0.01, 0.063 * H), 48, 36), skinMat);
  cranium.scale.set(0.86, 1.05, 0.96);
  cranium.position.set(0, 0.008 * H, -0.006 * H);
  headGroup.add(cranium);

  // 2. Jaw & Chin & Cheeks
  const jaw = new THREE.Mesh(new THREE.CylinderGeometry(0.054 * H, 0.034 * H, 0.052 * H, 32), skinMat);
  jaw.scale.set(state.gender === 'female' ? 0.80 : 0.85, 1, 0.75);
  jaw.position.set(0, -0.028 * H, 0.012 * H);
  headGroup.add(jaw);

  const chin = new THREE.Mesh(new THREE.SphereGeometry(0.018 * H, 24, 20), skinMat);
  chin.scale.set(state.gender === 'female' ? 0.85 : 1.0, 0.85, 1.15);
  chin.position.set(0, -0.052 * H, 0.026 * H);
  headGroup.add(chin);

  [-1, 1].forEach(side => {{
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.020 * H, 24, 16), skinMat);
    cheek.scale.set(0.65, 0.85, 0.9);
    cheek.position.set(side * 0.038 * H, -0.012 * H, 0.025 * H);
    headGroup.add(cheek);

    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.018 * H, 24, 16), skinMat);
    ear.scale.set(0.25, 1.15, 0.65);
    ear.rotation.set(0, 0, side * 0.12);
    ear.position.set(side * 0.056 * H, -0.005 * H, -0.008 * H);
    headGroup.add(ear);
  }});

  // 3. Eyes
  [-1, 1].forEach(side => {{
    const eyeGroup = new THREE.Group();
    eyeGroup.position.set(side * 0.023 * H, -0.004 * H, 0.048 * H);
    eyeGroup.rotation.y = side * 0.06;

    const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.0085 * H, 24, 18), charEyeWhiteMat);
    sclera.scale.set(1.15, 0.9, 0.95);
    eyeGroup.add(sclera);

    const iris = new THREE.Mesh(new THREE.CircleGeometry(0.0046 * H, 24), charIrisMat);
    iris.position.set(0, 0, 0.0082 * H);
    eyeGroup.add(iris);

    const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.0022 * H, 16), charPupilMat);
    pupil.position.set(0, 0, 0.0084 * H);
    eyeGroup.add(pupil);

    const glint = new THREE.Mesh(new THREE.CircleGeometry(0.0009 * H, 12), new THREE.MeshBasicMaterial({{color: 0xffffff}}));
    glint.position.set(0.0015 * H, 0.0016 * H, 0.0085 * H);
    eyeGroup.add(glint);

    const upperLid = new THREE.Mesh(new THREE.TorusGeometry(0.0082 * H, 0.0015 * H, 12, 24, Math.PI * 0.85), skinMat);
    upperLid.rotation.set(Math.PI * 0.18, 0, Math.PI * 0.08 * side);
    upperLid.position.set(0, 0.0035 * H, 0.003 * H);
    eyeGroup.add(upperLid);

    headGroup.add(eyeGroup);
  }});

  // 4. Eyebrows
  [-1, 1].forEach(side => {{
    const brow = new THREE.Mesh(new THREE.BoxGeometry(0.024 * H, 0.0032 * H, 0.004 * H), eyebrowMat);
    brow.position.set(side * 0.024 * H, 0.010 * H, 0.052 * H);
    brow.rotation.set(0.12, side * 0.18, -side * 0.14);
    headGroup.add(brow);
  }});

  // 5. 3D Sculpted Nose
  const noseBridge = new THREE.Mesh(new THREE.CylinderGeometry(0.0035 * H, 0.0055 * H, 0.028 * H, 16), skinMat);
  noseBridge.rotation.x = -0.28;
  noseBridge.position.set(0, -0.010 * H, 0.054 * H);
  headGroup.add(noseBridge);

  const noseTip = new THREE.Mesh(new THREE.SphereGeometry(0.0058 * H, 20, 16), skinMat);
  noseTip.scale.set(1.15, 0.95, 1.1);
  noseTip.position.set(0, -0.022 * H, 0.058 * H);
  headGroup.add(noseTip);

  [-1, 1].forEach(side => {{
    const nostril = new THREE.Mesh(new THREE.SphereGeometry(0.0032 * H, 16, 12), skinMat);
    nostril.position.set(side * 0.0055 * H, -0.023 * H, 0.054 * H);
    headGroup.add(nostril);
  }});

  // 6. Lips
  const lipMat = skinMat.clone();
  lipMat.color = skinMat.color.clone().lerp(new THREE.Color(0xa84855), state.gender === 'female' ? 0.45 : 0.28);
  lipMat.roughness = 0.38;

  const upperLip = new THREE.Mesh(new THREE.TorusGeometry(0.011 * H, 0.0024 * H, 12, 24, Math.PI), lipMat);
  upperLip.rotation.x = Math.PI * 0.52;
  upperLip.position.set(0, -0.035 * H, 0.046 * H);
  headGroup.add(upperLip);

  const lowerLip = new THREE.Mesh(new THREE.SphereGeometry(0.0085 * H, 20, 16), lipMat);
  lowerLip.scale.set(1.4, 0.45, 0.7);
  lowerLip.position.set(0, -0.040 * H, 0.047 * H);
  headGroup.add(lowerLip);

  // 7. Facial Hair / Beard
  if(state.gender !== 'female' && (state.beard === 'stubble' || state.beard === 'goatee' || state.beard === 'full')){{
    const beardColor = hairMat.color.clone().lerp(new THREE.Color(0x111111), 0.35);
    const stubbleMat = new THREE.MeshStandardMaterial({{
      color: beardColor,
      roughness: 0.82,
      metalness: 0.0
    }});

    if(state.beard === 'stubble'){{
      const stubble = new THREE.Mesh(new THREE.CylinderGeometry(0.0545 * H, 0.033 * H, 0.038 * H, 32, 1, true, -Math.PI * 0.55, Math.PI * 1.1), stubbleMat);
      stubble.scale.set(0.87, 1, 0.77);
      stubble.position.set(0, -0.036 * H, 0.013 * H);
      headGroup.add(stubble);
    }} else if(state.beard === 'goatee'){{
      const mustache = new THREE.Mesh(new THREE.TorusGeometry(0.012 * H, 0.0028 * H, 12, 24, Math.PI * 0.8), stubbleMat);
      mustache.rotation.x = Math.PI * 0.5;
      mustache.position.set(0, -0.032 * H, 0.049 * H);
      headGroup.add(mustache);

      const chinBeard = new THREE.Mesh(new THREE.ConeGeometry(0.012 * H, 0.024 * H, 20), stubbleMat);
      chinBeard.rotation.x = Math.PI * 0.95;
      chinBeard.position.set(0, -0.058 * H, 0.030 * H);
      headGroup.add(chinBeard);
    }} else if(state.beard === 'full'){{
      const fullBeard = new THREE.Mesh(new THREE.CylinderGeometry(0.056 * H, 0.038 * H, 0.050 * H, 32, 1, false, -Math.PI * 0.65, Math.PI * 1.3), stubbleMat);
      fullBeard.scale.set(0.89, 1.05, 0.82);
      fullBeard.position.set(0, -0.039 * H, 0.016 * H);
      headGroup.add(fullBeard);

      const chinExt = new THREE.Mesh(new THREE.SphereGeometry(0.022 * H, 24, 20), stubbleMat);
      chinExt.scale.set(1.1, 1.0, 1.25);
      chinExt.position.set(0, -0.062 * H, 0.028 * H);
      headGroup.add(chinExt);
    }}
  }}

  // 8. Glasses
  if(state.glasses === 'wayfarer'){{
    const glassGroup = new THREE.Group();
    glassGroup.position.set(0, -0.003 * H, 0.056 * H);
    const frameMat = new THREE.MeshStandardMaterial({{color: 0x151515, roughness: 0.15, metalness: 0.2}});
    const lensMat = new THREE.MeshStandardMaterial({{color: 0x181818, roughness: 0.05, transparent: true, opacity: 0.82}});

    [-1, 1].forEach(side => {{
      const rim = new THREE.Mesh(new THREE.BoxGeometry(0.026 * H, 0.018 * H, 0.003 * H), frameMat);
      rim.position.x = side * 0.024 * H;
      glassGroup.add(rim);

      const lens = new THREE.Mesh(new THREE.PlaneGeometry(0.022 * H, 0.014 * H), lensMat);
      lens.position.set(side * 0.024 * H, 0, 0.0018 * H);
      glassGroup.add(lens);

      const temple = new THREE.Mesh(new THREE.BoxGeometry(0.002 * H, 0.003 * H, 0.062 * H), frameMat);
      temple.position.set(side * 0.038 * H, 0.004 * H, -0.031 * H);
      glassGroup.add(temple);
    }});

    const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.012 * H, 0.0025 * H, 0.003 * H), frameMat);
    bridge.position.set(0, 0.004 * H, 0);
    glassGroup.add(bridge);

    headGroup.add(glassGroup);
  }} else if(state.glasses === 'round'){{
    const glassGroup = new THREE.Group();
    glassGroup.position.set(0, -0.003 * H, 0.056 * H);
    const metalMat = new THREE.MeshStandardMaterial({{color: 0xd4af37, roughness: 0.25, metalness: 0.85}});
    const clearLensMat = new THREE.MeshStandardMaterial({{color: 0xebf2fa, roughness: 0.05, transparent: true, opacity: 0.35, depthWrite: false}});

    [-1, 1].forEach(side => {{
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.011 * H, 0.0014 * H, 16, 32), metalMat);
      ring.position.x = side * 0.024 * H;
      glassGroup.add(ring);

      const lens = new THREE.Mesh(new THREE.CircleGeometry(0.010 * H, 24), clearLensMat);
      lens.position.set(side * 0.024 * H, 0, 0.0005 * H);
      glassGroup.add(lens);

      const temple = new THREE.Mesh(new THREE.CylinderGeometry(0.0008 * H, 0.0008 * H, 0.062 * H, 12), metalMat);
      temple.rotation.x = Math.PI / 2;
      temple.position.set(side * 0.035 * H, 0.002 * H, -0.031 * H);
      glassGroup.add(temple);
    }});

    const bridge = new THREE.Mesh(new THREE.TorusGeometry(0.006 * H, 0.0012 * H, 12, 16, Math.PI), metalMat);
    bridge.position.set(0, 0.004 * H, 0);
    glassGroup.add(bridge);

    headGroup.add(glassGroup);
  }}

  // 9. Hair Styles
  const hairGroup = new THREE.Group();
  if(state.hairStyle === 'undercut'){{
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.064 * H, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.46), hairMat);
    cap.scale.set(0.88, 1.05, 0.97); cap.position.set(0, 0.009 * H, -0.005 * H);
    hairGroup.add(cap);

    const topVol = new THREE.Mesh(new THREE.SphereGeometry(0.048 * H, 24, 20), hairMat);
    topVol.scale.set(0.85, 0.58, 1.25);
    topVol.rotation.set(-0.25, 0.18, -0.15);
    topVol.position.set(0.006 * H, 0.052 * H, 0.008 * H);
    hairGroup.add(topVol);

    [-1, 1].forEach(side => {{
      const sideBurn = new THREE.Mesh(new THREE.BoxGeometry(0.005 * H, 0.024 * H, 0.012 * H), hairMat);
      sideBurn.position.set(side * 0.052 * H, 0.005 * H, 0.012 * H);
      hairGroup.add(sideBurn);
    }});
  }} else if(state.hairStyle === 'curtain'){{
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.065 * H, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.52), hairMat);
    cap.scale.set(0.89, 1.06, 0.98); cap.position.set(0, 0.009 * H, -0.006 * H);
    hairGroup.add(cap);

    [-1, 1].forEach(side => {{
      const wave = new THREE.Mesh(new THREE.CylinderGeometry(0.012 * H, 0.004 * H, 0.042 * H, 16), hairMat);
      wave.rotation.set(0.45, 0, side * 0.65);
      wave.position.set(side * 0.022 * H, 0.038 * H, 0.046 * H);
      hairGroup.add(wave);

      const fringe = new THREE.Mesh(new THREE.SphereGeometry(0.028 * H, 20, 16), hairMat);
      fringe.scale.set(1.0, 0.65, 1.2);
      fringe.position.set(side * 0.032 * H, 0.048 * H, 0.020 * H);
      hairGroup.add(fringe);
    }});
  }} else if(state.hairStyle === 'crop'){{
    const cropBase = new THREE.Mesh(new THREE.SphereGeometry(0.065 * H, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.44), hairMat);
    cropBase.scale.set(0.89, 1.06, 0.98);
    cropBase.position.set(0, 0.009 * H, -0.005 * H);
    hairGroup.add(cropBase);

    for(let i = 0; i < 7; i++){{
      const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.012 * H, 0.028 * H, 12), hairMat);
      const ang = (i - 3) * 0.28;
      tuft.rotation.set(-0.35 + Math.sin(i) * 0.2, ang * 0.4, -ang);
      tuft.position.set(Math.sin(ang) * 0.026 * H, 0.062 * H, 0.018 * H - Math.abs(ang) * 0.01 * H);
      hairGroup.add(tuft);
    }}
  }} else if(state.hairStyle === 'wavy'){{
    const wavyBase = new THREE.Mesh(new THREE.SphereGeometry(0.067 * H, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.65), hairMat);
    wavyBase.scale.set(0.92, 1.15, 1.05);
    wavyBase.position.set(0, 0.006 * H, -0.010 * H);
    hairGroup.add(wavyBase);

    [-1, 1].forEach(side => {{
      const strand = new THREE.Mesh(new THREE.CylinderGeometry(0.014 * H, 0.008 * H, 0.075 * H, 16), hairMat);
      strand.rotation.set(0.15, 0, side * 0.18);
      strand.position.set(side * 0.048 * H, -0.025 * H, -0.015 * H);
      hairGroup.add(strand);
    }});
  }} else if(state.hairStyle === 'buzz'){{
    const buzzCap = new THREE.Mesh(new THREE.SphereGeometry(0.064 * H, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.48), hairMat);
    buzzCap.scale.set(0.88, 1.05, 0.98);
    buzzCap.position.set(0, 0.008 * H, -0.005 * H);
    hairGroup.add(buzzCap);
  }}
  headGroup.add(hairGroup);

  headGroup.traverse(o => {{
    if(o.isMesh){{
      o.castShadow = true;
      o.receiveShadow = true;
    }}
  }});
}}

/* ---------- Persistent 3D Mesh References ---------- */
let torsoSkinMesh, leftLegSkinMesh, rightLegSkinMesh;
let leftShoeGroup, rightShoeGroup, underwearMesh;
let neckMesh, headGroup;
let leftArmSkinGroup, rightArmSkinGroup;

let topTorsoMesh, topCollarMesh, topHemMesh;
let leftSleeveGroup, rightSleeveGroup;
let leftSleeveTube, leftSleeveCap, leftSleeveCuff;
let rightSleeveTube, rightSleeveCap, rightSleeveCuff;

let botWaistMesh, botWaistRimMesh;
let botLeftLegMesh, botRightLegMesh;
let botLeftCuffMesh, botRightCuffMesh;

function clearGroup(g){{
  while(g.children.length){{
    const o = g.children.pop();
    o.traverse(n => {{
      if(n.geometry) n.geometry.dispose();
    }});
  }}
}}

/* ---------- Full Geometries Builder ---------- */
function buildAllGeometries(){{
  clearGroup(mannequinGroup);
  clearGroup(topGroup);
  clearGroup(botGroup);

  const {{H, W, C, P, B}} = state;
  const isFemale = state.gender === 'female';
  SX = isFemale ? 1.10 : 1.18;
  SZ = isFemale ? 0.88 : 0.82;

  const safeH = Math.max(0.1, H);
  const hip = Math.max(C, P + (H > 0 || C > 0 || P > 0 ? (isFemale ? 22 : 18) : 0));
  const bmi = safeH > 0 ? W / Math.pow(safeH / 100, 2) : 22;
  const armR = Math.min(6, Math.max(0.1, (isFemale ? 3.6 : 4.2) + (isNaN(bmi) ? 0 : (bmi - 22) * 0.15)));
  const chestR = rad(C), waistR = rad(P), hipR = rad(hip);
  const shR = Math.max(0.1, (B / 2 - armR * 0.9) / SX);
  const neckR = Math.max(0.1, H * (isFemale ? 0.024 : 0.026));
  const yCr = 0.47 * H, yHip = 0.52 * H, ySh = 0.80 * H, yNk = 0.84 * H;
  const e = 0.85; // Ketebalan kain pakaian di atas kulit manekin (8.5 mm)

  const skinMat = getMannequinMaterial();
  const curTopMat = topMaterials[state.top] || topMaterials[0];
  const curBotMat = botMaterials[state.bot] || botMaterials[0];

  // 1. Tubuh Karakter (Torso)
  const rows = [
    [0.47, hipR * 0.88, 0],
    [0.52, hipR, 0.97],
    [0.56, hipR * 0.93, 0.97],
    [0.62, waistR, 0.96],
    [0.67, waistR + (chestR - waistR) * 0.72, 0.98],
    [0.72, chestR, 1.0],
    [0.76, chestR * 0.94, 0.93],
    [0.795, shR * 0.96, 0.4],
    [0.812, shR, 0],
    [0.828, shR * 0.52 + neckR * 0.48, 0],
    [0.838, neckR * 1.15, 0],
    [0.852, neckR, 0]
  ];
  torsoSkinMesh = createLatheMesh(rows.map(r => [r[1], r[0] * H]), skinMat, SX, SZ);
  mannequinGroup.add(torsoSkinMesh);

  // Celana Dalam / Fitted Compression Briefs
  underwearMesh = createLatheMesh([
    [hipR * 0.90 + 0.15, yCr - 0.015 * H],
    [hipR + 0.15, yHip],
    [hipR * 0.94 + 0.15, 0.56 * H]
  ], charUnderwearMat, SX, SZ);
  mannequinGroup.add(underwearMesh);

  // 2. Kaki & Sepatu Karakter
  const legTop = hipR * 0.62, ankle = Math.max(2.8, legTop * 0.34), lx = hipR * SX * 0.5;
  const legPts = add => [
    [legTop + add, yCr + 0.015 * H],
    [legTop * 0.93 + add, 0.38 * H],
    [legTop * 0.64 + add, 0.285 * H],
    [legTop * 0.68 + add, 0.20 * H],
    [legTop * 0.45 + add, 0.12 * H],
    [ankle + add, 0.045 * H],
    [ankle * 0.95 + add, 0.03 * H]
  ];

  leftLegSkinMesh = createLatheMesh(legPts(0), skinMat);
  leftLegSkinMesh.position.x = -lx;
  mannequinGroup.add(leftLegSkinMesh);

  rightLegSkinMesh = createLatheMesh(legPts(0), skinMat);
  rightLegSkinMesh.position.x = lx;
  mannequinGroup.add(rightLegSkinMesh);

  // Sepatu Karakter (Footwear)
  leftShoeGroup = createCharacterShoe(-1, lx, ankle, H, state);
  rightShoeGroup = createCharacterShoe(1, lx, ankle, H, state);
  mannequinGroup.add(leftShoeGroup);
  mannequinGroup.add(rightShoeGroup);

  // 3. Leher & Kepala Karakter Game
  neckMesh = createCylMesh(neckR, neckR * 1.05, yNk - 0.01 * H, yNk + 0.045 * H, 0, skinMat);
  mannequinGroup.add(neckMesh);

  headGroup = new THREE.Group();
  headGroup.position.set(0, 0.93 * H, 0.005 * H);
  buildCharacterHead(headGroup, skinMat, charHairMat, charEyebrowMat, state);
  mannequinGroup.add(headGroup);

  // 4. Lengan & Tangan Karakter Game (Anatomi Jari Rileks)
  function createArm(side){{
    const g = new THREE.Group();
    g.position.set(side * B / 2, ySh, 0);
    g.rotation.z = side * 0.09;

    const armSkin = createLatheMesh([
      [armR * 0.98, -0.012 * H], [armR, -0.06 * H], [armR * 0.86, -0.15 * H],
      [armR * 0.78, -0.18 * H], [armR * 0.8, -0.215 * H], [armR * 0.56, -0.29 * H],
      [armR * 0.5, -0.31 * H]
    ], skinMat);
    g.add(armSkin);

    const shJoint = new THREE.Mesh(new THREE.SphereGeometry(armR, 36, 24), skinMat);
    shJoint.position.y = -0.012 * H;
    shJoint.castShadow = true; shJoint.receiveShadow = true;
    g.add(shJoint);

    const hand = createCharacterHand(side, armR, H, skinMat);
    g.add(hand);

    return g;
  }}
  leftArmSkinGroup = createArm(-1);
  rightArmSkinGroup = createArm(1);
  mannequinGroup.add(leftArmSkinGroup);
  mannequinGroup.add(rightArmSkinGroup);

  // 4. Pakaian Atasan (Top Group)
  const sizeC = TOP_SIZES[state.topSize], sizeR = rad(sizeC), dTop = sizeC - C;
  const topStatus = fitStatus(dTop, 2, 14);
  document.getElementById('fitTop').textContent = `${{topStatus.label}} (${{dTop > 0 ? '+' : ''}}${{dTop}} cm)`;
  document.getElementById('dotTop').className = `chip-status ${{topStatus.class}}`;

  const gp = rows.slice(1, 10).map(r => [r[2] ? Math.max(r[1] + e, sizeR * r[2]) : r[1] + e + 0.4, r[0] * H]);
  gp.push([neckR + 1.6, 0.836 * H]);
  topTorsoMesh = createLatheMesh(gp, curTopMat.torso, SX, SZ);
  topGroup.add(topTorsoMesh);

  topCollarMesh = createTorusRing(neckR + 1.8, 0.55, 0.838 * H, curTopMat.sleeve, SX * 1.02, SZ * 1.02);
  topGroup.add(topCollarMesh);

  const hemR = rows[1][1] + e + 0.4;
  topHemMesh = createTorusRing(hemR, 0.45, rows[1][0] * H, curTopMat.sleeve, SX, SZ);
  topGroup.add(topHemMesh);

  const sl = Math.max(armR * 1.08 + e, armR + (sizeC - C) * 0.05);

  function createSleeve(side){{
    const g = new THREE.Group();
    g.position.set(side * B / 2, ySh, 0);
    g.rotation.z = side * 0.09;

    const tube = new THREE.Mesh(new THREE.CylinderGeometry(sl, sl * 0.93, Math.max(0.001, 0.138 * H), 64, 1, true), curTopMat.sleeve);
    tube.position.y = -0.081 * H;
    tube.castShadow = true; tube.receiveShadow = true;
    g.add(tube);

    const cap = new THREE.Mesh(new THREE.SphereGeometry(sl, 36, 24), curTopMat.sleeve);
    cap.position.y = -0.012 * H;
    cap.scale.y = 0.9;
    cap.castShadow = true; cap.receiveShadow = true;
    g.add(cap);

    const cuff = createTorusRing(sl * 0.93, 0.45, -0.15 * H, curTopMat.sleeve);
    g.add(cuff);

    return {{group: g, tube, cap, cuff}};
  }}

  const lSl = createSleeve(-1);
  leftSleeveGroup = lSl.group; leftSleeveTube = lSl.tube; leftSleeveCap = lSl.cap; leftSleeveCuff = lSl.cuff;
  topGroup.add(leftSleeveGroup);

  const rSl = createSleeve(1);
  rightSleeveGroup = rSl.group; rightSleeveTube = rSl.tube; rightSleeveCap = rSl.cap; rightSleeveCuff = rSl.cuff;
  topGroup.add(rightSleeveGroup);

  topGroup.visible = state.topOn;

  // 5. Pakaian Celana (Bot Group)
  const sizeP = BOT_SIZES[state.botSize], dBot = sizeP - P;
  const botStatus = fitStatus(dBot, 1, 12);
  document.getElementById('fitBot').textContent = `${{botStatus.label}} (${{dBot > 0 ? '+' : ''}}${{dBot}} cm)`;
  document.getElementById('dotBot').className = `chip-status ${{botStatus.class}}`;

  const loose = Math.max(0, sizeP - P) * 0.035;
  const wR = Math.max(waistR + e, rad(sizeP));

  // Points go from bottom (crotch yCr) to top (waist 0.64*H) so UV v goes smoothly from bottom to top
  botWaistMesh = createLatheMesh([
    [hipR * 0.9 + e, yCr],
    [Math.max(hipR + e, wR * 1.04), yHip],
    [Math.max(hipR * 0.93 + e, (wR + hipR) / 2), 0.56 * H],
    [wR, 0.64 * H]
  ], curBotMat.waist, SX, SZ);
  botGroup.add(botWaistMesh);

  botWaistRimMesh = createTorusRing(wR + 0.4, 0.5, 0.64 * H, curBotMat.waist, SX, SZ);
  botGroup.add(botWaistRimMesh);

  botLeftLegMesh = createLatheMesh(legPts(e + loose).slice(0, 6), curBotMat.leg);
  botLeftLegMesh.position.x = -lx;
  botGroup.add(botLeftLegMesh);

  botRightLegMesh = createLatheMesh(legPts(e + loose).slice(0, 6), curBotMat.leg);
  botRightLegMesh.position.x = lx;
  botGroup.add(botRightLegMesh);

  const cuffR = ankle + e + loose;
  botLeftCuffMesh = createTorusRing(cuffR + 0.3, 0.45, 0.045 * H, curBotMat.leg);
  botLeftCuffMesh.position.x = -lx;
  botGroup.add(botLeftCuffMesh);

  botRightCuffMesh = createTorusRing(cuffR + 0.3, 0.45, 0.045 * H, curBotMat.leg);
  botRightCuffMesh.position.x = lx;
  botGroup.add(botRightCuffMesh);

  botGroup.visible = state.botOn;
}}

/* Smooth Micro-Transition when clothing changes (Lembut & Taktil) */
function triggerSmoothTransition(group){{
  if(!group) return;
  const startScale = 0.985;
  const startTime = performance.now();
  const duration = 240;
  function step(now){{
    const elapsed = now - startTime;
    const p = Math.min(1, elapsed / duration);
    // Smooth easeOutCubic
    const ease = 1 - Math.pow(1 - p, 3);
    const sc = startScale + (1 - startScale) * ease;
    group.scale.set(sc, sc, sc);
    if(p < 1){{
      requestAnimationFrame(step);
    }} else {{
      group.scale.set(1, 1, 1);
    }}
  }}
  requestAnimationFrame(step);
}}

/* ---------- Instant Material Swapping ---------- */
function switchTopProduct(idx){{
  state.top = idx;
  const mats = topMaterials[idx];
  if(!mats) return;

  if(topTorsoMesh){{
    topTorsoMesh.material = mats.torso;
    topTorsoMesh.material.needsUpdate = true;
    if(topTorsoMesh.material.map) topTorsoMesh.material.map.needsUpdate = true;
  }}
  if(topCollarMesh){{
    topCollarMesh.material = mats.sleeve;
    topCollarMesh.material.needsUpdate = true;
  }}
  if(topHemMesh){{
    topHemMesh.material = mats.sleeve;
    topHemMesh.material.needsUpdate = true;
  }}

  const sleeveMeshes = [leftSleeveTube, leftSleeveCap, leftSleeveCuff, rightSleeveTube, rightSleeveCap, rightSleeveCuff];
  sleeveMeshes.forEach(m => {{
    if(m){{
      m.material = mats.sleeve;
      m.material.needsUpdate = true;
      if(m.material.map) m.material.map.needsUpdate = true;
    }}
  }});

  activeCustomTex = mats.mainTex || (mats.torso ? mats.torso.map : null);
  triggerSmoothTransition(topGroup);
  updateDesc('top');
  renderer.render(scene, camera);
}}

function switchBottomProduct(idx){{
  state.bot = idx;
  const mats = botMaterials[idx];
  if(!mats) return;

  if(botWaistMesh){{
    botWaistMesh.material = mats.waist;
    botWaistMesh.material.needsUpdate = true;
    if(botWaistMesh.material.map) botWaistMesh.material.map.needsUpdate = true;
  }}
  if(botWaistRimMesh){{
    botWaistRimMesh.material = mats.waist;
    botWaistRimMesh.material.needsUpdate = true;
  }}

  const legMeshes = [botLeftLegMesh, botRightLegMesh, botLeftCuffMesh, botRightCuffMesh];
  legMeshes.forEach(m => {{
    if(m){{
      m.material = mats.leg;
      m.material.needsUpdate = true;
      if(m.material.map) m.material.map.needsUpdate = true;
    }}
  }});

  activeCustomTex = mats.mainTex || (mats.waist ? mats.waist.map : null);
  triggerSmoothTransition(botGroup);
  updateDesc('bot');
  renderer.render(scene, camera);
}}

function updateWrinklesToggling(){{
  const scale = state.wrinkles ? 0.95 : 0.001;
  topMaterials.forEach(m => {{
    if(m.torso.normalScale) m.torso.normalScale.set(scale, scale);
    if(m.sleeve.normalScale) m.sleeve.normalScale.set(scale, scale);
    m.torso.needsUpdate = true;
    m.sleeve.needsUpdate = true;
  }});
  botMaterials.forEach(m => {{
    if(m.waist.normalScale) m.waist.normalScale.set(scale, scale);
    if(m.leg.normalScale) m.leg.normalScale.set(scale, scale);
    m.waist.needsUpdate = true;
    m.leg.needsUpdate = true;
  }});
  renderer.render(scene, camera);
}}

/* ---------- UI Controller & Event Handlers ---------- */
const sliders = {{H: 'H', W: 'W', C: 'C', P: 'P', B: 'B'}};
const unit = {{H: ' cm', W: ' kg', C: ' cm', P: ' cm', B: ' cm'}};

function syncOut(id){{
  const el = document.getElementById(id);
  el.nextElementSibling.textContent = el.value + unit[id];
}}

function calcEstimatedBody(hVal, wVal){{
  if(hVal <= 0 || wVal <= 0){{
    return {{C: 0, P: 0, B: 0}};
  }}
  const idealW = 22 * Math.pow(hVal / 100, 2);
  const deltaW = wVal - idealW;
  const C = Math.max(0, Math.round(hVal * 0.535 + deltaW * 0.75));
  const P = Math.max(0, Math.round(hVal * 0.44 + deltaW * 0.85));
  const B = Math.max(0, Math.round(hVal * 0.246 + deltaW * 0.08));
  return {{C, P, B}};
}}

function setSlider(id, v){{
  const el = document.getElementById(id);
  el.value = Math.round(v);
  state[id] = +el.value;
  syncOut(id);
}}

function applyEstimation(buildGeo = true){{
  const est = calcEstimatedBody(state.H, state.W);
  setSlider('C', est.C);
  setSlider('P', est.P);
  setSlider('B', est.B);
  if(buildGeo) buildAllGeometries();
}}

const autoSyncCheckbox = document.getElementById('autoSyncBody');

/* Throttled 60fps Geometry Builder (Bebas Lag & Stutter saat geser slider) */
let buildGeoPending = false;
function requestBuildGeometries(){{
  if(buildGeoPending) return;
  buildGeoPending = true;
  requestAnimationFrame(() => {{
    buildGeoPending = false;
    buildAllGeometries();
  }});
}}

Object.keys(sliders).forEach(id => {{
  const el = document.getElementById(id);
  syncOut(id);
  el.addEventListener('input', () => {{
    state[id] = +el.value;
    syncOut(id);
    if((id === 'H' || id === 'W') && autoSyncCheckbox && autoSyncCheckbox.checked){{
      applyEstimation(false);
    }} else if(id === 'C' || id === 'P' || id === 'B'){{
      if(autoSyncCheckbox) autoSyncCheckbox.checked = false;
    }}
    requestBuildGeometries();
  }});
}});

document.getElementById('est').addEventListener('click', () => {{
  if(autoSyncCheckbox) autoSyncCheckbox.checked = true;
  applyEstimation(true);
}});

function fillSizes(id, obj, key){{
  const s = document.getElementById(id);
  Object.keys(obj).forEach(k => {{
    const o = document.createElement('option');
    o.value = o.textContent = k;
    s.appendChild(o);
  }});
  s.value = state[key];
  s.addEventListener('change', () => {{
    state[key] = s.value;
    buildAllGeometries();
  }});
}}
fillSizes('topSize', TOP_SIZES, 'topSize');
fillSizes('botSize', BOT_SIZES, 'botSize');

function updateDesc(kind){{
  if(kind === 'top'){{
    const p = catalog.tops[state.top];
    if(p) document.getElementById('topDesc').innerHTML = `<b>${{p.name}}</b> (${{p.price}})<br>${{p.desc}}`;
  }} else {{
    const p = catalog.bottoms[state.bot];
    if(p) document.getElementById('botDesc').innerHTML = `<b>${{p.name}}</b> (${{p.price}})<br>${{p.desc}}`;
  }}
}}

function fillProds(boxId, kind, list){{
  const box = document.getElementById(boxId);
  box.innerHTML = '';
  list.forEach((p, i) => {{
    const card = document.createElement('div');
    card.className = 'prod-card' + (i === state[kind] ? ' on' : '');
    const thumbSrc = p.thumb_b64 || p.thumb_url;
    card.innerHTML = `
      <div class="img-box"><img src="${{thumbSrc}}" alt="${{p.name}}"></div>
      <div class="p-name">${{p.name}}</div>
      <div class="p-price">${{p.price}}</div>
    `;
    card.onclick = function(e){{
      e.preventDefault();
      [...box.children].forEach(c => c.classList.remove('on'));
      card.classList.add('on');
      if(kind === 'top'){{
        switchTopProduct(i);
      }} else {{
        switchBottomProduct(i);
      }}
    }};
    box.appendChild(card);
  }});
  updateDesc(kind);
}}

fillProds('topProds', 'top', catalog.tops);
fillProds('botProds', 'bot', catalog.bottoms);

// Studio background presets
const BG_PRESETS = {{
  neutral: 'radial-gradient(circle at 50% 38%, #F2F4F8 0%, #DFE4EC 55%, #C2C9D6 100%)',
  minimal: 'radial-gradient(circle at 50% 38%, #FFFFFF 0%, #E8EDF5 55%, #CCD5E2 100%)',
  dark: 'radial-gradient(circle at 50% 38%, #28252d 0%, #17151b 60%, #0c0b0e 100%)'
}};

function setBgPreset(val){{
  state.bg = val;
  const bgVal = BG_PRESETS[val] || BG_PRESETS.neutral;
  stage.style.background = bgVal;
  document.querySelectorAll('#bgPreset button').forEach(b => {{
    b.classList.toggle('on', b.dataset.val === val);
  }});
  const hintEl = document.querySelector('.hint');
  if(hintEl){{
    if(val === 'dark'){{
      hintEl.style.color = '#fff';
      hintEl.style.background = 'rgba(30, 27, 34, 0.84)';
    }} else {{
      hintEl.style.color = 'var(--mut)';
      hintEl.style.background = 'rgba(255, 255, 255, 0.84)';
    }}
  }}
}}

document.querySelectorAll('#bgPreset button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    setBgPreset(btn.dataset.val);
  }});
}});

// Lighting presets
document.querySelectorAll('#lightPreset button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#lightPreset button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    setLightingPreset(btn.dataset.val);
  }});
}});

// Populate Avatar Skin Tone Swatches
const skinBox = document.getElementById('skinTonePicker');
if(skinBox){{
  Object.keys(SKIN_TONES).forEach(k => {{
    const item = SKIN_TONES[k];
    const dot = document.createElement('div');
    dot.className = `color-dot ${{state.skinTone === k ? 'on' : ''}}`;
    dot.style.background = item.css;
    dot.title = item.label;
    dot.addEventListener('click', () => {{
      document.querySelectorAll('#skinTonePicker .color-dot').forEach(d => d.classList.remove('on'));
      dot.classList.add('on');
      state.skinTone = k;
      updateCharacterSkin();
    }});
    skinBox.appendChild(dot);
  }});
}}

// Populate Avatar Hair Color Swatches
const hairBox = document.getElementById('hairColorPicker');
if(hairBox){{
  Object.keys(HAIR_COLORS).forEach(k => {{
    const item = HAIR_COLORS[k];
    const dot = document.createElement('div');
    dot.className = `color-dot ${{state.hairColor === k ? 'on' : ''}}`;
    dot.style.background = item.css;
    dot.title = item.label;
    dot.addEventListener('click', () => {{
      document.querySelectorAll('#hairColorPicker .color-dot').forEach(d => d.classList.remove('on'));
      dot.classList.add('on');
      state.hairColor = k;
      updateCharacterHair();
    }});
    hairBox.appendChild(dot);
  }});
}}

// Character Avatar: Gender
document.querySelectorAll('#charGender button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#charGender button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    state.gender = btn.dataset.val;
    if(state.gender === 'female'){{
      if(state.hairStyle === 'undercut') state.hairStyle = 'curtain';
      state.beard = 'clean';
      document.querySelectorAll('#charBeard button').forEach(b => b.classList.toggle('on', b.dataset.val === 'clean'));
      const hs = document.getElementById('hairStyleSelect');
      if(hs) hs.value = state.hairStyle;
    }}
    buildAllGeometries();
    renderer.render(scene, camera);
  }});
}});

// Character Avatar: Hairstyle
const hsEl = document.getElementById('hairStyleSelect');
if(hsEl){{
  hsEl.addEventListener('change', e => {{
    state.hairStyle = e.target.value;
    buildAllGeometries();
    renderer.render(scene, camera);
  }});
}}

// Character Avatar: Beard
document.querySelectorAll('#charBeard button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#charBeard button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    state.beard = btn.dataset.val;
    buildAllGeometries();
    renderer.render(scene, camera);
  }});
}});

// Character Avatar: Glasses
document.querySelectorAll('#charGlasses button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#charGlasses button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    state.glasses = btn.dataset.val;
    buildAllGeometries();
    renderer.render(scene, camera);
  }});
}});

// Character Avatar: Shoes
document.querySelectorAll('#charShoes button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#charShoes button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    state.shoes = btn.dataset.val;
    buildAllGeometries();
    renderer.render(scene, camera);
  }});
}});

document.getElementById('wrinklesOn').addEventListener('change', e => {{
  state.wrinkles = e.target.checked;
  updateWrinklesToggling();
}});

// Checkboxes: Toggle visibility
document.getElementById('topOn').addEventListener('change', e => {{
  state.topOn = e.target.checked;
  topGroup.visible = state.topOn;
  const dTop = TOP_SIZES[state.topSize] - state.C;
  const topStatus = fitStatus(dTop, 2, 14);
  document.getElementById('fitTop').textContent = state.topOn ? `${{topStatus.label}} (${{dTop > 0 ? '+' : ''}}${{dTop}} cm)` : "-";
  document.getElementById('dotTop').className = `chip-status ${{state.topOn ? topStatus.class : ''}}`;
}});

document.getElementById('botOn').addEventListener('change', e => {{
  state.botOn = e.target.checked;
  botGroup.visible = state.botOn;
  const dBot = BOT_SIZES[state.botSize] - state.P;
  const botStatus = fitStatus(dBot, 1, 12);
  document.getElementById('fitBot').textContent = state.botOn ? `${{botStatus.label}} (${{dBot > 0 ? '+' : ''}}${{dBot}} cm)` : "-";
  document.getElementById('dotBot').className = `chip-status ${{state.botOn ? botStatus.class : ''}}`;
}});

const spin = document.getElementById('spin');
const stageSpinBtn = document.getElementById('stageSpinBtn');

function toggleAutoSpin(){{
  controls.autoRotate = !controls.autoRotate;
  if(spin) spin.classList.toggle('on', controls.autoRotate);
  if(stageSpinBtn) stageSpinBtn.classList.toggle('on', controls.autoRotate);
}}

spin.addEventListener('click', toggleAutoSpin);
if(stageSpinBtn) stageSpinBtn.addEventListener('click', toggleAutoSpin);

document.getElementById('reset').addEventListener('click', () => resetCam(true));

// Camera Quick-View Pills
document.querySelectorAll('#camPills .cam-pill[data-angle]').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#camPills .cam-pill[data-angle]').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    setCameraAngle(btn.dataset.angle);
  }});
}});

/* ---------- FITUR INPUT / UNGGAH FOTO PAKAIAN SENDIRI ---------- */
let activeCustomTex = topMaterials[0].mainTex;

const uploadZone = document.getElementById('uploadZone');
const customFileInput = document.getElementById('customFileInput');
const tuneBox = document.getElementById('tuneBox');
const tuneX = document.getElementById('tuneX');
const tuneY = document.getElementById('tuneY');
const tuneScale = document.getElementById('tuneScale');
const tuneXOut = document.getElementById('tuneXOut');
const tuneYOut = document.getElementById('tuneYOut');
const tuneScaleOut = document.getElementById('tuneScaleOut');

document.querySelectorAll('#customCategory button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#customCategory button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    state.customCat = btn.dataset.val;
  }});
}});

uploadZone.addEventListener('click', () => customFileInput.click());
uploadZone.addEventListener('dragover', e => {{ e.preventDefault(); uploadZone.style.borderColor = 'var(--brand)'; }});
uploadZone.addEventListener('dragleave', e => {{ e.preventDefault(); uploadZone.style.borderColor = 'var(--line)'; }});
uploadZone.addEventListener('drop', e => {{
  e.preventDefault();
  uploadZone.style.borderColor = 'var(--line)';
  if(e.dataTransfer.files && e.dataTransfer.files[0]){{
    processUploadedFile(e.dataTransfer.files[0], state.customCat);
  }}
}});

customFileInput.addEventListener('change', e => {{
  if(e.target.files && e.target.files[0]){{
    processUploadedFile(e.target.files[0], state.customCat);
  }}
}});

function processUploadedFile(file, category){{
  const reader = new FileReader();
  reader.onload = function(evt){{
    const img = new Image();
    img.onload = function(){{
      // 1. Offscreen analysis untuk segmentasi background & pencarian titik tengah
      const tempC = document.createElement('canvas');
      const w = img.naturalWidth || img.width;
      const h = img.naturalHeight || img.height;
      tempC.width = w;
      tempC.height = h;
      const tCtx = tempC.getContext('2d');
      tCtx.drawImage(img, 0, 0);
      const imgData = tCtx.getImageData(0, 0, w, h);
      const d = imgData.data;

      // Sample warna background dari 4 pojok
      const sample = (x, y) => {{
        const i = (y * w + x) * 4;
        return [d[i], d[i+1], d[i+2]];
      }};
      const c = [sample(4,4), sample(w-5,4), sample(4,h-5), sample(w-5,h-5)];
      const bgR = (c[0][0]+c[1][0]+c[2][0]+c[3][0])/4;
      const bgG = (c[0][1]+c[1][1]+c[2][1]+c[3][1])/4;
      const bgB = (c[0][2]+c[1][2]+c[2][2]+c[3][2])/4;

      // Temukan bounding box pakaian
      let minX = w, maxX = 0, minY = h, maxY = 0;
      let fabricR = 0, fabricG = 0, fabricB = 0, fabricCount = 0;
      for(let y = 0; y < h; y += 4){{
        for(let x = 0; x < w; x += 4){{
          const i = (y * w + x) * 4;
          const dist = Math.max(Math.abs(d[i]-bgR), Math.abs(d[i+1]-bgG), Math.abs(d[i+2]-bgB));
          if(dist > 22){{
            if(x < minX) minX = x;
            if(x > maxX) maxX = x;
            if(y < minY) minY = y;
            if(y > maxY) maxY = y;
            if(y > h * 0.35 && y < h * 0.65 && x > w * 0.35 && x < w * 0.65){{
              fabricR += d[i]; fabricG += d[i+1]; fabricB += d[i+2];
              fabricCount++;
            }}
          }}
        }}
      }}

      if(fabricCount > 0){{
        fabricR = Math.round(fabricR / fabricCount);
        fabricG = Math.round(fabricG / fabricCount);
        fabricB = Math.round(fabricB / fabricCount);
      }} else {{
        fabricR = 245; fabricG = 245; fabricB = 245;
      }}

      // 2. Buat kanvas tekstur torso/waist 512x512
      const canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 512;
      const ctx = canvas.getContext('2d');

      // Warna dasar kain bersih tanpa garis batas
      ctx.fillStyle = `rgb(${{fabricR}}, ${{fabricG}}, ${{fabricB}})`;
      ctx.fillRect(0, 0, 512, 512);

      // Potong bagian baju dan buang background putih
      const gw = Math.max(10, maxX - minX);
      const gh = Math.max(10, maxY - minY);
      const fgC = document.createElement('canvas');
      fgC.width = gw;
      fgC.height = gh;
      const fgCtx = fgC.getContext('2d');
      const fgData = tCtx.getImageData(minX, minY, gw, gh);
      const fgD = fgData.data;

      // Alpha feathering pada background
      for(let i = 0; i < fgD.length; i += 4){{
        const dist = Math.max(Math.abs(fgD[i]-bgR), Math.abs(fgD[i+1]-bgG), Math.abs(fgD[i+2]-bgB));
        if(dist < 18){{
          fgD[i+3] = 0;
        }} else if(dist < 38){{
          fgD[i+3] = Math.round(((dist - 18) / 20) * 255);
        }}
      }}
      fgCtx.putImageData(fgData, 0, 0);

      // Posisikan lurus sempurna di tengah X=256
      const maxW = category === 'top' ? 290 : 320;
      const maxH = category === 'top' ? 360 : 360;
      const scaleFactor = Math.min(maxW / gw, maxH / gh, 1.2);
      const targetW = Math.round(gw * scaleFactor);
      const targetH = Math.round(gh * scaleFactor);
      const targetX = Math.round((512 - targetW) / 2); // Tepat lurus di tengah (X=256)
      const targetY = category === 'top' ? 45 : 20;

      ctx.drawImage(fgC, targetX, targetY, targetW, targetH);

      // Buat kain sleeve/leg yang matching
      const subCanvas = document.createElement('canvas');
      subCanvas.width = 512;
      subCanvas.height = 512;
      const subCtx = subCanvas.getContext('2d');
      subCtx.fillStyle = `rgb(${{fabricR}}, ${{fabricG}}, ${{fabricB}})`;
      subCtx.fillRect(0, 0, 512, 512);

      // Buat material Three.js
      const mainTex = new THREE.CanvasTexture(canvas);
      mainTex.encoding = THREE.sRGBEncoding;
      mainTex.generateMipmaps = true;
      mainTex.minFilter = THREE.LinearMipmapLinearFilter;
      mainTex.magFilter = THREE.LinearFilter;
      if(renderer && renderer.capabilities) mainTex.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 16);
      mainTex.wrapS = THREE.RepeatWrapping;
      mainTex.wrapT = THREE.ClampToEdgeWrapping;
      mainTex.offset.set(0, 0);

      const subTex = new THREE.CanvasTexture(subCanvas);
      subTex.encoding = THREE.sRGBEncoding;
      subTex.generateMipmaps = true;
      subTex.minFilter = THREE.LinearMipmapLinearFilter;
      subTex.magFilter = THREE.LinearFilter;
      if(renderer && renderer.capabilities) subTex.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 16);
      subTex.wrapS = THREE.RepeatWrapping;
      subTex.wrapT = THREE.RepeatWrapping;

      const newTopMat = {{
        torso: new THREE.MeshStandardMaterial({{
          color: 0xffffff,
          map: mainTex,
          normalMap: normalTextures.top_wrinkles || null,
          normalScale: new THREE.Vector2(0.8, 0.8),
          roughness: 0.76,
          metalness: 0.03,
          polygonOffset: true,
          polygonOffsetFactor: -1.0,
          polygonOffsetUnits: -4.0,
          side: THREE.DoubleSide
        }}),
        sleeve: new THREE.MeshStandardMaterial({{
          color: 0xffffff,
          map: subTex,
          roughness: 0.76,
          metalness: 0.03,
          polygonOffset: true,
          polygonOffsetFactor: -1.0,
          polygonOffsetUnits: -4.0,
          side: THREE.DoubleSide
        }}),
        mainTex: mainTex
      }};

      const newBotMat = {{
        waist: new THREE.MeshStandardMaterial({{
          color: 0xffffff,
          map: mainTex,
          normalMap: normalTextures.pants_wrinkles || null,
          normalScale: new THREE.Vector2(0.85, 0.85),
          roughness: 0.80,
          metalness: 0.03,
          polygonOffset: true,
          polygonOffsetFactor: -1.0,
          polygonOffsetUnits: -4.0,
          side: THREE.DoubleSide
        }}),
        leg: new THREE.MeshStandardMaterial({{
          color: 0xffffff,
          map: subTex,
          roughness: 0.80,
          metalness: 0.03,
          polygonOffset: true,
          polygonOffsetFactor: -1.0,
          polygonOffsetUnits: -4.0,
          side: THREE.DoubleSide
        }}),
        mainTex: mainTex
      }};

      const prodName = file.name.replace(/\.[^/.]+$/, "") + " (Kustom)";
      const thumbB64 = canvas.toDataURL('image/jpeg', 0.85);

      if(category === 'top'){{
        topMaterials.push(newTopMat);
        catalog.tops.push({{
          id: 'custom_top_' + Date.now(),
          name: prodName,
          price: "Pilihan Anda",
          desc: "Foto produk pakaian yang diunggah pengguna. Posisi grafis dipasang lurus simetris di tengah dada tanpa garis potongan.",
          thumb_b64: thumbB64
        }});
        fillProds('topProds', 'top', catalog.tops);
        switchTopProduct(topMaterials.length - 1);
        [...document.getElementById('topProds').children].forEach((c, idx) => {{
          c.classList.toggle('on', idx === topMaterials.length - 1);
        }});
      }} else {{
        botMaterials.push(newBotMat);
        catalog.bottoms.push({{
          id: 'custom_bot_' + Date.now(),
          name: prodName,
          price: "Pilihan Anda",
          desc: "Foto produk celana yang diunggah pengguna. Ban pinggang dipasang lurus simetris di pinggang manekin tanpa garis potongan.",
          thumb_b64: thumbB64
        }});
        fillProds('botProds', 'bot', catalog.bottoms);
        switchBottomProduct(botMaterials.length - 1);
        [...document.getElementById('botProds').children].forEach((c, idx) => {{
          c.classList.toggle('on', idx === botMaterials.length - 1);
        }});
      }}

      activeCustomTex = mainTex;
      tuneBox.style.display = 'block';
      resetTuneSliders();
    }};
    img.src = evt.target.result;
  }};
  reader.readAsDataURL(file);
}}

function resetTuneSliders(){{
  tuneX.value = 0; tuneXOut.textContent = "0%";
  tuneY.value = 0; tuneYOut.textContent = "0%";
  tuneScale.value = 1.0; tuneScaleOut.textContent = "100%";
  applyTune();
}}

function applyTune(){{
  if(!activeCustomTex) return;
  const ox = parseFloat(tuneX.value);
  const oy = parseFloat(tuneY.value);
  const sc = parseFloat(tuneScale.value);

  tuneXOut.textContent = (ox * 100).toFixed(0) + "%";
  tuneYOut.textContent = (oy * 100).toFixed(0) + "%";
  tuneScaleOut.textContent = Math.round(sc * 100) + "%";

  activeCustomTex.offset.set(ox, oy);
  activeCustomTex.repeat.set(1 / sc, 1 / sc);
  activeCustomTex.needsUpdate = true;
  renderer.render(scene, camera);
}}

tuneX.addEventListener('input', applyTune);
tuneY.addEventListener('input', applyTune);
tuneScale.addEventListener('input', applyTune);
document.getElementById('btnResetTune').addEventListener('click', resetTuneSliders);

/* ---------- Eksekusi Awal ---------- */
resize();
buildAllGeometries();
resetCam();

(function loop(){{
  requestAnimationFrame(loop);
  controls.update();
  renderer.render(scene, camera);
}})();

window.__VIEWER__ = {{
  state,
  topGroup,
  botGroup,
  mannequinGroup,
  switchTopProduct,
  switchBottomProduct,
  topMaterials,
  botMaterials
}};
}})();
</script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Selesai! index.html berhasil dikompilasi ({len(html_content)} bytes).")
