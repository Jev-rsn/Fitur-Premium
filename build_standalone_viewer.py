#!/usr/bin/env python3
"""
Membangun katalog produk dengan color_hex murni (0xffffff)
agar tekstur foto asli dirender dengan warna asli tanpa penggelapan.
"""
import os, json

with open('products_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

for t in catalog['tops']:
    t['color_hex'] = 0xffffff

for b in catalog['bottoms']:
    b['color_hex'] = 0xffffff

with open('products_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

with open('products_catalog.js', 'w', encoding='utf-8') as f:
    f.write("/* Auto-generated product catalog with embedded base64 textures */\n")
    f.write("window.PRODUCT_CATALOG = ")
    json.dump(catalog, f, ensure_ascii=False)
    f.write(";\n")

print("Katalog produk diperbarui dengan color_hex murni 0xffffff.")
