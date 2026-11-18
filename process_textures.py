#!/usr/bin/env python3
"""
Memproses foto katalog produk asli menjadi tekstur 3D fotorealistik:
1. Thumbnail UI tajam & bersih (256x256)
2. Tekstur 3D UV untuk torso / pinggang (512x512) dengan:
   - Background putih / foto dihapus bersih (NO white cutout borders)
   - Grafis / kancing / resleting diposisikan lurus sempurna di tengah (Centered at X=256)
   - Blending halus ke kain dasar (Seamless edge feathering)
3. Tekstur 3D UV untuk lengan / kaki (512x512) dari sampel kain asli (bukan celah latar belakang)
4. Export data produk lengkap (dengan data URL base64 agar aman dari CORS saat dibuka via file://)
"""
import os, sys, json, base64
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

PRODUCTS_DIR = 'products'
TEXTURES_DIR = 'textures'
os.makedirs(TEXTURES_DIR, exist_ok=True)

def to_base64(img, fmt='JPEG', quality=90):
    buf = BytesIO()
    img.save(buf, format=fmt, quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    mime = 'image/jpeg' if fmt.upper() in ('JPEG', 'JPG') else 'image/png'
    return f"data:{mime};base64,{b64}"

def make_seamless(img, blend_w=36):
    """Membuat tekstur kain dapat di-tile secara seamless tanpa garis potongan batas."""
    w, h = img.size
    arr = np.array(img, dtype=np.float32)
    res = arr.copy()
    for x in range(blend_w):
        alpha = x / float(blend_w)
        res[:, x] = arr[:, x] * alpha + arr[:, w - blend_w + x] * (1.0 - alpha)
        res[:, w - blend_w + x] = res[:, x]
    for y in range(blend_w):
        alpha = y / float(blend_w)
        res[y, :] = res[y, :] * alpha + res[h - blend_w + y, :] * (1.0 - alpha)
        res[h - blend_w + y, :] = res[y, :]
    return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))

