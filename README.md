#  Güzellik Merkezi Randevu Yönetim Sistemi

> Veri Akış Diyagramı (DFD) tabanlı, tam özellikli randevu yönetim sistemi

---

##  İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Teknoloji Yığını](#-teknoloji-yığını)
- [DFD ile Kod Eşleşmesi](#-dfd-ile-kod-eşleşmesi)
- [Özellikler](#-özellikler)
- [Proje Yapısı](#-proje-yapısı)
- [Veritabanı Tasarımı](#️-veritabanı-tasarımı)
- [Kurulum](#-kurulum)
- [Kullanım Kılavuzu](#-kullanım-kılavuzu)
- [Route Tablosu](#-route-tablosu)
- [Güvenlik](#-güvenlik)
- [Sistem Loglama](#-sistem-loglama)
- [Geliştirme Notları](#-geliştirme-notları)
- [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

##  Proje Hakkında

Bu proje, bir güzellik merkezi için **uçtan uca randevu yönetim sistemi** sunar. Müşteri randevu alma, personel onay ve takvim yönetimi, admin raporlama ve loglama gibi tüm süreçleri kapsar.

| Rol | Açıklama |
|-----|----------|
| 👤 **Müşteri** | Randevu alır, değerlendirme yapar, geçmişini görür |
| 👩‍💼 **Personel** | Randevuları onaylar, gelme durumunu işler, değerlendirmeleri görür |
| 🛠 **Admin** | Tüm sistemi yönetir, istatistikleri izler, personel ekler |

---

## 🛠 Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+ / Flask 3.0 |
| Veritabanı | SQLite (`randevu.db`) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Navigasyon | Offcanvas Sidebar (responsive, tüm ekran boyutları) |
| E-posta | Gmail SMTP (`smtplib`) |
| Şifreleme | SHA-256 (`hashlib`) |
| Export | openpyxl (Excel) + reportlab (PDF) |

---

## 🗺 DFD ile Kod Eşleşmesi

Projede kullanılan DFD (Veri Akış Diyagramı) her bir süreç numarasıyla birebir eşleşmektedir:

| DFD Süreci | Açıklama | Kod Konumu |
|-----------|----------|------------|
| **1.0** | Kullanıcı Giriş Yapması | `routes/auth_routes.py` → `login_page()` |
| **2.0** | Randevu Talebi Oluştur | `routes/musteri_routes.py` → `randevu_al()` |
| **3.0** | Uygunluk Kontrolü | `utils/validators.py` → `cakisma_var_mi()` |
| **4.0** | Onaylanan Randevu Kaydı | `routes/personel_routes.py` → `randevu_onayla()` |
| **5.0** | Randevu Bilgisi Hatırlatma | `routes/personel_routes.py` → `hatirlatma_gonder()` |
| **6.0** | Randevu Gelme Durumu | `routes/personel_routes.py` → `gelme_durumu_guncelle()` |
| **7.0** | Personel Değerlendirme İşlemi | `routes/admin_routes.py` + personel paneli |
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

##  Özellikler

###  Müşteri

- Telefon + şifre ile kayıt ve giriş
- Şifre sıfırlama (telefon numarasıyla)
- Profil güncelleme (ad-soyad, telefon, e-posta)
- İşlem, personel ve tarih/saat seçerek randevu alma (tek sayfada)
- Randevularını liste görünümünde takip etme
- Beklemedeki randevuyu iptal etme → otomatik e-posta bildirimi
- Tamamlanan randevular için personel değerlendirmesi (hizmet / tutum / süre, 1–5 yıldız)

###  Personel

- E-posta + şifre ile giriş
- Şifre değiştirme
- Kendi randevularını listeleme ve filtreleme
- Randevu onaylama / reddetme
- Müşteri gelme durumu işaretleme (geldi / gelmedi) → puan güncelleme
- Randevu hatırlatma e-postası gönderme (tek seferlik)
- Değerlendirmelerini görüntüleme ve ortalama puan takibi

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
│   ├── personel_routes.py          # Onay, reddet, gelme durumu, hatırlatma
│   └── admin_routes.py             # Admin paneli, müşteri/personel yönetimi, loglar
│
├── utils/
│   ├── auth_helper.py              # SHA-256 hash, session kontrol fonksiyonları
│   ├── email_helper.py             # Gmail SMTP, HTML e-posta şablonları
│   ├── validators.py               # Form validasyonu, akıllı çakışma kontrolü
│   ├── export_helper.py            # Excel (openpyxl) + PDF (reportlab) export
│   └── logger.py                   # Sistem loglama modülü
│
└── templates/
    ├── base.html                   # Ana şablon — offcanvas sidebar navigasyon
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
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | INTEGER PK | - |
| ad | TEXT UNIQUE | Hizmet adı |
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
| GET | `/personel/randevular` | Randevu listesi |
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
| POST | `/admin/musteri-durum/<id>` | Müşteri aktif/ban toggle |
| GET | `/admin/personeller` | Personel listesi |
| GET/POST | `/admin/personel-ekle` | Yeni personel ekle |
| GET/POST | `/admin/personel-calisma/<id>` | Haftalık çalışma saatleri |
| GET/POST | `/admin/tatil-gunleri` | Tatil/izin yönetimi |
| GET | `/admin/tum-randevular` | Tüm randevular |
| GET | `/admin/randevular-indir` | Excel / PDF export |
| GET | `/admin/istatistikler` | Performans raporları |
| GET/POST | `/admin/hizmetler` | Hizmet yönetimi |
| GET | `/admin/loglar` | Sistem log görüntüleyici |

---

## Güvenlik

### Şifre Hashleme

Tüm şifreler **SHA-256** ile hashlenerek saklanır:

```python
# utils/auth_helper.py
import hashlib

def hash_sifre(sifre: str) -> str:
    return hashlib.sha256(sifre.encode()).hexdigest()

def sifre_dogru_mu(sifre: str, hash_deger: str) -> bool:
    return hash_sifre(sifre) == hash_deger
```

### Session Yönetimi

Her rol için ayrı session kontrolü:

```python
def musteri_mi()  → session.get('kullanici_rol') == 'musteri'
def personel_mi() → session.get('kullanici_rol') in ('personel', 'admin')
def admin_mi()    → session.get('kullanici_rol') == 'admin'
```

### Form Validasyonu

İki katmanlı — hem JavaScript (anlık) hem Python (güvenli taraf):

- Ad-soyad: yalnızca harf ve boşluk
- Telefon: yalnızca rakam, 10 hane
- E-posta: standart format kontrolü
- Şifre: minimum 6 karakter

### Yetkilendirme

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

### Kullanım Örneği

```python
from utils.logger import log_yaz, log_randevu, log_admin

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

**S: 5000 portu meşgul hatası alıyorum.**  
A: `app.py` içinde `port=5001` yap ve `http://localhost:5001` adresine git.

**S: Personel randevu alırken görünmüyor.**  
A: Personelin ilgili hizmette **uzmanlığı** tanımlı olmalı. Admin → Personeller → uzmanlık checkbox'larını kontrol et.

**S: Randevu alırken saat seçenekleri boş geliyor.**  
A: Seçilen tarih personelin **çalışma saatleri** dışında veya **tatil günü** olarak tanımlı olabilir.

**S: Puan sistemi nasıl çalışıyor?**  
A: Başlangıç 100 puan. Zamanında gelince +10, gelmeyince -20. Puan hiçbir zaman 0'ın altına düşmez.

**S: Sidebar menü neden açılmıyor?**  
A: Bootstrap JS'in yüklendiğinden emin ol. Tarayıcı konsolunda (F12) hata var mı kontrol et. Sayfayı `Ctrl+Shift+R` ile hard refresh yap.

---

*Bu proje DFD tabanlı sistem analizi ve Python Flask geliştirme pratiği amacıyla oluşturulmuştur.*