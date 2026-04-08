# 💅 Güzellik Merkezi Randevu Yönetim Sistemi

> **Öğrenci Projesi** | Python Flask + SQLite + Bootstrap 5  
> Veri Akış Diyagramı (DFD) tabanlı, tam özellikli randevu yönetim sistemi

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [DFD ile Kod Eşleşmesi](#-dfd-ile-kod-eşleşmesi)
- [Özellikler](#-özellikler)
- [Proje Yapısı](#-proje-yapısı)
- [Veritabanı Tasarımı](#️-veritabanı-tasarımı)
- [Kurulum](#-kurulum)
- [Kullanım Kılavuzu](#-kullanım-kılavuzu)
- [Route Tablosu](#-route-tablosu)
- [Güvenlik](#-güvenlik)
- [Sistem Loglama](#-sistem-loglama)
- [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

## 📖 Proje Hakkında

Bu proje, bir güzellik merkezi için **uçtan uca randevu yönetim sistemi** sunar. Sistem; müşteri randevu alma, personel onay ve takvim yönetimi, admin raporlama ve loglama gibi tüm süreçleri kapsar.

Proje, **Veri Akış Diyagramı (DFD)** temel alınarak tasarlanmıştır. Her süreç numarası (1.0, 2.0 … 8.0) doğrudan kod içindeki bir route veya fonksiyona karşılık gelir.

### Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+ / Flask 3.0 |
| Veritabanı | SQLite (randevu.db) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Takvim | FullCalendar.js 6.1 (CDN) |
| E-posta | Gmail SMTP (smtplib) |
| Şifreleme | SHA-256 (hashlib) |

---

## 🗺 DFD ile Kod Eşleşmesi

Projede kullanılan DFD (Veri Akış Diyagramı) her bir süreç numarasıyla eşleşmektedir:

| DFD Süreci | Açıklama | Kod Konumu |
|-----------|----------|------------|
| **1.0** | Kullanıcı Giriş Yapması | `routes/auth_routes.py` → `login_page()` |
| **2.0** | Randevu Talebi Oluştur | `routes/musteri_routes.py` → `randevu_al()` |
| **3.0** | Uygunluk Kontrolü | `utils/validators.py` → `cakisma_var_mi()` |
| **4.0** | Onaylanan Randevu Kaydı | `routes/personel_routes.py` → `randevu_onayla()` |
| **5.0** | Randevu Bilgisi Hatırlatma | `routes/personel_routes.py` → `hatirlatma_gonder()` |
| **6.0** | Randevu Gelme Durumu | `routes/personel_routes.py` → `gelme_durumu_guncelle()` |
| **7.0** | Personel Değerlendirme | `routes/admin_routes.py` + personel paneli |
| **8.0** | Müşterinin Formu Doldurması | `routes/musteri_routes.py` → `degerlendirme_yap()` |

### Veri Depoları (D1–D6)

| DFD Deposu | Karşılık Gelen Tablo |
|-----------|---------------------|
| D1 – Müşteri Kayıtları | `musteriler` |
| D2 – Randevu Veritabanı | `randevular` |
| D3 – Onaylanan Randevu Bilgileri | `randevular` (durum='onaylandi') |
| D4 – Personel Veritabanı | `personeller` |
| D5 – Boş Değerlendirme Formları | `hizmetler` |
| D6 – Dolu Değerlendirme Formları | `degerlendirmeler` |

---

## ✨ Özellikler

### 👤 Müşteri

- Telefon + şifre ile kayıt ve giriş
- Şifre sıfırlama (telefon numarasıyla)
- Profil güncelleme (ad-soyad, telefon, e-posta)
- İşlem, personel ve tarih/saat seçerek randevu alma
- Randevularını liste görünümünde takip etme
- Beklemedeki randevuyu iptal etme → **otomatik e-posta bildirimi**
- Tamamlanan randevular için personel değerlendirmesi

### 👩‍💼 Personel

- E-posta + şifre ile giriş
- Şifre değiştirme
- Kendi randevularını listeleme ve filtreleme
- Randevu onaylama / reddetme
- Müşteri gelme durumu işaretleme (geldi / gelmedi) → puan güncelleme
- Randevu hatırlatma e-postası gönderme (tek seferlik)
- Değerlendirmelerini görüntüleme ve ortalama puan takibi

### 🛠 Admin

- Dashboard: anlık sistem istatistikleri
- Müşteri yönetimi: listeleme, **ada/telefona/e-postaya göre arama**, aktif/ban
- Personel yönetimi: ekleme, **çoklu uzmanlık atama**, çalışma saati tanımlama
- Tatil / izin günü tanımlama (sistem geneli veya personel bazlı)
- Tüm randevuları görüntüleme
- Toplu hatırlatma e-postası gönderme
- Dinamik hizmet ekleme/çıkarma (işlem süresi dahil)
- İstatistik ekranı: personel performansı, müşteri davranış analizi
- **Sistem log görüntüleyici**: seviye ve işlem bazlı filtreleme

### 🔧 Sistem

- **Akıllı çakışma kontrolü**: işlem süresi bazlı — 60 dk'lık botoks randevusu bitmeden yeni randevu açılmaz
- **Çalışma saati kısıtlaması**: personel tanımlanmış saatler dışına randevu alamaz
- **Tatil günü kısıtlaması**: tatil günleri randevu alınamaz
- **Kapsamlı loglama**: tüm kritik işlemler (giriş, randevu, admin eylemleri) veritabanına kaydedilir
- Validasyon: ad-soyad sadece harf, telefon sadece rakam (hem JS hem Python)
- **Puan sistemi**: zamanında gelme +10, gelmeme -20, başlangıç 100

---

## 📁 Proje Yapısı

```
randevu_sistemi/
│
├── app.py                          # Flask uygulama fabrikası, blueprint kayıtları
├── config.py                       # Gmail SMTP, gizli anahtar, DB yolu
├── database.py                     # init_db(), get_db(), tablo şemaları
├── requirements.txt                # Python bağımlılıkları
│
├── routes/
│   ├── auth_routes.py              # Giriş, kayıt, çıkış (müşteri + personel)
│   ├── musteri_routes.py           # Randevu alma, listeleme, iptal, değerlendirme
│   ├── personel_routes.py          # Onay, reddet, gelme durumu, hatırlatma, takvim
│   └── admin_routes.py             # Admin paneli, müşteri/personel yönetimi, loglar
│
├── utils/
│   ├── auth_helper.py              # SHA-256 hash, session kontrol fonksiyonları
│   ├── email_helper.py             # Gmail SMTP, HTML e-posta şablonları
│   ├── validators.py               # Form validasyonu, akıllı çakışma kontrolü
│   └── logger.py                   # Sistem loglama modülü
│
└── templates/
    ├── base.html                   # Ana şablon, navbar, flash mesajları
    │
    ├── auth/
    │   ├── login.html              # Müşteri giriş sayfası
    │   ├── kayit.html              # Müşteri kayıt sayfası
    │   ├── personel_login.html     # Personel/Admin giriş sayfası
    │   └── sifremi_unuttum.html    # Şifre sıfırlama
    │
    ├── musteri/
    │   ├── panel.html              # Müşteri ana sayfası
    │   ├── randevu_al.html         # Randevu alma formu
    │   ├── randevularim.html       # Randevu listesi
    │   ├── degerlendirme.html      # Personel değerlendirme formu
    │   └── profil.html             # Profil güncelleme
    │
    ├── personel/
    │   ├── panel.html              # Personel ana sayfası
    │   ├── randevular.html         # Randevu listesi ve işlemler
    │   ├── degerlendirmelerim.html # Kendi değerlendirmeleri
    │   └── sifre_degistir.html     # Şifre değiştirme
    │
    └── admin/
        ├── panel.html              # Admin dashboard
        ├── musteriler.html         # Müşteri listesi + arama
        ├── personeller.html        # Personel listesi
        ├── personel_ekle.html      # Personel ekleme (çoklu uzmanlık)
        ├── personel_calisma.html   # Haftalık çalışma saatleri
        ├── tatil_gunleri.html      # Tatil/izin yönetimi
        ├── tum_randevular.html     # Tüm randevular
        ├── istatistikler.html      # Raporlar
        ├── hizmetler.html          # Hizmet yönetimi (süre dahil)
        └── loglar.html             # Sistem log görüntüleyici
```

---

## 🗄️ Veritabanı Tasarımı

SQLite veritabanı (`randevu.db`) uygulama ilk çalıştığında **otomatik oluşturulur**. Elle SQL çalıştırmaya gerek yoktur.

### Tablo İlişki Şeması

```
musteriler ──┐
             ├──► randevular ◄──── personeller
             │         │
             │         └──► degerlendirmeler
             │
             └── (puan, gelmeme_sayisi)

personeller ──► personel_uzmanliklar ◄── hizmetler
personeller ──► personel_calisma_saatleri
personeller ──► tatil_gunleri (personel_id NULL = sistem geneli)

loglar (bağımsız — tüm olayları kaydeder)
```

### `musteriler`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | Otomatik artan |
| ad_soyad | TEXT | Ad ve soyad |
| telefon | TEXT UNIQUE | Giriş anahtarı |
| email | TEXT | Hatırlatma için (opsiyonel) |
| sifre_hash | TEXT | SHA-256 hash |
| puan | INTEGER | Başlangıç: 100 |
| gelmeme_sayisi | INTEGER | Kaç randevuya gelmedi |
| aktif | INTEGER | 1=aktif, 0=banlı |

### `personeller`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| ad_soyad | TEXT | - |
| email | TEXT UNIQUE | Giriş anahtarı |
| sifre_hash | TEXT | SHA-256 hash |
| uzmanlik | TEXT | Geriye dönük uyumluluk için tutulur |
| rol | TEXT | 'personel' veya 'admin' |
| aktif | INTEGER | 1=aktif, 0=pasif |

### `randevular`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| musteri_id | INTEGER FK | → musteriler |
| personel_id | INTEGER FK | → personeller |
| islem | TEXT | Yapılacak hizmet adı |
| tarih | TEXT | YYYY-MM-DD |
| saat | TEXT | HH:MM |
| durum | TEXT | beklemede / onaylandi / reddedildi / tamamlandi / gelmedi |
| hatirlatma_gonderildi | INTEGER | 0=hayır, 1=evet |
| olusturma_tarihi | TEXT | datetime('now') |

### `degerlendirmeler`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| randevu_id | INTEGER UNIQUE FK | Her randevu 1 değerlendirme |
| musteri_id | INTEGER FK | - |
| personel_id | INTEGER FK | - |
| hizmet_puani | INTEGER | 1–5 |
| tutum_puani | INTEGER | 1–5 |
| sure_puani | INTEGER | 1–5 |
| yorum | TEXT | Opsiyonel |

### `hizmetler`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| ad | TEXT UNIQUE | Hizmet adı |
| sure_dakika | INTEGER | İşlem süresi (çakışma kontrolünde kullanılır) |
| aktif | INTEGER | 1=aktif, 0=pasif |

### `personel_uzmanliklar`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| personel_id | INTEGER FK | - |
| hizmet_id | INTEGER FK | - |
| UNIQUE(personel_id, hizmet_id) | — | Aynı kombinasyon 2 kez girilemesin |

### `personel_calisma_saatleri`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| personel_id | INTEGER FK | - |
| gun | INTEGER | 0=Pazartesi … 6=Pazar |
| baslangic_saat | TEXT | HH:MM |
| bitis_saat | TEXT | HH:MM |

### `tatil_gunleri`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| personel_id | INTEGER FK / NULL | NULL → sistem geneli tatil |
| tarih | TEXT | YYYY-MM-DD |
| aciklama | TEXT | "Kurban Bayramı", "Yıllık İzin" vb. |

### `loglar`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| zaman | TEXT | datetime('now') |
| seviye | TEXT | INFO / AUDIT / WARNING / ERROR |
| kullanici | TEXT | ad_soyad veya 'anonim' |
| rol | TEXT | musteri / personel / admin / sistem |
| islem | TEXT | Kısa eylem kodu: 'giris_basarili', 'randevu_al' vb. |
| detay | TEXT | Uzun açıklama |
| ip_adresi | TEXT | İstemci IP |

---

## ⚙️ Kurulum

### 1. Gereksinimler

- Python 3.10 veya üzeri
- pip

### 2. Projeyi İndir

```bash
git clone <repo-url>
cd randevu_sistemi
```

### 3. Sanal Ortam Oluştur

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Kur

```bash
pip install -r requirements.txt
```

`requirements.txt` içeriği:
```
Flask==3.0.0
Werkzeug==3.0.1
openpyxl==3.1.2
reportlab==4.1.0
```

### 5. Gmail SMTP Ayarı

`config.py` dosyasını aç ve şu alanları düzenle:

```python
MAIL_USERNAME = "senin-gmail@gmail.com"
MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"   # Gmail Uygulama Şifresi
```

> **Gmail Uygulama Şifresi Nasıl Alınır?**
> 1. Google Hesabı → Güvenlik → 2 Adımlı Doğrulama'yı aç
> 2. Güvenlik → Uygulama şifreleri → "Posta / Windows Bilgisayarı"
> 3. Üretilen 16 haneli şifreyi `MAIL_PASSWORD`'e yapıştır

### 6. Uygulamayı Başlat

```bash
python app.py
```

Tarayıcıda aç: [http://localhost:5000](http://localhost:5000)

> Port meşgulse `app.py` içinde `port=5001` yap ve `http://localhost:5001` adresiyle dene.

### 7. İlk Kurulum Notu

Uygulama ilk çalıştığında `randevu.db` otomatik oluşturulur. Varsayılan admin hesabı da otomatik eklenir:

```
E-posta : admin@medicalpoint.com
Şifre   : admin123
```

> ⚠️ İlk girişten sonra şifreyi değiştirmeyi unutma!

---

## 🧭 Kullanım Kılavuzu

### Müşteri Olarak

1. Ana sayfada **Kayıt Ol** → ad-soyad, telefon, şifre gir
2. Giriş yap → **Randevu Al**
3. İşlem seç → Personel seç → Tarih ve saat seç
   - Sistem tatil günlerini ve personel çalışma saatlerini otomatik filtreler
   - Akıllı çakışma kontrolü: işlem süresi bitmeden çakışan saat seçilemez
4. Randevu onayını bekle → Onaylanınca e-posta ile bildirim gelir
5. Randevu günü gelince personel "Geldi" işaretler → +10 puan
6. Randevu tamamlandıktan sonra **Değerlendir** → personele puan ver

### Personel Olarak

```
Giriş: /auth/personel-login
E-posta + şifre (admin tarafından oluşturulur)
```

1. Panel'den bekleyen randevuları gör
2. **Onayla** veya **Reddet**
3. Randevu saati geldiğinde **Geldi / Gelmedi** işaretle
4. **Hatırlatma Gönder** → müşteriye e-posta hatırlatması

### Admin Olarak

```
Giriş: /auth/personel-login
E-posta: admin@medicalpoint.com
```

**Personel Ekle:**
- Ad-soyad, e-posta, şifre gir
- Çoklu uzmanlık seç (checkbox listesi)
- Personel eklendikten sonra **Çalışma Saatleri** butonuyla gün/saat tanımla

**Tatil Yönetimi:**
- Admin Panel → **Tatil/İzin** menüsü
- Sistem geneli tatil (bayram, resmi tatil) → Personel boş bırak
- Personel izni → İlgili personeli seç

**Raporlama:**
- İstatistikler sayfasından performans analizi görüntüle

**Loglar:**
- Admin Panel → **Loglar** menüsü
- Seviye filtresi: INFO / AUDIT / WARNING / ERROR
- İşlem filtresi: `giris`, `randevu`, `admin` gibi anahtar kelimelerle ara

---

## 🌐 Route Tablosu

### Auth

| Method | URL | Açıklama |
|--------|-----|----------|
| GET/POST | `/auth/login` | Müşteri girişi |
| GET/POST | `/auth/kayit` | Müşteri kaydı |
| GET/POST | `/auth/sifremi-unuttum` | Şifre sıfırlama |
| GET/POST | `/auth/personel-login` | Personel / Admin girişi |
| GET | `/auth/cikis` | Oturumu kapat |

### Müşteri

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | `/musteri/panel` | Ana panel |
| GET/POST | `/musteri/randevu-al` | Randevu alma formu |
| GET | `/musteri/randevularim` | Randevu listesi |
| GET/POST | `/musteri/degerlendirme/<id>` | Değerlendirme formu |
| POST | `/musteri/randevu-iptal/<id>` | Randevu iptali + e-posta |
| GET/POST | `/musteri/profil` | Profil güncelleme |

### Personel

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | `/personel/panel` | Ana panel |
| GET | `/personel/randevular` | Randevu listesi (filtreli) |
| POST | `/personel/onayla/<id>` | Randevu onayla |
| POST | `/personel/reddet/<id>` | Randevu reddet |
| POST | `/personel/gelme/<id>` | Gelme durumu güncelle + puan |
| POST | `/personel/hatirlatma/<id>` | Hatırlatma e-postası gönder |
| GET | `/personel/degerlendirmelerim` | Kendi değerlendirmeleri |
| GET/POST | `/personel/sifre-degistir` | Şifre değiştirme |

### Admin

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | `/admin/panel` | Dashboard |
| GET | `/admin/musteriler` | Müşteri listesi + arama (`?q=`) |
| GET | `/admin/musteriler-indir/excel` | Müşteri listesi Excel indir |
| POST | `/admin/musteri-durum/<id>` | Müşteri aktif/ban toggle |
| GET | `/admin/personeller` | Personel listesi |
| GET/POST | `/admin/personel-ekle` | Yeni personel ekle |
| GET/POST | `/admin/personel-calisma/<id>` | Haftalık çalışma saatleri |
| GET/POST | `/admin/tatil-gunleri` | Tatil/izin yönetimi |
| GET | `/admin/tum-randevular` | Tüm randevular |
| GET | `/admin/istatistikler` | Performans raporları |
| GET/POST | `/admin/hizmetler` | Hizmet yönetimi |
| POST | `/admin/toplu-hatirlatma` | Toplu e-posta gönder |
| GET | `/admin/loglar` | Sistem log görüntüleyici |

---

## 🔒 Güvenlik

### Şifre Hashleme

Tüm şifreler **SHA-256** ile hashlenerek saklanır. Düz metin şifre asla veritabanında bulunmaz.

```python
# utils/auth_helper.py
import hashlib

def hash_sifre(sifre: str) -> str:
    return hashlib.sha256(sifre.encode()).hexdigest()

def sifre_dogru_mu(sifre: str, hash_deger: str) -> bool:
    return hash_sifre(sifre) == hash_deger
```

### Session Yönetimi

Her rol için ayrı session kontrolü yapılır:

```python
def musteri_mi()  → session.get('rol') == 'musteri'
def personel_mi() → session.get('rol') in ('personel', 'admin')
def admin_mi()    → session.get('rol') == 'admin'
```

### Form Validasyonu

İki katmanlı validasyon — hem JavaScript (anlık geri bildirim) hem Python (güvenli taraf):

- Ad-soyad: yalnızca harf ve boşluk (`^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$`)
- Telefon: yalnızca rakam, 10 hane
- E-posta: standart format kontrolü
- Şifre: minimum 6 karakter

### Yetkilendirme

Her blueprint'te `@giris_gerekli`, `@personel_giris_gerekli`, `@admin_gerekli` decorator'ları kullanılır. Yetkisiz erişim denemelerinde otomatik yönlendirme yapılır ve log kaydı düşülür.

---

## 📋 Sistem Loglama

`utils/logger.py` modülü tüm kritik olayları `loglar` tablosuna kaydeder.

### Log Seviyeleri

| Seviye | Renk | Kullanım |
|--------|------|----------|
| `INFO` | Gri | Normal işlemler: giriş, randevu alma |
| `AUDIT` | Mavi | Yetkili işlemler: admin eylemleri, onay/red |
| `WARNING` | Sarı | Başarısız giriş denemeleri |
| `ERROR` | Kırmızı | Sistem hataları |

### Otomatik Loglanan İşlemler

- ✅ Müşteri / personel giriş denemeleri (başarılı ve başarısız)
- ✅ Randevu oluşturma, onaylama, reddetme, iptal, tamamlama
- ✅ Admin: personel ekleme, çalışma saati güncelleme, tatil ekleme/silme
- ✅ Müşteri puan değişimleri

### Kullanım Örneği

```python
from utils.logger import log_yaz, log_randevu, log_admin

# Genel log
log_yaz(islem='ozel_islem', detay='Açıklama', seviye='INFO')

# Randevu logu
log_randevu(eylem='onayla', randevu_id=42, detay='10:00 – Botoks')

# Admin logu
log_admin(eylem='personel_ekle', detay='Ayşe Yılmaz eklendi')
```

> Loglama hiçbir zaman ana işlemi durdurmaz. Hata oluşursa sessizce `print` yapar ve devam eder.

---

## ❓ Sık Sorulan Sorular

**S: Randevu.db dosyası nerede oluşuyor?**  
A: Proje kök dizininde, `app.py` ile aynı klasörde oluşur.

**S: Veritabanını sıfırlamak istiyorum, ne yapmalıyım?**  
A: `randevu.db` dosyasını sil, uygulamayı yeniden başlat. Tablolar ve varsayılan admin yeniden oluşturulur.

**S: E-posta gönderilmiyor, ne yapmalıyım?**  
A: `config.py`'deki `MAIL_USERNAME` ve `MAIL_PASSWORD` değerlerini kontrol et. `MAIL_PASSWORD` Gmail şifren değil, **Uygulama Şifresi** olmalıdır.

**S: 5000 portu meşgul hatası alıyorum.**  
A: `app.py` içinde `port=5001` yap ve `http://localhost:5001` adresine git.

**S: Personel randevu alırken görünmüyor.**  
A: Personelin ilgili hizmette **uzmanlığı** tanımlı olmalı. Admin → Personel Ekle / Düzenle → uzmanlık checkbox'larını kontrol et.

**S: Randevu alırken saat seçenekleri neden boş?**  
A: Seçilen tarihin personelin **çalışma saatleri** dışında olması veya o tarihin **tatil günü** olarak tanımlı olması sebebiyle filtrelenmiş olabilir.

**S: Puan sistemi nasıl çalışıyor?**  
A: Başlangıç puanı 100. Randevuya zamanında gelince +10, gelmeyince -20 puan. Puan hiçbir zaman 0'ın altına düşmez. Admin panelinde müşteri puanları izlenebilir.

---

## 📝 Geliştirme Notları

Bu proje bir öğrenci projesidir. Üretim ortamına taşımadan önce şu adımlar önerilir:

- [ ] SHA-256 → **bcrypt** şifreleme geçişi (`bcrypt` kütüphanesi)
- [ ] `SECRET_KEY` değerini ortam değişkeninden oku (`.env` dosyası)
- [ ] SQLite → PostgreSQL geçişi (büyük ölçekli kullanım için)
- [ ] Rate limiting ekle (brute-force koruması için)
- [ ] HTTPS sertifikası (Let's Encrypt)

---

*Bu proje DFD tabanlı sistem analizi ve Python Flask geliştirme pratiği amacıyla oluşturulmuştur.*
