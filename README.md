<<<<<<< HEAD
#  Güzellik Merkezi Randevu Yönetim Sistemi

=======
# 💅 Güzellik Merkezi Randevu Yönetim Sistemi

> **Öğrenci Projesi** | Python Flask + SQLite + Bootstrap 5  
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
> Veri Akış Diyagramı (DFD) tabanlı, tam özellikli randevu yönetim sistemi

---

<<<<<<< HEAD
##  İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Teknoloji Yığını](#-teknoloji-yığını)
=======
## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
- [DFD ile Kod Eşleşmesi](#-dfd-ile-kod-eşleşmesi)
- [Özellikler](#-özellikler)
- [Proje Yapısı](#-proje-yapısı)
- [Veritabanı Tasarımı](#️-veritabanı-tasarımı)
- [Kurulum](#-kurulum)
- [Kullanım Kılavuzu](#-kullanım-kılavuzu)
- [Route Tablosu](#-route-tablosu)
- [Güvenlik](#-güvenlik)
- [Sistem Loglama](#-sistem-loglama)
<<<<<<< HEAD
- [Geliştirme Notları](#-geliştirme-notları)
=======
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
- [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

<<<<<<< HEAD
##  Proje Hakkında

Bu proje, bir güzellik merkezi için **uçtan uca randevu yönetim sistemi** sunar. Müşteri randevu alma, personel onay ve takvim yönetimi, admin raporlama ve loglama gibi tüm süreçleri kapsar.

| Rol | Açıklama |
|-----|----------|
| 👤 **Müşteri** | Randevu alır, değerlendirme yapar, geçmişini görür |
| 👩‍💼 **Personel** | Randevuları onaylar, gelme durumunu işler, değerlendirmeleri görür |
| 🛠 **Admin** | Tüm sistemi yönetir, istatistikleri izler, personel ekler |

---

## 🛠 Teknoloji Yığını
=======
## 📖 Proje Hakkında

Bu proje, bir güzellik merkezi için **uçtan uca randevu yönetim sistemi** sunar. Sistem; müşteri randevu alma, personel onay ve takvim yönetimi, admin raporlama ve loglama gibi tüm süreçleri kapsar.


| Rol | Açıklama |
|-----|----------|
|  **Müşteri** | Randevu alır, değerlendirme yapar, geçmişini görür |
|  **Personel** | Randevuları onaylar, gelme durumunu işler, değerlendirmeleri görür |
|  **Admin** | Tüm sistemi yönetir, istatistikleri izler, personel ekler |

---

##  DFD ile Kod Eşleşmesi
=======
Proje, **Veri Akış Diyagramı (DFD)** temel alınarak tasarlanmıştır. Her süreç numarası (1.0, 2.0 … 8.0) doğrudan kod içindeki bir route veya fonksiyona karşılık gelir.

### Teknoloji Yığını
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+ / Flask 3.0 |
<<<<<<< HEAD
| Veritabanı | SQLite (`randevu.db`) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Navigasyon | Offcanvas Sidebar (responsive, tüm ekran boyutları) |
| E-posta | Gmail SMTP (`smtplib`) |
| Şifreleme | SHA-256 (`hashlib`) |
| Export | openpyxl (Excel) + reportlab (PDF) |
=======
| Veritabanı | SQLite (randevu.db) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Takvim | FullCalendar.js 6.1 (CDN) |
| E-posta | Gmail SMTP (smtplib) |
| Şifreleme | SHA-256 (hashlib) |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

---

## 🗺 DFD ile Kod Eşleşmesi

<<<<<<< HEAD
Projede kullanılan DFD (Veri Akış Diyagramı) her bir süreç numarasıyla birebir eşleşmektedir:
=======

Projede kullanılan DFD (Veri Akış Diyagramı) her bir süreç numarasıyla eşleşmektedir:
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

| DFD Süreci | Açıklama | Kod Konumu |
|-----------|----------|------------|
| **1.0** | Kullanıcı Giriş Yapması | `routes/auth_routes.py` → `login_page()` |
| **2.0** | Randevu Talebi Oluştur | `routes/musteri_routes.py` → `randevu_al()` |
| **3.0** | Uygunluk Kontrolü | `utils/validators.py` → `cakisma_var_mi()` |
| **4.0** | Onaylanan Randevu Kaydı | `routes/personel_routes.py` → `randevu_onayla()` |
| **5.0** | Randevu Bilgisi Hatırlatma | `routes/personel_routes.py` → `hatirlatma_gonder()` |
| **6.0** | Randevu Gelme Durumu | `routes/personel_routes.py` → `gelme_durumu_guncelle()` |
<<<<<<< HEAD
| **7.0** | Personel Değerlendirme İşlemi | `routes/admin_routes.py` + personel paneli |
=======
| **7.0** | Personel Değerlendirme | `routes/admin_routes.py` + personel paneli |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
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

<<<<<<< HEAD
##  Özellikler

###  Müşteri
=======
## ✨ Özellikler


### Müşteri Özellikleri
-  Telefon numarası + şifre ile giriş
-  Ad-Soyad ve telefon validasyonu (sadece harf / sadece rakam)
-  İşlem, personel, tarih ve saat seçimi (tek sayfada)
-  Randevu uygunluk kontrolü (çakışma engelleme)
-  Randevu iptal etme (sadece beklemedekiler)
-  Tamamlanan randevuları değerlendirme (1-5 yıldız sistemi)
-  Puan takibi (zamanında gelme → +10, gelmeme → -20)

### Personel Özellikleri
-  E-posta + şifre ile giriş
-  Bugünkü randevuları görme
-  Randevu onaylama / reddetme
-  Müşteriye e-posta hatırlatması gönderme (Gmail SMTP)
-  Gelme durumu güncelleme (tamamlandı / gelmedi)
-  Kendi değerlendirmelerini ve ortalama puanlarını görme

### Admin Özellikleri
-  Sistem geneli dashboard (istatistikler)
-  Tüm müşterileri listeleme ve ban/unban
-  Personel ekleme ve listeleme
-  Tüm randevuları filtreleme (durum, tarih)
-  Toplu e-posta hatırlatması gönderme
-  İstatistikler sayfası (aylık randevular, popüler işlemler, performans)
=======
### 👤 Müşteri
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

- Telefon + şifre ile kayıt ve giriş
- Şifre sıfırlama (telefon numarasıyla)
- Profil güncelleme (ad-soyad, telefon, e-posta)
<<<<<<< HEAD
- İşlem, personel ve tarih/saat seçerek randevu alma (tek sayfada)
- Randevularını liste görünümünde takip etme
- Beklemedeki randevuyu iptal etme → otomatik e-posta bildirimi
- Tamamlanan randevular için personel değerlendirmesi (hizmet / tutum / süre, 1–5 yıldız)

###  Personel
=======
- İşlem, personel ve tarih/saat seçerek randevu alma
- Randevularını liste görünümünde takip etme
- Beklemedeki randevuyu iptal etme → **otomatik e-posta bildirimi**
- Tamamlanan randevular için personel değerlendirmesi

### 👩‍💼 Personel
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

- E-posta + şifre ile giriş
- Şifre değiştirme
- Kendi randevularını listeleme ve filtreleme
- Randevu onaylama / reddetme
- Müşteri gelme durumu işaretleme (geldi / gelmedi) → puan güncelleme
- Randevu hatırlatma e-postası gönderme (tek seferlik)
- Değerlendirmelerini görüntüleme ve ortalama puan takibi

<<<<<<< HEAD
### Admin

- Dashboard: anlık sistem istatistikleri
- Müşteri yönetimi: listeleme, ada/telefona/e-postaya göre arama, aktif/ban
- Personel yönetimi: ekleme, çoklu uzmanlık atama, çalışma saati tanımlama
- Tatil / izin günü tanımlama (sistem geneli veya personel bazlı)
- Tüm randevuları görüntüleme ve filtreleme
- Excel ve PDF export (randevular + müşteri listesi)
- Dinamik hizmet ekleme/çıkarma (işlem süresi dahil: 15–120 dk)
- İstatistik ekranı: personel performansı, müşteri davranış analizi
- Sistem log görüntüleyici: seviye ve işlem bazlı filtreleme

### Sistem

- **Akıllı çakışma kontrolü:** işlem süresi bazlı — 60 dk'lık randevu bitmeden yeni randevu açılmaz
- **Çalışma saati kısıtlaması:** personel tanımlı saatler dışına randevu alamaz
- **Tatil günü kısıtlaması:** tatil günleri randevu alınamaz
- **Kapsamlı loglama:** tüm kritik işlemler veritabanına kaydedilir
- **Responsive navigasyon:** offcanvas sidebar — her ekran boyutunda sorunsuz çalışır
- Validasyon: ad-soyad sadece harf, telefon sadece rakam (hem JS hem Python)
- Puan sistemi: başlangıç 100, zamanında gelme +10, gelmeme -20

---

## Proje Yapısı
=======
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

##  Proje Yapısı
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

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
<<<<<<< HEAD
│   ├── personel_routes.py          # Onay, reddet, gelme durumu, hatırlatma
=======
│   ├── personel_routes.py          # Onay, reddet, gelme durumu, hatırlatma, takvim
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
│   └── admin_routes.py             # Admin paneli, müşteri/personel yönetimi, loglar
│
├── utils/
│   ├── auth_helper.py              # SHA-256 hash, session kontrol fonksiyonları
│   ├── email_helper.py             # Gmail SMTP, HTML e-posta şablonları
│   ├── validators.py               # Form validasyonu, akıllı çakışma kontrolü
<<<<<<< HEAD
│   ├── export_helper.py            # Excel (openpyxl) + PDF (reportlab) export
│   └── logger.py                   # Sistem loglama modülü
│
└── templates/
    ├── base.html                   # Ana şablon — offcanvas sidebar navigasyon
=======
│   └── logger.py                   # Sistem loglama modülü
│
└── templates/
    ├── base.html                   # Ana şablon, navbar, flash mesajları
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
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

<<<<<<< HEAD
## Veritabanı Tasarımı

SQLite veritabanı (`randevu.db`) uygulama ilk çalıştığında **otomatik oluşturulur**. Elle SQL çalıştırmaya gerek yoktur.

### Tablo İlişki Özeti

```
musteriler ──────────────────────────────┐
                                          ├── randevular ── degerlendirmeler
personeller ─── personel_uzmanliklar     │
            ─── personel_calisma_saatleri┘
            ─── tatil_gunleri

loglar  (bağımsız)
hizmetler ── personel_uzmanliklar
```

### Tablo Detayları

#### `musteriler`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | Otomatik artan |
| ad_soyad | TEXT | Sadece harf |
| telefon | TEXT UNIQUE | Giriş kimliği, sadece rakam |
| email | TEXT | Bildirim için, opsiyonel |
| sifre_hash | TEXT | SHA-256 |
| puan | INTEGER | Başlangıç: 100 |
| gelmeme_sayisi | INTEGER | Toplam gelmeme sayacı |
| aktif | INTEGER | 0=banlı, 1=aktif |

#### `personeller`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | Otomatik artan |
| ad_soyad | TEXT | Personel tam adı |
| email | TEXT UNIQUE | Giriş kimliği |
| sifre_hash | TEXT | SHA-256 |
| rol | TEXT | 'personel' veya 'admin' |
| aktif | INTEGER | 0=pasif, 1=aktif |

#### `randevular`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| musteri_id | INTEGER FK | → musteriler.id |
| personel_id | INTEGER FK | → personeller.id |
| islem | TEXT | Yapılacak işlem adı |
| tarih | TEXT | YYYY-MM-DD |
| saat | TEXT | HH:MM |
| durum | TEXT | beklemede / onaylandi / reddedildi / tamamlandi / gelmedi |
| hatirlatma_gonderildi | INTEGER | 0=hayır, 1=evet (tek seferlik) |
| olusturma_tarihi | TEXT | Zaman damgası |

#### `degerlendirmeler`
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| randevu_id | INTEGER UNIQUE FK | Her randevu bir kez değerlendirilebilir |
| musteri_id | INTEGER FK | → musteriler.id |
| personel_id | INTEGER FK | → personeller.id |
| hizmet_puani | INTEGER | 1–5 |
| tutum_puani | INTEGER | 1–5 |
| sure_puani | INTEGER | 1–5 |
| yorum | TEXT | İsteğe bağlı |

#### `hizmetler`
=======

##  Kurulum
=======
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
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| ad | TEXT UNIQUE | Hizmet adı |
<<<<<<< HEAD
| sure_dakika | INTEGER | Çakışma kontrolünde kullanılır (varsayılan: 30) |
| aktif | INTEGER | 0=listede gösterilmez |

#### Diğer Tablolar

| Tablo | Amaç |
|-------|------|
| `personel_uzmanliklar` | Personel ↔ Hizmet many-to-many ilişkisi |
| `personel_calisma_saatleri` | Günlük çalışma başlangıç/bitiş saatleri (0=Pzt … 6=Paz) |
| `tatil_gunleri` | Sistem geneli veya personel bazlı tatil (personel_id NULL = sistem geneli) |
| `loglar` | Tüm kritik işlemlerin zaman damgalı kaydı |

---

## Kurulum

### 1. Gereksinimler

- Python 3.10+
- Gmail hesabı (SMTP için Uygulama Şifresi)

### 2. Bağımlılıkları Yükle

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. config.py Ayarla

```python
# config.py
MAIL_USERNAME = 'sizin@gmail.com'
MAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'   # Gmail Uygulama Şifresi (16 hane)
SECRET_KEY    = 'guclu-rastgele-anahtar-girin'
DATABASE      = 'randevu.db'
```

### 4. Çalıştır

```bash
python app.py
# → http://localhost:5000
```

Veritabanı ilk çalıştırmada otomatik oluşturulur.

### 5. Admin Girişi

```
URL    : http://localhost:5000/auth/personel-login
E-posta: admin@medicalpoint.com
Şifre  : admin123
```

### Gmail Uygulama Şifresi Alma

1. Google Hesabı → Güvenlik → **2 Adımlı Doğrulama**'yı etkinleştir
2. Güvenlik → **Uygulama Şifreleri** → "Posta" için şifre oluştur
3. Oluşturulan 16 karakterli kodu `config.py`'deki `MAIL_PASSWORD`'a yaz

---

## Kullanım Kılavuzu

### Müşteri Akışı

1. `/auth/kayit` → kayıt ol
2. `/auth/giris` → giriş yap
3. Sidebar → **Randevu Al** → hizmet, personel, tarih/saat seç
4. Personel onayladıktan sonra e-posta bildirimi gelir
5. Randevu sonrası Sidebar → **Randevularım** → değerlendirme yap

### Personel Akışı

1. `/auth/personel-login` → giriş yap
2. Sidebar → **Randevular** → beklemedeki randevuları onayla/reddet
3. Randevu günü hatırlatma e-postası gönder
4. **Tamamlandı** veya **Gelmedi** işaretle → müşteri puanı güncellenir

### Admin Akışı

1. `/auth/personel-login` → admin girişi
2. Sidebar → **Personeller** → personel ekle, uzmanlık ve çalışma saati ata
3. Sidebar → **Hizmetler** → hizmet tanımla, süre seç
4. Sidebar → **Tatil/İzin** → tatil günlerini tanımla
5. Sidebar → **Raporlar** → istatistikler ve logları izle

---

## Route Tablosu

### Auth

| Method | URL | Açıklama |
|--------|-----|----------|
| GET/POST | `/auth/giris` | Müşteri girişi |
=======
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


Tarayıcında şu adrese git:  
 **http://localhost:5000**
=======
Tarayıcıda aç: [http://localhost:5000](http://localhost:5000)


> Port meşgulse `app.py` içinde `port=5001` yap ve `http://localhost:5001` adresiyle dene.


##  Kullanım Kılavuzu
=======
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


##  Veritabanı Tasarımı

SQLite veritabanı (`randevu.db`) uygulama başladığında otomatik oluşturulur.

### Tablolar

#### `musteriler` (D1 - Müşteri Kayıtları)
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | Otomatik artan kimlik |
| ad_soyad | TEXT | Ad ve soyad |
| telefon | TEXT UNIQUE | Giriş için kullanılan numara |
| email | TEXT | Hatırlatma için (opsiyonel) |
| sifre_hash | TEXT | SHA-256 ile hash'lenmiş şifre |
| puan | INTEGER | Başlangıç: 100, +10/-20 değişir |
| gelmeme_sayisi | INTEGER | Kaç randevuya gelmedi |
| aktif | INTEGER | 1=aktif, 0=banlandı |

#### `randevular` (D2 - Randevu Veritabanı)
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| musteri_id | INTEGER FK | musteriler.id |
| personel_id | INTEGER FK | personeller.id |
| islem | TEXT | Yapılacak işlem adı |
| tarih | TEXT | YYYY-MM-DD formatı |
| saat | TEXT | HH:MM formatı |
| durum | TEXT | beklemede/onaylandi/reddedildi/tamamlandi/gelmedi |
| hatirlatma_gonderildi | INTEGER | 0=hayır, 1=evet |

#### `degerlendirmeler` (D6 - Dolu Değerlendirme Formları)
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| randevu_id | INTEGER UNIQUE | Her randevu 1 değerlendirme |
| hizmet_puani | INTEGER | 1-5 arası |
| tutum_puani | INTEGER | 1-5 arası |
| sure_puani | INTEGER | 1-5 arası |
| yorum | TEXT | İsteğe bağlı metin |

---

##  API Route Tablosu
=======
## 🌐 Route Tablosu

### Auth
>>>>>>> bd518f92eabaffbac0e90754026c59523601c257

| Method | URL | Açıklama |
|--------|-----|----------|
| GET/POST | `/auth/login` | Müşteri girişi |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
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
<<<<<<< HEAD
| GET | `/personel/randevular` | Randevu listesi |
=======
| GET | `/personel/randevular` | Randevu listesi (filtreli) |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
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
<<<<<<< HEAD
=======
| GET | `/admin/musteriler-indir/excel` | Müşteri listesi Excel indir |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
| POST | `/admin/musteri-durum/<id>` | Müşteri aktif/ban toggle |
| GET | `/admin/personeller` | Personel listesi |
| GET/POST | `/admin/personel-ekle` | Yeni personel ekle |
| GET/POST | `/admin/personel-calisma/<id>` | Haftalık çalışma saatleri |
| GET/POST | `/admin/tatil-gunleri` | Tatil/izin yönetimi |
| GET | `/admin/tum-randevular` | Tüm randevular |
<<<<<<< HEAD
| GET | `/admin/randevular-indir` | Excel / PDF export |
| GET | `/admin/istatistikler` | Performans raporları |
| GET/POST | `/admin/hizmetler` | Hizmet yönetimi |
=======
| GET | `/admin/istatistikler` | Performans raporları |
| GET/POST | `/admin/hizmetler` | Hizmet yönetimi |
| POST | `/admin/toplu-hatirlatma` | Toplu e-posta gönder |
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
| GET | `/admin/loglar` | Sistem log görüntüleyici |

---

<<<<<<< HEAD
## Güvenlik

### Şifre Hashleme

Tüm şifreler **SHA-256** ile hashlenerek saklanır:
=======
## 🔒 Güvenlik

### Şifre Hashleme

Tüm şifreler **SHA-256** ile hashlenerek saklanır. Düz metin şifre asla veritabanında bulunmaz.
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

```python
# utils/auth_helper.py
import hashlib

def hash_sifre(sifre: str) -> str:
    return hashlib.sha256(sifre.encode()).hexdigest()

def sifre_dogru_mu(sifre: str, hash_deger: str) -> bool:
    return hash_sifre(sifre) == hash_deger
```

### Session Yönetimi

<<<<<<< HEAD
Her rol için ayrı session kontrolü:

```python
def musteri_mi()  → session.get('kullanici_rol') == 'musteri'
def personel_mi() → session.get('kullanici_rol') in ('personel', 'admin')
def admin_mi()    → session.get('kullanici_rol') == 'admin'
=======
Her rol için ayrı session kontrolü yapılır:

```python
def musteri_mi()  → session.get('rol') == 'musteri'
def personel_mi() → session.get('rol') in ('personel', 'admin')
def admin_mi()    → session.get('rol') == 'admin'
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
```

### Form Validasyonu

<<<<<<< HEAD
İki katmanlı — hem JavaScript (anlık) hem Python (güvenli taraf):

- Ad-soyad: yalnızca harf ve boşluk
=======
İki katmanlı validasyon — hem JavaScript (anlık geri bildirim) hem Python (güvenli taraf):

- Ad-soyad: yalnızca harf ve boşluk (`^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$`)
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
- Telefon: yalnızca rakam, 10 hane
- E-posta: standart format kontrolü
- Şifre: minimum 6 karakter

### Yetkilendirme

<<<<<<< HEAD
Her blueprint'te `@giris_gerekli`, `@personel_giris_gerekli`, `@admin_gerekli` decorator'ları kullanılır. Yetkisiz erişimde otomatik yönlendirme ve log kaydı oluşur.

---

## Sistem Loglama

`utils/logger.py` tüm kritik olayları `loglar` tablosuna kaydeder.

### Log Seviyeleri

| Seviye | Kullanım |
|--------|----------|
| `INFO` | Normal işlemler: giriş, randevu alma |
| `AUDIT` | Yetkili işlemler: admin eylemleri, onay/red |
| `WARNING` | Başarısız giriş denemeleri |
| `ERROR` | Sistem hataları |

### Otomatik Loglanan İşlemler

-  Müşteri / personel giriş denemeleri (başarılı ve başarısız)
-  Randevu oluşturma, onaylama, reddetme, iptal, tamamlama
-  Admin: personel ekleme, çalışma saati, tatil ekleme/silme
-  Müşteri puan değişimleri
=======
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
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

### Kullanım Örneği

```python
from utils.logger import log_yaz, log_randevu, log_admin

<<<<<<< HEAD
log_yaz(islem='ozel_islem', detay='Açıklama', seviye='INFO')
log_randevu(eylem='onayla', randevu_id=42, detay='10:00 – Botoks')
log_admin(eylem='personel_ekle', detay='Ayşe Yılmaz eklendi')
```

> Loglama hiçbir zaman ana işlemi durdurmaz — hata oluşursa sessizce devam eder.

---

##  Geliştirme Notları

Bu proje bir öğrenci projesidir. Üretim ortamına taşımadan önce önerilen adımlar:

- [ ] SHA-256 → **bcrypt** şifreleme geçişi
- [ ] `SECRET_KEY` ortam değişkeninden oku (`.env` dosyası)
- [ ] SQLite → PostgreSQL geçişi (büyük ölçekli kullanım)
- [ ] Rate limiting ekle (brute-force koruması)
- [ ] HTTPS sertifikası (Let's Encrypt)
- [ ] CSRF koruması (Flask-WTF)

### Temel Kavramlar

| Kavram | Açıklama |
|--------|----------|
| **Blueprint** | Flask'ta route gruplamak için kullanılır |
| **MVC Benzeri Yapı** | `routes/` = Controller, `templates/` = View, `database.py` = Model |
| **Decorator** | `@giris_gerekli` gibi fonksiyon sarmalayıcıları |
| **Jinja2** | `{{ değişken }}` ve `{% if/for %}` template dili |
| **Session** | Kullanıcı giriş durumunu hatırlamak için şifreli cookie |
| **Offcanvas** | Bootstrap'in responsive yan panel bileşeni |

---

## Sık Sorulan Sorular

**S: randevu.db dosyası nerede oluşuyor?**  
A: Proje kök dizininde, `app.py` ile aynı klasörde oluşur.

**S: Veritabanını sıfırlamak istiyorum.**  
A: `randevu.db` dosyasını sil, uygulamayı yeniden başlat. Tablolar ve varsayılan admin otomatik yeniden oluşturulur.

**S: E-posta gönderilmiyor.**  
A: `config.py`'deki `MAIL_PASSWORD` Gmail şifren değil **Uygulama Şifresi** olmalıdır.
=======
# Genel log
log_yaz(islem='ozel_islem', detay='Açıklama', seviye='INFO')

# Randevu logu
log_randevu(eylem='onayla', randevu_id=42, detay='10:00 – Botoks')

# Admin logu
log_admin(eylem='personel_ekle', detay='Ayşe Yılmaz eklendi')
```

> Loglama hiçbir zaman ana işlemi durdurmaz. Hata oluşursa sessizce `print` yapar ve devam eder.

---

##  Sık Sorulan Sorular

**S: Randevu.db dosyası nerede oluşuyor?**  
A: Proje kök dizininde, `app.py` ile aynı klasörde oluşur.

**S: Veritabanını sıfırlamak istiyorum, ne yapmalıyım?**  
A: `randevu.db` dosyasını sil, uygulamayı yeniden başlat. Tablolar ve varsayılan admin yeniden oluşturulur.

**S: E-posta gönderilmiyor, ne yapmalıyım?**  
A: `config.py`'deki `MAIL_USERNAME` ve `MAIL_PASSWORD` değerlerini kontrol et. `MAIL_PASSWORD` Gmail şifren değil, **Uygulama Şifresi** olmalıdır.
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1

**S: 5000 portu meşgul hatası alıyorum.**  
A: `app.py` içinde `port=5001` yap ve `http://localhost:5001` adresine git.

**S: Personel randevu alırken görünmüyor.**  
<<<<<<< HEAD
A: Personelin ilgili hizmette **uzmanlığı** tanımlı olmalı. Admin → Personeller → uzmanlık checkbox'larını kontrol et.

**S: Randevu alırken saat seçenekleri boş geliyor.**  
A: Seçilen tarih personelin **çalışma saatleri** dışında veya **tatil günü** olarak tanımlı olabilir.

**S: Puan sistemi nasıl çalışıyor?**  
A: Başlangıç 100 puan. Zamanında gelince +10, gelmeyince -20. Puan hiçbir zaman 0'ın altına düşmez.

**S: Sidebar menü neden açılmıyor?**  
A: Bootstrap JS'in yüklendiğinden emin ol. Tarayıcı konsolunda (F12) hata var mı kontrol et. Sayfayı `Ctrl+Shift+R` ile hard refresh yap.

---

*Bu proje DFD tabanlı sistem analizi ve Python Flask geliştirme pratiği amacıyla oluşturulmuştur.*
=======
A: Personelin ilgili hizmette **uzmanlığı** tanımlı olmalı. Admin → Personel Ekle / Düzenle → uzmanlık checkbox'larını kontrol et.

**S: Randevu alırken saat seçenekleri neden boş?**  
A: Seçilen tarihin personelin **çalışma saatleri** dışında olması veya o tarihin **tatil günü** olarak tanımlı olması sebebiyle filtrelenmiş olabilir.

**S: Puan sistemi nasıl çalışıyor?**  
A: Başlangıç puanı 100. Randevuya zamanında gelince +10, gelmeyince -20 puan. Puan hiçbir zaman 0'ın altına düşmez. Admin panelinde müşteri puanları izlenebilir.

---


##  Kullanılan Teknolojiler
=======
## 📝 Geliştirme Notları
>>>>>>> bd518f92eabaffbac0e90754026c59523601c257

Bu proje bir öğrenci projesidir. Üretim ortamına taşımadan önce şu adımlar önerilir:

- [ ] SHA-256 → **bcrypt** şifreleme geçişi (`bcrypt` kütüphanesi)
- [ ] `SECRET_KEY` değerini ortam değişkeninden oku (`.env` dosyası)
- [ ] SQLite → PostgreSQL geçişi (büyük ölçekli kullanım için)
- [ ] Rate limiting ekle (brute-force koruması için)
- [ ] HTTPS sertifikası (Let's Encrypt)

---

<<<<<<< HEAD
##  Notlar

Bu projeyi incelerken dikkat etmen gereken kavramlar:

1. **MVC Benzeri Yapı:** `routes/` = Controller, `templates/` = View, `database.py` = Model
2. **Blueprint:** Flask'ta route gruplamak için kullanılır
3. **Decorator:** `@giris_gerekli` gibi fonksiyon sarmalayıcıları
4. **Jinja2:** `{{ değişken }}` ve `{% if/for %}` template dili
5. **Session:** Kullanıcının giriş durumunu hatırlamak için şifreli cookie
6. **Hash:** Şifreleri güvenli saklamak için tek yönlü dönüşüm
7. **SMTP:** E-posta protokolü, Gmail üzerinden kullanılır

---

*Güzellik Merkezi Randevu Sistemi Projesi*
=======
*Bu proje DFD tabanlı sistem analizi ve Python Flask geliştirme pratiği amacıyla oluşturulmuştur.*

>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