def process_top(filename, name, price, desc, fabric_type="cotton"):
    path = os.path.join(PRODUCTS_DIR, filename)
    img = Image.open(path).convert('RGB')
    w, h = img.size
    arr = np.array(img, dtype=np.float32)

    # 1. Thumbnail UI
    thumb = img.resize((256, 256), Image.Resampling.LANCZOS)
    thumb_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_thumb.jpg")
    thumb.save(thumb_path, quality=90)

    # 2. Pemrosesan Khusus per Jenis Baju agar 100% Lurus & Tanpa Potongan Palsu
    prod_id = filename[:-4]

    if prod_id == "tshirt_graphic_white":
        # Kaos combed putih bersih
        fabric_swatch = Image.new('RGB', (512, 512), (247, 247, 247))
        sleeve = fabric_swatch.copy()
        
        # Ekstrak grafis minimalis geometris (posisi asli X: 415..615, Y: 345..550)
        graphic_crop = img.crop((410, 340, 620, 555))
        gw, gh = graphic_crop.size
        g_arr = np.array(graphic_crop, dtype=np.float32)
        # Pisahkan grafis hitam dari kain putih
        diff = np.max(np.abs(g_arr - [225, 225, 225]), axis=-1)
        alpha = np.clip((diff - 8.0) / 22.0, 0.0, 1.0)
        alpha_img = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))

        # Posisikan simetris lurus di tengah dada (X=256)
        target_w = 210
        target_h = int(target_w * gh / gw)
        g_resized = graphic_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        a_resized = alpha_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        torso = fabric_swatch.copy()
        pos_x = (512 - target_w) // 2  # Tepat di tengah (X=256)
        pos_y = 150                   # Area dada manekin
        torso.paste(g_resized, (pos_x, pos_y), a_resized)

    elif prod_id == "polo_navy":
        # Sampel kain navy pique murni (bebas background putih)
        swatch_crop = img.crop((400, 500, 620, 720)).resize((512, 512), Image.Resampling.LANCZOS)
        fabric_swatch = make_seamless(swatch_crop, blend_w=32)
        sleeve = fabric_swatch.copy()

        # Ekstrak kerah dan plaket kancing polo (X: 380..644, Y: 65..450)
        placket_crop = arr[65:450, 380:644]
        ph, pw, _ = placket_crop.shape

        # Hapus background putih di atas pundak/leher
        dist = np.max(np.abs(placket_crop - [254, 254, 254]), axis=-1)
        alpha = np.clip((dist - 18.0) / 20.0, 0.0, 1.0)

        # Feathering batas luar agar menyatu halus dengan kain
        border_fade = np.ones((ph, pw), dtype=np.float32)
        fade_px = 25
        for y in range(ph):
            if y > ph - fade_px:
                border_fade[y, :] *= (ph - y) / float(fade_px)
        for x in range(pw):
            if x < fade_px:
                border_fade[:, x] *= x / float(fade_px)
            elif x > pw - fade_px:
                border_fade[:, x] *= (pw - x) / float(fade_px)

        combined_alpha = alpha * border_fade
        alpha_img = Image.fromarray((combined_alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0))

        target_w, target_h = 240, 300
        placket_resized = Image.fromarray(placket_crop.astype(np.uint8)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        alpha_resized = alpha_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        torso = fabric_swatch.copy()
        pos_x = (512 - target_w) // 2  # Lurus di tengah dada (X=256)
        pos_y = 10                    # Posisi kerah atas
        torso.paste(placket_resized, (pos_x, pos_y), alpha_resized)

    elif prod_id == "flannel_red":
        # Ambil pola kotak flanel merah-hitam asli dari badan baju (bebas background putih)
        flannel_crop = img.crop((312, 280, 712, 680)).resize((512, 512), Image.Resampling.LANCZOS)
        fabric_swatch = make_seamless(flannel_crop, blend_w=36)
        sleeve = fabric_swatch.copy()
        torso = fabric_swatch.copy()

    else:
        # Kaos basic putih
        fabric_swatch = Image.new('RGB', (512, 512), (248, 248, 248))
        sleeve = fabric_swatch.copy()
        torso = fabric_swatch.copy()

    sleeve_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_sleeve.jpg")
    sleeve.save(sleeve_path, quality=90)

    torso_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_torso.jpg")
    torso.save(torso_path, quality=90)

    return {
        "id": filename[:-4],
        "name": name,
        "price": price,
        "desc": desc,
        "fabric_type": fabric_type,
        "thumb_url": f"textures/{filename[:-4]}_thumb.jpg",
        "torso_url": f"textures/{filename[:-4]}_torso.jpg",
        "sleeve_url": f"textures/{filename[:-4]}_sleeve.jpg",
        "thumb_b64": to_base64(thumb),
        "torso_b64": to_base64(torso),
        "sleeve_b64": to_base64(sleeve)
    }

def process_bottom(filename, name, price, desc, fabric_type="denim"):
    path = os.path.join(PRODUCTS_DIR, filename)
    img = Image.open(path).convert('RGB')
    w, h = img.size
    arr = np.array(img, dtype=np.float32)

    # 1. Thumbnail UI
    thumb = img.resize((256, 256), Image.Resampling.LANCZOS)
    thumb_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_thumb.jpg")
    thumb.save(thumb_path, quality=90)

    # 2. Sampel kain kaki murni DARI SATU KAKI (kiri: X 320..440, Y 600..740)
    # Ini MENUNTASKAN masalah putih di celah selangkangan!
    leg_crop = img.crop((320, 600, 440, 720)).resize((512, 512), Image.Resampling.LANCZOS)
    fabric_swatch = make_seamless(leg_crop, blend_w=32)

    leg_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_leg.jpg")
    fabric_swatch.save(leg_path, quality=90)

    # 3. Area Ban Pinggang & Resleting Celana (Waistband & Zipper Fly)
    waist_crop = arr[50:420, 300:724]
    wh, ww, _ = waist_crop.shape

    # Deteksi warna background dari pojok foto
    corners = np.vstack([arr[:25,:25].reshape(-1,3), arr[:25,-25:].reshape(-1,3)])
    bg_color = np.median(corners, axis=0)

    # Masking hapus background putih di atas ban pinggang
    dist = np.max(np.abs(waist_crop - bg_color), axis=-1)
    alpha = np.clip((dist - 14.0) / 20.0, 0.0, 1.0)

    # Feathering batas bawah & samping agar menyatu mulus dengan kain denim
    border_fade = np.ones((wh, ww), dtype=np.float32)
    fade_px = 30
    for y in range(wh):
        if y > wh - fade_px:
            border_fade[y, :] *= (wh - y) / float(fade_px)
    for x in range(ww):
        if x < fade_px:
            border_fade[:, x] *= x / float(fade_px)
        elif x > ww - fade_px:
            border_fade[:, x] *= (ww - x) / float(fade_px)

    combined_alpha = alpha * border_fade
    alpha_img = Image.fromarray((combined_alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))

    target_w, target_h = 320, 370
    waist_resized = Image.fromarray(waist_crop.astype(np.uint8)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    alpha_resized = alpha_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    waist = fabric_swatch.copy()
    pos_x = (512 - target_w) // 2  # Lurus di tengah (X=256)
    pos_y = 10                    # Posisi atas ban pinggang
    waist.paste(waist_resized, (pos_x, pos_y), alpha_resized)

    waist_path = os.path.join(TEXTURES_DIR, f"{filename[:-4]}_waist.jpg")
    waist.save(waist_path, quality=90)

    return {
        "id": filename[:-4],
        "name": name,
        "price": price,
        "desc": desc,
        "fabric_type": fabric_type,
        "thumb_url": f"textures/{filename[:-4]}_thumb.jpg",
        "waist_url": f"textures/{filename[:-4]}_waist.jpg",
        "leg_url": f"textures/{filename[:-4]}_leg.jpg",
        "thumb_b64": to_base64(thumb),
        "waist_b64": to_base64(waist),
        "leg_b64": to_base64(fabric_swatch)
    }

def main():
    print("Memproses foto katalog produk asli tanpa potongan...")
    
    tops = [
        process_top(
            "tshirt_graphic_white.jpg",
            "Kaos Graphic Minimalist Putih",
            "Rp 149.000",
            "Katun combed 24s dengan sablon grafis geometris modern.",
            fabric_type="cotton"
        ),
        process_top(
            "flannel_red.jpg",
            "Kemeja Flanel Buffalo Merah",
            "Rp 229.000",
            "Kain flanel katun premium motif kotak merah-hitam.",
            fabric_type="flannel"
        ),
        process_top(
            "polo_navy.jpg",
            "Kaos Polo Pique Navy",
            "Rp 179.000",
            "Polo shirt katun rajut pique biru dongker dengan kancing mutiara.",
            fabric_type="pique"
        ),
        process_top(
            "tshirt_white_basic.jpg",
            "Kaos Polos Basic Putih",
            "Rp 99.000",
            "Kaos oblong putih polos combed 30s adem dan lembut.",
            fabric_type="cotton"
        )
    ]

    bottoms = [
        process_bottom(
            "jeans_blue.jpg",
            "Jeans Biru Klasik Regular Fit",
            "Rp 299.000",
            "Denim twill 13.5 oz cuci medium wash dengan aksen rivet tembaga.",
            fabric_type="denim"
        ),
        process_bottom(
            "jeans_indigo.jpg",
            "Jeans Indigo Gelap Raw Finish",
            "Rp 319.000",
            "Denim kaku raw indigo pekat dengan jahitan kontras warna emas.",
            fabric_type="denim"
        ),
        process_bottom(
            "chino_khaki.jpg",
            "Celana Chino Slim Khaki",
            "Rp 219.000",
            "Celana panjang chino katun stretch warna krem khaki kasual.",
            fabric_type="cotton"
        )
    ]

    catalog = {
        "tops": tops,
        "bottoms": bottoms
    }

    # Simpan JSON
    with open('products_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    # Simpan JS file agar bisa langsung di-include di HTML tanpa fetch CORS
    with open('products_catalog.js', 'w', encoding='utf-8') as f:
        f.write("/* Auto-generated product catalog with embedded base64 textures */\n")
        f.write("window.PRODUCT_CATALOG = ")
        json.dump(catalog, f, ensure_ascii=False)
        f.write(";\n")

    print("Selesai! File textures dan products_catalog.json/js berhasil dibuat dengan rapi tanpa potongan.")

if __name__ == '__main__':
    main()
