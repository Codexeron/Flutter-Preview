#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flutter Önizleyici → APK Builder
=================================

Kullanım:
    python build_apk.py                  # Mevcut klasördeki PWA'yı APK yap
    python build_apk.py --pwa-only       # Sadece PWA klasörünü hazırla (APK'sız)
    python build_apk.py --port 8899      # Farklı port

İlk çalıştırma: ~500 MB indirir (Android SDK + bubblewrap)
Sonraki: ~30 saniye
Gereksinim: Python 3.8+, Node.js 16+, Java 17+
"""

import os, sys, json, shutil, subprocess, tempfile, time, socket
import http.server, socketserver, threading, webbrowser, zipfile
from pathlib import Path

# ─── Ayarlar ────────────────────────────────────────────────
DEFAULT_PORT = 8765
APP_NAME = "FlutterApp"
APP_ID = "com.flutterpreview.app"
OUTPUT_APK = "flutter-app.apk"

# ─── Renkler ────────────────────────────────────────────────
class C:
    OK = "\033[92m"; WARN = "\033[93m"; ERR = "\033[91m"
    INFO = "\033[96m"; END = "\033[0m"
    def __init__(self): pass

def log(msg, kind="info"):
    colors = {"ok": C.OK, "warn": C.WARN, "err": C.ERR, "info": C.INFO}
    prefix = {"ok": "✓", "warn": "⚠", "err": "✗", "info": "ℹ"}
    print(f"{colors.get(kind,C.INFO)}{prefix.get(kind,' ')} {msg}{C.END}")

# ─── Kontroller ─────────────────────────────────────────────
def have(cmd):
    try:
        subprocess.run([cmd, "--version"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def check_env():
    missing = []
    if not have("node"):
        missing.append("Node.js (https://nodejs.org)")
    if not have("npx"):
        missing.append("npx (Node.js ile gelir)")
    if missing:
        log("Eksik programlar:", "err")
        for m in missing: print(f"   • {m}")
        sys.exit(1)
    log("Node.js ve npx hazır", "ok")

# ─── Basit HTTP sunucusu (bubblewrap URL ister) ─────────────
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def start_server(directory, port):
    os.chdir(directory)
    handler = QuietHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def free_port():
    s = socket.socket()
    s.bind(("", 0))
    p = s.getsockname()[1]
    s.close()
    return p

# ─── Bubblewrap ile APK üret ────────────────────────────────
def build_with_bubblewrap(source_dir, output_dir, port):
    """source_dir içindeki PWA'yı bubblewrap ile APK yapar"""
    log("HTTP sunucusu başlatılıyor...", "info")
    httpd = start_server(source_dir, port)
    url = f"http://localhost:{port}"
    log(f"PWA sunuldu: {url}", "ok")

    # Build klasörü
    build_dir = Path(tempfile.mkdtemp(prefix="bubblewrap-"))
    log(f"Çalışma klasörü: {build_dir}", "info")

    try:
        # bubblewrap init
        log("Bubblewrap ile Android projesi kuruluyor (ilk seferde 3-5 dk)...", "info")
        manifest_url = f"{url}/manifest.json"

        result = subprocess.run([
            "npx", "--yes", "@bubblewrap/cli", "init",
            "--manifest", manifest_url,
            "--directory", str(build_dir),
        ], input=f"\n", text=True, capture_output=True, timeout=1800)

        if result.returncode != 0:
            log("Init hatası:", "err")
            print(result.stdout); print(result.stderr)
            raise RuntimeError("bubblewrap init başarısız")

        log("Bubblewrap build başlıyor...", "info")
        result = subprocess.run([
            "npx", "--yes", "@bubblewrap/cli", "build",
            "--directory", str(build_dir),
        ], text=True, capture_output=True, timeout=1800)

        if result.returncode != 0:
            log("Build hatası:", "err")
            print(result.stdout); print(result.stderr)
            raise RuntimeError("bubblewrap build başarısız")

        # APK'yı bul
        candidates = list(build_dir.glob("*.apk"))
        if not candidates:
            raise RuntimeError("APK üretilemedi")

        apk = candidates[0]
        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / OUTPUT_APK
        shutil.copy(apk, dest)
        log(f"APK hazır: {dest}", "ok")
        return dest

    finally:
        httpd.shutdown()
        shutil.rmtree(build_dir, ignore_errors=True)

# ─── ZIP içeriğini çıkar ────────────────────────────────────
def extract_zip(zip_path, target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(target_dir)
    log(f"ZIP açıldı: {target_dir}", "ok")

# ─── PWA doğrulama ──────────────────────────────────────────
def verify_pwa(directory):
    required = ["index.html", "manifest.json"]
    missing = [f for f in required if not (directory / f).exists()]
    if missing:
        log(f"Eksik dosyalar: {missing}", "err")
        sys.exit(1)
    log("PWA dosyaları doğrulandı", "ok")

# ─── Ana akış ───────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    pwa_only = "--pwa-only" in args
    port_arg = None
    for i, a in enumerate(args):
        if a == "--port" and i + 1 < len(args):
            port_arg = int(args[i+1])

    src = Path.cwd()

    # ZIP verilmişse aç
    zips = list(src.glob("*.zip"))
    if zips and not (src / "index.html").exists():
        log(f"ZIP bulundu: {zips[0].name}", "info")
        extract_zip(zips[0], src)
        zips[0].unlink()

    verify_pwa(src)

    if pwa_only:
        log("--pwa-only: Sadece klasör hazır. Sıradaki adımlar:", "info")
        print("   1. https://app.netlify.com/drop adresine bu klasörü sürükle")
        print("   2. Oluşan URL'yi https://pwabuilder.com'a ver")
        print("   3. APK indir")
        return

    check_env()
    port = port_arg or free_port()
    output_dir = src / "output"

    print()
    log("İlk çalıştırma 5-10 dk sürebilir (Android SDK indirilir)", "warn")
    log("Sonraki çalıştırmalar ~30 saniye", "info")
    print()

    try:
        apk = build_with_bubblewrap(src, output_dir, port)
        print()
        log("=" * 50, "ok")
        log(f"BAŞARILI — APK: {apk}", "ok")
        log("=" * 50, "ok")
        print()
        print(f"  {C.INFO}Telefona kurmak için:{C.END}")
        print(f"    1. {apk} dosyasını telefona kopyala")
        print(f"    2. Telefonda dosyayı aç")
        print(f"    3. 'Bilinmeyen kaynaklara izin ver' → Kur")
        print()
    except Exception as e:
        log(f"Build başarısız: {e}", "err")
        log("Alternatif: python build_apk.py --pwa-only", "warn")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        log("İptal edildi", "warn")
        sys.exit(130)
