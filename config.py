"""
============================================================
 config.py  –  Uygulama Ayarları
============================================================
Tüm sabit değerler ve hassas bilgiler burada tutulur.
Gerçek bir projede bu değerler .env dosyasından okunur.

ÖNEMLİ: SECRET_KEY'i asla GitHub'a yükleme!
============================================================
"""

import os

class Config:
    """
    Flask uygulama konfigürasyonu.
    os.environ.get() → önce çevre değişkenine bakar,
    bulamazsa ikinci parametredeki varsayılanı kullanır.
    """

    # --------------------------------------------------
    # Güvenlik anahtarı – session ve cookie şifrelemesi için
    # Üretimde rastgele uzun bir string olmalı!
    # --------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gizli-anahtar-2024-degistir')

    # --------------------------------------------------
    # Veritabanı dosyasının yolu
    # --------------------------------------------------
    DATABASE = os.environ.get('DATABASE', 'randevu.db')

    # --------------------------------------------------
    # E-posta (Gmail SMTP) ayarları
    # Gmail'de "Uygulama Şifresi" oluşturman gerekiyor:
    # Google Hesabı → Güvenlik → 2 Adımlı Doğrulama → Uygulama Şifreleri
    # --------------------------------------------------
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587          # TLS portu
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'senin@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'uygulama-sifresi')
    MAIL_SENDER   = os.environ.get('MAIL_USERNAME', 'senin@gmail.com')

    # --------------------------------------------------
    # Uygulama genel ayarları
    # --------------------------------------------------
    # Randevu kaç dakika önce hatırlatma gönderilsin?
    REMINDER_HOURS_BEFORE = 24

    # Müşteri kaç randevu kaçırırsa kara listeye alınsın?
    MAX_NO_SHOW = 3
