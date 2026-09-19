# ⚡ Flutter Önizleyici → APK

Flutter benzeri kod yaz, anında önizle, **dakikalar içinde APK** al.
**Kurulum yok. 3-5 GB değil, 0-500 MB. Ücretsiz.**

## 🚀 Hızlı Başlangıç

### 1. Kodu Yaz
Tarayıcıda aç: **https://KULLANICIADIN.github.io/flutter-preview/flutter.html**
(veya bu README'nin bulunduğu klasördeki `flutter.html`)

Sol panelde kod yaz. Sağda canlı önizleme.

### 2. APK Paketi İndir
Üst barda **📦 APK Oluştur** düğmesine bas.
`flutter-app-apk.zip` iner.

### 3. APK Üret — 2 Yoldan Biri

---

## 🥇 Yol A: PWABuilder (Kurulum YOK, 2 dakika)

**Hiçbir şey indirmeden, sadece tarayıcıyla APK al.**

1. ZIP'i bir klasöre çıkar (7-Zip, WinRAR vb. ile)
2. https://app.netlify.com/drop adresine **klasörü sürükle-bırak**
3. Netlify size bir URL verir: `https://mutlu-kedi-12345.netlify.app`
4. https://www.pwabuilder.com adresine git, URL'yi yapıştır → **Start**
5. **Package for Stores → Android → Generate → Download**
6. APK indi! 🎉

**Toplam süre:** 2 dakika  
**Kurulum:** 0 MB  
**Maliyet:** 0 ₺

---

## 🥈 Yol B: Python ile Lokal Build (İlk seferde 500 MB, sonra 30 sn)

**Tamamen kendi bilgisayarında, hiçbir siteye yüklemeden.**

### Gereksinimler
- **Python 3.8+** → https://python.org (varsa atla, ~30 MB)
- **Node.js 16+** → https://nodejs.org (~50 MB)

### Adımlar

```bash
# 1. ZIP'i çıkar
unzip flutter-app-apk.zip
cd flutter-app-apk

# 2. APK'yı üret (ilk seferde 5-10 dk, Android SDK iner)
python build_apk.py

# Sonraki çalıştırmalar ~30 saniye
