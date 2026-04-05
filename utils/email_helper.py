"""
============================================================
 utils/email_helper.py  –  E-posta Gönderme Yardımcıları
============================================================
Gmail SMTP üzerinden e-posta gönderme işlemleri.

ANAHTAR KAVRAM – SMTP:
    SMTP (Simple Mail Transfer Protocol), e-posta göndermek
    için kullanılan protokoldür. Gmail'in SMTP sunucusuna
    bağlanıp "postacı" gibi mektup teslim ederiz.

ANAHTAR KAVRAM – TLS:
    Transport Layer Security – bağlantıyı şifreler.
    Port 587 ile Gmail'e güvenli bağlantı sağlarız.

KURULUM GEREKSİNİMİ:
    Gmail hesabında "Uygulama Şifresi" oluşturulmalı:
    myaccount.google.com → Güvenlik → Uygulama şifreleri
============================================================
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def email_gonder(alici: str, konu: str, html_icerik: str) -> bool:
    """
    Gmail SMTP üzerinden HTML e-posta gönderir.

    Args:
        alici       : Alıcı e-posta adresi
        konu        : E-posta konusu
        html_icerik : HTML formatlı e-posta içeriği

    Returns:
        True = başarılı, False = hata oluştu

    HATA YÖNETİMİ:
        Bağlantı hatası veya kimlik doğrulama hatası olursa
        False döndürür, uygulama çökmez.
    """
    try:
        # --------------------------------------------------
        # MIME mesajı oluştur (Multipurpose Internet Mail Extensions)
        # HTML ve düz metin birlikte göndermek için kullanılır
        # --------------------------------------------------
        mesaj = MIMEMultipart('alternative')
        mesaj['Subject'] = konu
        mesaj['From']    = current_app.config['MAIL_SENDER']
        mesaj['To']      = alici

        # HTML içeriği ekle
        html_kisim = MIMEText(html_icerik, 'html', 'utf-8')
        mesaj.attach(html_kisim)

        # --------------------------------------------------
        # Gmail SMTP'ye bağlan ve e-postayı gönder
        # --------------------------------------------------
        with smtplib.SMTP(
            current_app.config['MAIL_SERVER'],
            current_app.config['MAIL_PORT']
        ) as sunucu:
            sunucu.ehlo()                     # Sunucuya kendini tanıt
            sunucu.starttls()                 # Şifreli bağlantıya geç
            sunucu.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )
            sunucu.sendmail(
                current_app.config['MAIL_SENDER'],
                alici,
                mesaj.as_string()
            )

        print(f"✅ E-posta gönderildi: {alici}")
        return True

    except smtplib.SMTPAuthenticationError:
        # Gmail kimlik doğrulaması başarısız
        print("❌ E-posta hatası: Gmail kimlik bilgileri yanlış!")
        print("   config.py içindeki MAIL_USERNAME ve MAIL_PASSWORD'ü kontrol et.")
        return False

    except Exception as hata:
        # Diğer hatalar (ağ sorunu, sunucu hatası vb.)
        print(f"❌ E-posta gönderilemedi: {hata}")
        return False


def hatirlatma_emaili_olustur(musteri_adi: str, tarih: str,
                               saat: str, islem: str, personel: str) -> str:
    """
    Randevu hatırlatma e-postası için HTML içerik üretir.

    Args:
        musteri_adi : Müşteri adı soyadı
        tarih       : Randevu tarihi (YYYY-MM-DD)
        saat        : Randevu saati (HH:MM)
        islem       : Yapılacak işlem
        personel    : Personel adı

    Returns:
        HTML formatlı e-posta içeriği
    """
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
            .container {{
                max-width: 600px; margin: 20px auto;
                background: white; border-radius: 10px;
                padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: #e74c3c; color: white;
                padding: 20px; border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .bilgi-kutusu {{
                background: #f8f9fa; border-left: 4px solid #e74c3c;
                padding: 15px; margin: 20px 0; border-radius: 4px;
            }}
            .bilgi-satir {{ margin: 8px 0; color: #333; }}
            .bilgi-satir span {{ font-weight: bold; color: #e74c3c; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏥 Güzellik Merkezi</h2>
                <p>Randevu Hatırlatması</p>
            </div>
            <div style="padding: 20px;">
                <p>Sayın <strong>{musteri_adi}</strong>,</p>
                <p>Yarın bir randevunuz bulunmaktadır. Detaylar aşağıdadır:</p>

                <div class="bilgi-kutusu">
                    <div class="bilgi-satir">📅 Tarih: <span>{tarih}</span></div>
                    <div class="bilgi-satir">🕐 Saat: <span>{saat}</span></div>
                    <div class="bilgi-satir">💆 İşlem: <span>{islem}</span></div>
                    <div class="bilgi-satir">👤 Personel: <span>{personel}</span></div>
                </div>

                <p>Randevunuza zamanında gelmenizi rica ederiz.</p>
                <p>Randevunuzu iptal etmek istiyorsanız lütfen bizi arayın.</p>
            </div>
            <div class="footer">
                <p>Güzellik Merkezi Randevu Sistemi &copy; 2024</p>
            </div>
        </div>
    </body>
    </html>
    """


