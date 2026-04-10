"""
============================================================
 utils/logger.py  –  Sistem Loglama Modülü
============================================================
Tüm kritik olayları veritabanına kaydeder.

Analoji: Bir güvenlik kamerası gibi düşün.
    Her önemli hareket (giriş, randevu, iptal, hata) kaydedilir.
    Kamera görüntüleri (loglar) sonradan incelenebilir.

SEVİYELER:
    INFO   → Normal işlemler (giriş, randevu alma)
    AUDIT  → Yetkili işlemler (admin eylemleri)
    WARNING→ Dikkat gerektiren durumlar (başarısız giriş)
    ERROR  → Sistem hataları

KULLANIM:
    from utils.logger import log_yaz
    log_yaz(islem='randevu_al', detay='10:00 saati seçildi', seviye='INFO')
============================================================
"""

from flask import session, request


def log_yaz(islem: str, detay: str = '',
            seviye: str = 'INFO', kullanici: str = '',
            rol: str = ''):
    """
    Bir sistem olayını loglar tablosuna kaydeder.

    Flask uygulama bağlamı içinde çağrılmalıdır (route içinde).

    Args:
        islem     : Kısa eylem kodu, örn: 'randevu_al', 'giris_basarisiz'
        detay     : Uzun açıklama veya JSON string (opsiyonel)
        seviye    : 'INFO' | 'AUDIT' | 'WARNING' | 'ERROR'
        kullanici : Zorunlu değil, session'dan otomatik alınır
        rol       : Zorunlu değil, session'dan otomatik alınır
    """
    try:
        from database import get_db

        # Kullanıcı bilgisini session'dan al (parametre verilmemişse)
        if kullanici is None:
            kullanici = session.get('kullanici_adi', 'anonim')
        if rol is None:
            rol = session.get('rol', 'anonim')

        # İstemci IP'si — proxy arkasındaysa X-Forwarded-For başlığına bak
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        db = get_db()
        db.execute('''
            INSERT INTO loglar (seviye, kullanici, rol, islem, detay, ip_adresi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (seviye, kullanici, rol, islem, detay, ip))
        db.commit()

    except Exception as hata:
        # Loglama hiçbir zaman ana işlemi durdurmamalı!
        # Sessizce hata yazdır, uygulamayı çökertme.
        print(f"[LOGGER HATA] {hata}")


def log_giris(basarili: bool, kullanici_adi: str, rol: str = 'musteri'):
    """
    Giriş denemesini loglar. Başarısız girişler WARNING seviyesinde.

    Args:
        basarili      : True = başarılı giriş, False = hatalı şifre/kullanıcı
        kullanici_adi : Telefon numarası veya e-posta
        rol           : 'musteri' veya 'personel'
    """
    if basarili:
        log_yaz(
            islem='giris_basarili',
            detay=f'{kullanici_adi} girişi başarılı',
            seviye='INFO',
            kullanici=kullanici_adi,
            rol=rol
        )
    else:
        log_yaz(
            islem='giris_basarisiz',
            detay=f'{kullanici_adi} için hatalı giriş denemesi',
            seviye='WARNING',
            kullanici=kullanici_adi,
            rol=rol
        )


def log_randevu(eylem: str, randevu_id: int, detay: str = ''):
    """
    Randevuyla ilgili olayları loglar.

    Args:
        eylem      : 'olustur' | 'onayla' | 'reddet' | 'iptal' | 'tamamla'
        randevu_id : İlgili randevu ID'si
        detay      : Ek bilgi
    """
    log_yaz(
        islem=f'randevu_{eylem}',
        detay=f'Randevu #{randevu_id} — {detay or ""}',
        seviye='AUDIT' if eylem in ('onayla', 'reddet', 'tamamla') else 'INFO'
    )


def log_admin(eylem: str, detay: str = ''):
    """
    Admin işlemlerini AUDIT seviyesinde loglar.
    Admin eylemleri her zaman izlenmelidir.
    """
    log_yaz(islem=f'admin_{eylem}', detay=detay, seviye='AUDIT')