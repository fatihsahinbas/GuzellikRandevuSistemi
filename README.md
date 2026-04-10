#  Randevu Yönetim Sistemi

> **Projesi** | Python Flask + SQLite + Bootstrap 5  
> Veri Akış Diyagramı (DFD) tabanlı randevu sistemi

---

##  İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [DFD ile Kod Eşleşmesi](#dfd-ile-kod-eşleşmesi)
- [Özellikler](#özellikler)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Kullanım Kılavuzu](#kullanım-kılavuzu)
- [Veritabanı Tasarımı](#veritabanı-tasarımı)
- [API Route Tablosu](#api-route-tablosu)
- [Güvenlik Önlemleri](#güvenlik-önlemleri)
- [Sık Sorulan Sorular](#sık-sorulan-sorular)

---

## 📖 Proje Hakkında

Bu proje, bir güzellik/sağlık kliniği için **randevu yönetim sistemi** geliştirmektedir.  
Sistem üç farklı kullanıcı rolüne hizmet eder:

| Rol | Açıklama |
|-----|----------|
|  **Müşteri** | Randevu alır, değerlendirme yapar, geçmişini görür |
|  **Personel** | Randevuları onaylar, gelme durumunu işler, değerlendirmeleri görür |
|  **Admin** | Tüm sistemi yönetir, istatistikleri izler, personel ekler |

---

##  DFD ile Kod Eşleşmesi

DFD diyagramındaki her işlem biriminin kod karşılığı:

| DFD İşlem | Açıklama | Kod Dosyası | Fonksiyon |
|-----------|----------|-------------|-----------|
| **1.0** | Kullanıcı Giriş Yapması | `routes/auth_routes.py` | `login_page()` |
| **2.0** | Randevu Talebi Oluştur | `routes/musteri_routes.py` | `randevu_al()` |
| **3.0** | Uygunlık Kontrolü | `routes/musteri_routes.py` | `randevu_al()` içinde |
| **4.0** | Onaylanan Randevu Kaydı | `routes/personel_routes.py` | `randevu_onayla()` |
| **5.0** | Randevu Bilgisi Hatırlatma | `routes/personel_routes.py` | `hatirlatma_gonder()` |
| **6.0** | Randevu Gelme Durumu | `routes/personel_routes.py` | `gelme_durumu_guncelle()` |
| **7.0** | Personel Değerlendirme İşlemi | `routes/personel_routes.py` | `degerlendirmelerim()` |
| **8.0** | Müşterinin Formu Doldurması | `routes/musteri_routes.py` | `degerlendirme_yap()` |

**Veri Depoları (D1-D6):**

| DFD Deposu | Açıklama | Veritabanı Tablosu |
|------------|----------|-------------------|
| **D1** | Müşteri Kayıtları | `musteriler` |
| **D2** | Randevu Veritabanı | `randevular` |
| **D3** | Onaylanan Randevu Bilgileri | `randevular` (durum='onaylandi') |
| **D4** | Personel Veritabanı | `personeller` |
| **D5** | Boş Değerlendirme Formları | `templates/musteri/degerlendirme.html` |
| **D6** | Dolu Değerlendirme Formları | `degerlendirmeler` |

---

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

---

##  Proje Yapısı

```
randevu_sistemi/
│
├── app.py                  # Flask uygulaması giriş noktası
├── config.py               # Ayarlar (secret key, mail, db)
├── database.py             # SQLite bağlantısı ve tablo oluşturma
├── requirements.txt        # Python paketleri
│
├── routes/                 # Blueprint'ler (URL grupları)
│   ├── __init__.py
│   ├── auth_routes.py      # Giriş / Kayıt / Çıkış
│   ├── musteri_routes.py   # Müşteri işlemleri
│   ├── personel_routes.py  # Personel işlemleri
│   └── admin_routes.py     # Admin paneli
│
├── utils/                  # Yardımcı araçlar
│   ├── __init__.py
│   ├── auth_helper.py      # Şifre hash, session yönetimi
│   ├── email_helper.py     # Gmail SMTP e-posta gönderimi
│   └── validators.py       # Form doğrulama fonksiyonları
│
└── templates/              # HTML şablonları (Jinja2)
    ├── base.html           # Ana şablon (navbar, footer)
    ├── auth/
    │   ├── login.html
    │   ├── kayit.html
    │   └── personel_login.html
    ├── musteri/
    │   ├── panel.html
    │   ├── randevu_al.html
    │   ├── randevularim.html
    │   └── degerlendirme.html
    ├── personel/
    │   ├── panel.html
    │   ├── randevular.html
    │   └── degerlendirmelerim.html
    └── admin/
        ├── panel.html
        ├── musteriler.html
        ├── personeller.html
        ├── personel_ekle.html
        ├── tum_randevular.html
        └── istatistikler.html
```

---

##  Kurulum

### 1. Gereksinimleri Karşıla

- **Python 3.10+** kurulu olmalı  
  → https://www.python.org/downloads/

- **pip** kurulu olmalı (Python ile birlikte gelir)

### 2. Projeyi İndir / Klonla

```bash
# ZIP ile indirdiysen klasöre gir:
cd randevu_sistemi

# veya git ile:
git clone <repo-url>
cd randevu_sistemi
```

### 3. Sanal Ortam Oluştur (Önerilir)

```bash
# Sanal ortam oluştur
python -m venv venv

# Aktifleştir (Windows)
venv\Scripts\activate

# Aktifleştir (Mac/Linux)
source venv/bin/activate
```

> **Sanal ortam nedir?** Projenin bağımlılıklarını sistemden izole eder.  
> Tıpkı her projeye ayrı bir "çanta" vermek gibi.

### 4. Bağımlılıkları Kur

```bash
pip install -r requirements.txt
```

### 5. E-posta Ayarları (Opsiyonel)

`config.py` dosyasını aç ve Gmail bilgilerini gir:

```python
MAIL_USERNAME = 'senin@gmail.com'
MAIL_PASSWORD = 'uygulama-sifresi'   # Gmail Uygulama Şifresi
```

> **Gmail Uygulama Şifresi nasıl oluşturulur?**
> 1. [myaccount.google.com](https://myaccount.google.com) → Güvenlik
> 2. 2 Adımlı Doğrulama'yı etkinleştir
> 3. Güvenlik → Uygulama şifreleri → Yeni oluştur
> 4. Oluşan 16 haneli şifreyi `MAIL_PASSWORD`'a yaz

### 6. Uygulamayı Başlat

```bash
python app.py
```

Tarayıcında şu adrese git:  
 **http://localhost:5000**

---

##  Kullanım Kılavuzu

### Müşteri Olarak Giriş

1. Ana sayfada **"Kayıt Ol"** butonuna tıkla
2. Ad-Soyad (yalnızca harf!), telefon (yalnızca rakam!), e-posta ve şifre gir
3. Giriş sayfasından **telefon + şifre** ile giriş yap
4. **"Randevu Al"** butonuyla yeni randevu oluştur:
   - İşlem seç → Personel seç → Tarih/Saat seç → Gönder
5. Randevu onaylandıktan sonra e-posta alırsın (e-posta girdiysen)
6. Tamamlanan randevuları **yıldız sistemiyle değerlendir**

### Personel Olarak Giriş

1. Alt kısımdaki **"Personel/Yönetici Girişi"** linkine tıkla
2. E-posta + şifre ile giriş yap
3. Bekleyen randevuları **onayla veya reddet**
4. Onayladıktan sonra müşteriye **hatırlatma e-postası** gönder
5. Randevu günü **"Geldi?"** butonuyla müşteri gelme durumunu kaydet

### Admin Olarak Giriş

**Varsayılan admin bilgileri:**
```
E-posta: admin@guzellikmerkezi.com
Şifre:   admin123
```
>  İlk girişten sonra şifreyi değiştirmeyi unutma!

1. Dashboard'dan sisteme genel bakış
2. **Personel Ekle** → Yeni çalışan hesabı oluştur
3. **Toplu Hatırlatma** → Yarınki tüm randevulara e-posta gönder
4. **Müşteriler** → Düşük puanlı müşterileri takip et, ban uygula

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

| Method | URL | Açıklama |
|--------|-----|----------|
| GET/POST | `/auth/login` | Müşteri girişi |
| GET/POST | `/auth/kayit` | Müşteri kaydı |
| GET/POST | `/auth/personel-login` | Personel/Admin girişi |
| GET | `/auth/cikis` | Çıkış |
| GET | `/musteri/panel` | Müşteri ana sayfası |
| GET/POST | `/musteri/randevu-al` | Randevu oluşturma |
| GET | `/musteri/randevularim` | Randevu listesi |
| GET/POST | `/musteri/degerlendirme/<id>` | Değerlendirme formu |
| POST | `/musteri/randevu-iptal/<id>` | Randevu iptali |
| GET | `/personel/panel` | Personel paneli |
| GET | `/personel/randevular` | Randevu listesi |
| POST | `/personel/onayla/<id>` | Randevu onaylama |
| POST | `/personel/reddet/<id>` | Randevu reddetme |
| POST | `/personel/gelme/<id>` | Gelme durumu güncelleme |
| POST | `/personel/hatirlatma/<id>` | E-posta gönderme |
| GET | `/personel/degerlendirmelerim` | Kendi değerlendirmeleri |
| GET | `/admin/panel` | Admin dashboard |
| GET | `/admin/musteriler` | Müşteri yönetimi |
| GET | `/admin/personeller` | Personel listesi |
| GET/POST | `/admin/personel-ekle` | Personel ekleme |
| GET | `/admin/tum-randevular` | Tüm randevular |
| GET | `/admin/istatistikler` | İstatistikler |
| POST | `/admin/toplu-hatirlatma` | Toplu e-posta |

---

##  Güvenlik Önlemleri

### Şifre Güvenliği
```python
# Şifre asla düz metin olarak saklanmaz!
# SHA-256 hash algoritması kullanılır
import hashlib
sifre_hash = hashlib.sha256(sifre.encode('utf-8')).hexdigest()
```

### Oturum Güvenliği
- Flask `session` nesnesi kullanılır
- `SECRET_KEY` ile imzalanır
- Rol bazlı erişim kontrolü (`@admin_gerekli`, `@giris_gerekli` decorator'ları)

### Form Doğrulama
- **Frontend (JavaScript):** Anlık geri bildirim
- **Backend (Python):** Güvenlik doğrulaması
- SQL Injection koruması: Parametreli sorgular (`?` placeholder)
- XSS koruması: Jinja2 otomatik HTML escape

### Özel Kurallar (DFD notlarından)
```
Ad-Soyad: Harf dışı karakter girilirse hata
Telefon: Sayı dışı karakter girilirse hata
Her iki kontrol hem JS hem Python'da uygulanır
```

---

##  Sık Sorulan Sorular

**S: E-posta gönderilmiyor, ne yapmalıyım?**  
C: `config.py`'deki `MAIL_USERNAME` ve `MAIL_PASSWORD` değerlerini kontrol et. Gmail'de "Uygulama Şifresi" oluşturman gerekiyor, normal şifren çalışmaz.

**S: `randevu.db` dosyası oluşmuyor?**  
C: `app.py`'yi doğru klasörden çalıştırdığından emin ol. Uygulama başladığında veritabanı otomatik oluşur.

**S: Admin şifremi unuttum?**  
C: `randevu.db` dosyasını sil, uygulama yeniden başlatıldığında varsayılan admin oluşturulur (`admin123`).

**S: Yeni işlem türü eklemek istiyorum?**  
C: `templates/admin/personel_ekle.html` dosyasındaki `<select>` listesine ekle. Personelin uzmanlık alanı = müşterinin seçeceği işlem.

**S: Şifre hash'i nasıl çalışıyor?**  
C: SHA-256 tek yönlü bir fonksiyondur. `"abc123"` → her zaman aynı hash üretir. Ama hash'ten `"abc123"`'e geri dönemezsin. Bu yüzden doğrulama için: girilen şifre hash'lenir ve veritabanındaki hash ile karşılaştırılır.

---

##  Kullanılan Teknolojiler

| Teknoloji | Sürüm | Kullanım Amacı |
|-----------|-------|----------------|
| Python | 3.10+ | Ana programlama dili |
| Flask | 3.0.0 | Web çerçevesi |
| SQLite | Dahili | Veritabanı |
| Bootstrap | 5.3.0 | Frontend UI |
| Bootstrap Icons | 1.10.0 | İkonlar |
| Jinja2 | Flask ile | HTML template motoru |
| smtplib | Dahili | E-posta gönderimi |

---

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