def randevu_onay_emaili_olustur(musteri_adi: str, tarih: str,
                                  saat: str, islem: str) -> str:
    """
    Randevu onaylandığında gönderilecek e-posta içeriğini üretir.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
            .container {{
                max-width: 600px; margin: 20px auto;
                background: white; border-radius: 10px; padding: 30px;
            }}
            .header {{ background: #27ae60; color: white; padding: 20px;
                        text-align: center; border-radius: 8px; }}
            .bilgi {{ background: #f0fff4; border: 1px solid #27ae60;
                      padding: 15px; border-radius: 8px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>✅ Randevunuz Onaylandı!</h2>
            </div>
            <p>Sayın <strong>{musteri_adi}</strong>,</p>
            <div class="bilgi">
                <p>📅 <strong>Tarih:</strong> {tarih}</p>
                <p>🕐 <strong>Saat:</strong> {saat}</p>
                <p>💆 <strong>İşlem:</strong> {islem}</p>
            </div>
            <p>Randevunuz başarıyla onaylanmıştır. Sizi bekliyoruz!</p>
        </div>
    </body>
    </html>
    """
def sifre_sifirlama_emaili_olustur(musteri_adi: str, reset_link: str) -> str:
    """
    Şifre sıfırlama e-postası HTML içeriği üretir.

    Args:
        musteri_adi : Müşteri adı
        reset_link  : Sıfırlama linki (token içerir)
    """
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
            .container {{
                max-width: 600px; margin: 20px auto;
                background: white; border-radius: 10px; padding: 30px;
            }}
            .header {{ background: #dc3545; color: white;
                       padding: 20px; border-radius: 8px; text-align: center; }}
            .btn {{
                display: inline-block; padding: 12px 30px;
                background: #dc3545; color: white; text-decoration: none;
                border-radius: 6px; font-size: 16px; margin: 20px 0;
            }}
            .uyari {{ color: #999; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔐 Şifre Sıfırlama</h2>
            </div>
            <p>Sayın <strong>{musteri_adi}</strong>,</p>
            <p>Şifrenizi sıfırlamak için aşağıdaki butona tıklayın:</p>

            <div style="text-align: center;">
                <a href="{reset_link}" class="btn">Şifremi Sıfırla</a>
            </div>

            <p class="uyari">
                ⚠️ Bu link <strong>1 saat</strong> geçerlidir.<br>
                Eğer bu talebi siz yapmadıysanız bu e-postayı görmezden gelin.
            </p>
        </div>
    </body>
    </html>
    """
    
def iptal_emaili_olustur(musteri_adi: str, tarih: str,
                          saat: str, islem: str, personel: str) -> str:
    """
    Randevu iptali için müşteriye gönderilecek HTML e-posta içeriğini üretir.

    Args:
        musteri_adi : Müşteri adı soyadı
        tarih       : İptal edilen randevu tarihi (YYYY-MM-DD)
        saat        : İptal edilen randevu saati (HH:MM)
        islem       : İptal edilen işlem adı
        personel    : Atanmış personel adı

    Returns:
        HTML formatlı e-posta içeriği (str)
    """
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
            .container {{
                max-width: 600px; margin: 20px auto;
                background: white; border-radius: 10px;
                padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: #c0392b; color: white;
                padding: 20px; border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .bilgi-kutusu {{
                background: #fff5f5; border-left: 4px solid #c0392b;
                padding: 15px; margin: 20px 0; border-radius: 4px;
            }}
            .bilgi-satir {{ margin: 8px 0; color: #333; }}
            .bilgi-satir span {{ font-weight: bold; color: #c0392b; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏥 MedicalPoint</h2>
                <p>Randevu İptal Bildirimi</p>
            </div>
            <div style="padding: 20px;">
                <p>Sayın <strong>{musteri_adi}</strong>,</p>
                <p>Aşağıdaki randevunuz <strong>iptal edilmiştir</strong>.</p>

                <div class="bilgi-kutusu">
                    <div class="bilgi-satir">📅 Tarih: <span>{tarih}</span></div>
                    <div class="bilgi-satir">🕐 Saat: <span>{saat}</span></div>
                    <div class="bilgi-satir">💅 İşlem: <span>{islem}</span></div>
                    <div class="bilgi-satir">👤 Personel: <span>{personel}</span></div>
                </div>

                <p>Yeni bir randevu almak isterseniz sitemizi ziyaret edebilirsiniz.</p>
                <p>İyi günler dileriz.</p>
            </div>
            <div class="footer">
                <p>MedicalPoint | Bu e-posta otomatik olarak gönderilmiştir.</p>
            </div>
        </div>
    </body>
    </html>
    """