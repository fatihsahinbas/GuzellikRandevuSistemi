"""
============================================================
 database.py  –  Veritabanı Yönetimi
============================================================
SQLite bağlantısı ve tablo oluşturma işlemleri burada.

ANAHTAR KAVRAM – SQLite:
    SQLite, tek bir .db dosyasına kaydeden hafif bir
    veritabanıdır. Sunucu gerektirmez. Tıpkı bir Excel
    dosyası gibi düşün ama SQL sorguları ile çalışır.

ANAHTAR KAVRAM – g nesnesi:
    Flask'ın g (global) nesnesi, bir HTTP isteği boyunca
    veri taşımak için kullanılır. İstek bitince temizlenir.
    Tıpkı bir garsonun sipariş defteri gibi – her masada
    (her istek) yeniden başlar.
============================================================
"""

import sqlite3
from flask import g, current_app


def get_db():
    """
    Veritabanı bağlantısını döndürür.

    Aynı istek içinde ikinci kez çağrılırsa yeni bağlantı
    açmaz, mevcut bağlantıyı (g.db) geri döndürür.
    Bu, performans açısından önemlidir.
    """
    if 'db' not in g:
        # Bağlantıyı aç ve satırları dict gibi okuyabilmek için
        # row_factory ayarını yap
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Row nesnesini dict gibi kullanmamızı sağlar
        # Örnek: row['ad_soyad'] şeklinde erişim
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    İstek sonunda veritabanı bağlantısını kapatır.
    Flask otomatik olarak bu fonksiyonu çağırır.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Veritabanı tablolarını oluşturur.
    Tablolar zaten varsa 'IF NOT EXISTS' sayesinde hata vermez.

    TABLOLAR:
    ─────────────────────────────────────────────────────────
    musteriler     → Müşteri kayıtları (D1)
    personeller    → Personel veritabanı (D4)
    randevular     → Randevu veritabanı (D2)
    degerlendirmeler → Dolu değerlendirme formları (D6)
    ─────────────────────────────────────────────────────────
    """
    from flask import current_app
    db = sqlite3.connect(current_app.config['DATABASE'])

    # -------------------------------------------------------
    # TABLO 1: musteriler (D1 - Müşteri Kayıtları)
    # DFD'de: ad-soyad, telefon, puan bilgileri tutulur
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS musteriler (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad    TEXT    NOT NULL,          -- Müşteri adı ve soyadı
            telefon     TEXT    NOT NULL UNIQUE,   -- Benzersiz telefon numarası
            email       TEXT,                      -- E-posta (hatırlatma için)
            sifre_hash  TEXT    NOT NULL,          -- Şifre (hash'lenmiş)
            puan        INTEGER DEFAULT 100,       -- Başlangıç puanı 100
            gelmeme_sayisi INTEGER DEFAULT 0,      -- Kaç randevuya gelmedi
            kayit_tarihi TEXT DEFAULT (datetime('now')),
            aktif       INTEGER DEFAULT 1          -- 0=pasif, 1=aktif
        )
    ''')

    # -------------------------------------------------------
    # TABLO 2: personeller (D4 - Personel Veritabanı)
    # DFD'de: personel ismi, yaptığı işlem bilgileri
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS personeller (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad    TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            sifre_hash  TEXT    NOT NULL,
            uzmanlik    TEXT    NOT NULL,          -- Yaptığı işlem (botoks, saç vb.)
            rol         TEXT    DEFAULT 'personel', -- 'personel' veya 'admin'
            aktif       INTEGER DEFAULT 1
        )
    ''')

    # -------------------------------------------------------
    # TABLO 3: randevular (D2 - Randevu Veritabanı)
    # DFD'de: yapılacak işlem, işlemi yapan personel,
    #         tarih ve saat bilgileri tutulur
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS randevular (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            musteri_id      INTEGER NOT NULL,
            personel_id     INTEGER NOT NULL,
            islem           TEXT    NOT NULL,       -- Yapılacak işlem
            tarih           TEXT    NOT NULL,       -- YYYY-MM-DD formatı
            saat            TEXT    NOT NULL,       -- HH:MM formatı
            durum           TEXT    DEFAULT 'beklemede',
                -- 'beklemede' | 'onaylandi' | 'reddedildi' | 'tamamlandi' | 'gelmedi'
            hatirlatma_gonderildi INTEGER DEFAULT 0, -- 0=hayır, 1=evet
            olusturma_tarihi TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (musteri_id)  REFERENCES musteriler(id),
            FOREIGN KEY (personel_id) REFERENCES personeller(id)
        )
    ''')

    # -------------------------------------------------------
    # TABLO 4: degerlendirmeler (D5/D6 - Değerlendirme Formları)
    # DFD'de 7.0 ve 8.0: Personel değerlendirme işlemi
    # Müşteri hizmet kalitesi, personel tutumu vb. değerlendirir
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS degerlendirmeler (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            randevu_id      INTEGER NOT NULL UNIQUE, -- Her randevu 1 değerlendirme
            musteri_id      INTEGER NOT NULL,
            personel_id     INTEGER NOT NULL,
            hizmet_puani    INTEGER NOT NULL,        -- 1-5 arası
            tutum_puani     INTEGER NOT NULL,        -- 1-5 arası
            sure_puani      INTEGER NOT NULL,        -- 1-5 arası
            yorum           TEXT,
            olusturma_tarihi TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (randevu_id)  REFERENCES randevular(id),
            FOREIGN KEY (musteri_id)  REFERENCES musteriler(id),
            FOREIGN KEY (personel_id) REFERENCES personeller(id)
        )
    ''')
    
    # TABLO 5: hizmetler (Admin tarafından yönetilen işlem listesi)
    db.execute('''
        CREATE TABLE IF NOT EXISTS hizmetler (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ad            TEXT NOT NULL UNIQUE,
            sure_dakika   INTEGER DEFAULT 30,   -- İşlem süresi (dk): 30, 45, 60, 90...
            aktif         INTEGER DEFAULT 1
        )
    ''')
    
    # TABLO: sifre_sifirlama tokenları
    db.execute('''
        CREATE TABLE IF NOT EXISTS sifre_sifirlama (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            musteri_id  INTEGER NOT NULL,
            token       TEXT NOT NULL UNIQUE,
            son_kullanim TEXT NOT NULL,  -- Token geçerlilik süresi
            kullanildi  INTEGER DEFAULT 0,
            FOREIGN KEY (musteri_id) REFERENCES musteriler(id)
        )
    ''')

    # -------------------------------------------------------
    # TABLO 5: personel_uzmanliklar
    # Personel ↔ Hizmet çoka-çok ilişkisi
    # Analoji: Bir doktorun birden fazla branşı olabilir,
    #          bir branşta birden fazla doktor çalışabilir.
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS personel_uzmanliklar (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            personel_id INTEGER NOT NULL,
            hizmet_id   INTEGER NOT NULL,
            UNIQUE(personel_id, hizmet_id),              -- Aynı kombinasyon 2 kez girilemesin
            FOREIGN KEY (personel_id) REFERENCES personeller(id),
            FOREIGN KEY (hizmet_id)   REFERENCES hizmetler(id)
        )
    ''')

    # -------------------------------------------------------
    # TABLO 6: personel_calisma_saatleri
    # Her personel için gün bazlı çalışma aralığı.
    # gun: 0=Pazartesi, 1=Salı, ... 6=Pazar (Python weekday())
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS personel_calisma_saatleri (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            personel_id     INTEGER NOT NULL,
            gun             INTEGER NOT NULL,   -- 0-6 arası
            baslangic_saat  TEXT NOT NULL,      -- HH:MM
            bitis_saat      TEXT NOT NULL,      -- HH:MM
            UNIQUE(personel_id, gun),
            FOREIGN KEY (personel_id) REFERENCES personeller(id)
        )
    ''')

    # -------------------------------------------------------
    # TABLO 7: tatil_gunleri
    # Personel bazlı veya sistem geneli tatil/izin günleri.
    # personel_id NULL ise sistem geneli (resmi tatil vb.)
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS tatil_gunleri (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            personel_id INTEGER,                -- NULL = tüm sistem için
            tarih       TEXT NOT NULL,          -- YYYY-MM-DD
            aciklama    TEXT,                   -- "Kurban Bayramı", "Yıllık İzin" vb.
            FOREIGN KEY (personel_id) REFERENCES personeller(id)
        )
    ''')

    # -------------------------------------------------------
    # TABLO 8: loglar
    # Sistem olaylarının kaydı — kim, ne zaman, ne yaptı.
    # -------------------------------------------------------
    db.execute('''
        CREATE TABLE IF NOT EXISTS loglar (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            zaman       TEXT DEFAULT (datetime('now')),
            seviye      TEXT DEFAULT 'INFO',    -- INFO | WARNING | ERROR | AUDIT
            kullanici   TEXT,                   -- ad_soyad veya 'sistem'
            rol         TEXT,                   -- musteri | personel | admin | sistem
            islem       TEXT NOT NULL,          -- Kısa eylem açıklaması
            detay       TEXT,                   -- JSON veya uzun açıklama
            ip_adresi   TEXT
        )
    ''')

    db.commit()

    # -------------------------------------------------------
    # Varsayılan admin hesabı oluştur (ilk kurulumda)
    # -------------------------------------------------------
    _create_default_admin(db)

    db.close()


def _create_default_admin(db):
    """
    İlk kurulumda varsayılan admin hesabı ekler.
    Admin zaten varsa hiçbir şey yapmaz.

    Varsayılan giriş: admin@guzellikmerkezi.com / admin123
    UYARI: Üretimde bu şifreyi hemen değiştir!
    """
    import hashlib

    # Admin var mı kontrol et
    cursor = db.execute(
        "SELECT id FROM personeller WHERE rol = 'admin' LIMIT 1"
    )
    if cursor.fetchone():
        return  # Zaten var, işlem yapma

    # Şifreyi SHA-256 ile hash'le
    sifre_hash = hashlib.sha256('admin123'.encode()).hexdigest()

    db.execute('''
        INSERT INTO personeller (ad_soyad, email, sifre_hash, uzmanlik, rol)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Sistem Yöneticisi', 'admin@guzellikmerkezi.com', sifre_hash, 'Yönetim', 'admin'))

    db.commit()
    print("✅ Varsayılan admin oluşturuldu: admin@guzellikmerkezi.com / admin123")
