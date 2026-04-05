"""
============================================================
 routes/auth_routes.py  –  Kimlik Doğrulama Route'ları
============================================================
Giriş, kayıt ve çıkış işlemleri bu blueprint'te yönetilir.

KAPSANAN İŞLEMLER:
    GET  /auth/login        → Giriş sayfasını göster
    POST /auth/login        → Giriş formunu işle
    GET  /auth/kayit        → Kayıt sayfasını göster
    POST /auth/kayit        → Kayıt formunu işle
    GET  /auth/cikis        → Oturumu kapat

ANAHTAR KAVRAM – GET vs POST:
    GET  = "Bana veri göster" (sayfa açmak gibi)
    POST = "Bu veriyi işle"   (form göndermek gibi)
============================================================
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from database import get_db
from utils.auth_helper import (hash_sifre, sifre_dogru_mu,
                                musteri_giris_yap, personel_giris_yap)
from utils.validators import (ad_soyad_gecerli_mi, telefon_gecerli_mi,
                               sifre_gecerli_mi, email_gecerli_mi)

# Blueprint oluştur; name='auth' → url_for('auth.login_page') şeklinde kullanılır
auth_bp = Blueprint('auth', __name__)


# ==============================================================
# MÜŞTERİ GİRİŞ / KAYIT
# ==============================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """
    Müşteri giriş sayfası.

    GET:  Boş giriş formunu göster.
    POST: Telefon + şifre ile doğrulama yap.

    DFD 1.0: Kullanıcı Giriş Yapması
    Giriş bilgileri: Ad-Soyad + Telefon (DFD'ye göre)
    Biz sistemi geliştirerek telefon + şifre kullandık.
    """
    # Zaten giriş yapmışsa yönlendir
    if 'kullanici_rol' in session:
        return _rol_yonlendir(session['kullanici_rol'])

    if request.method == 'POST':
        # Form verilerini al (strip() = baştaki/sondaki boşlukları temizle)
        telefon = request.form.get('telefon', '').strip()
        sifre   = request.form.get('sifre', '').strip()

        # Boşluk kontrolü
        if not telefon or not sifre:
            flash('Telefon ve şifre alanları zorunludur.', 'danger')
            return render_template('auth/login.html')

        # Veritabanında müşteriyi ara
        db = get_db()
        musteri = db.execute(
            'SELECT * FROM musteriler WHERE telefon = ?', (telefon,)
        ).fetchone()

        # Müşteri bulundu ve şifre doğru mu?
        if musteri and sifre_dogru_mu(sifre, musteri['sifre_hash']):
            if not musteri['aktif']:
                flash('Hesabınız pasife alınmıştır. Lütfen iletişime geçin.', 'warning')
                return render_template('auth/login.html')

            # Session'ı oluştur ve müşteri paneline yönlendir
            musteri_giris_yap(musteri['id'], musteri['ad_soyad'])
            flash(f'Hoş geldiniz, {musteri["ad_soyad"]}!', 'success')
            return redirect(url_for('musteri.panel'))
        else:
            flash('Telefon numarası veya şifre hatalı.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/kayit', methods=['GET', 'POST'])
def kayit_page():
    """
    Müşteri kayıt sayfası.

    POST: Yeni müşteri hesabı oluşturur.
          Telefon numarası benzersiz olmalı (UNIQUE constraint).

    DOĞRULAMA KURALLARI (DFD notlarından):
        - Ad-Soyad: Sadece harf
        - Telefon: Sadece sayı
    """
    if 'kullanici_rol' in session:
        return _rol_yonlendir(session['kullanici_rol'])

    if request.method == 'POST':
        # Form verilerini topla
        ad_soyad = request.form.get('ad_soyad', '').strip()
        telefon  = request.form.get('telefon', '').strip()
        email    = request.form.get('email', '').strip()
        sifre    = request.form.get('sifre', '').strip()
        sifre2   = request.form.get('sifre2', '').strip()

        # --------------------------------------------------
        # Validasyon – her alanı ayrı ayrı doğrula
        # --------------------------------------------------
        hatalar = []

        gecerli, mesaj = ad_soyad_gecerli_mi(ad_soyad)
        if not gecerli:
            hatalar.append(mesaj)

        gecerli, mesaj = telefon_gecerli_mi(telefon)
        if not gecerli:
            hatalar.append(mesaj)

        gecerli, mesaj = email_gecerli_mi(email)
        if not gecerli:
            hatalar.append(mesaj)

        gecerli, mesaj = sifre_gecerli_mi(sifre)
        if not gecerli:
            hatalar.append(mesaj)

        if sifre != sifre2:
            hatalar.append('Şifreler birbiriyle eşleşmiyor.')

        # Hata varsa formu tekrar göster
        if hatalar:
            for hata in hatalar:
                flash(hata, 'danger')
            return render_template('auth/kayit.html',
                                   form_data={'ad_soyad': ad_soyad,
                                              'telefon': telefon,
                                              'email': email})

        # --------------------------------------------------
        # Veritabanına kaydet
        # --------------------------------------------------
        db = get_db()

        # Telefon numarası daha önce kayıtlı mı?
        mevcut = db.execute(
            'SELECT id FROM musteriler WHERE telefon = ?', (telefon,)
        ).fetchone()

        if mevcut:
            flash('Bu telefon numarası zaten kayıtlı.', 'danger')
            return render_template('auth/kayit.html')

        # Şifreyi hash'le ve kaydet
        sifre_hash = hash_sifre(sifre)
        db.execute('''
            INSERT INTO musteriler (ad_soyad, telefon, email, sifre_hash)
            VALUES (?, ?, ?, ?)
        ''', (ad_soyad, telefon, email or None, sifre_hash))
        db.commit()

        flash('Kaydınız başarıyla oluşturuldu! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login_page'))

    return render_template('auth/kayit.html')


# ==============================================================
# PERSONEL / ADMİN GİRİŞİ
# ==============================================================

@auth_bp.route('/personel-login', methods=['GET', 'POST'])
def personel_login_page():
    """
    Personel ve Admin giriş sayfası.

    Personel: e-posta + şifre ile giriş yapar.
    rol alanına göre ('personel' veya 'admin') yönlendirme yapılır.
    """
    if 'kullanici_rol' in session:
        return _rol_yonlendir(session['kullanici_rol'])

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        sifre = request.form.get('sifre', '').strip()

        if not email or not sifre:
            flash('E-posta ve şifre zorunludur.', 'danger')
            return render_template('auth/personel_login.html')

        # Personel veritabanında ara
        db = get_db()
        personel = db.execute(
            'SELECT * FROM personeller WHERE email = ? AND aktif = 1',
            (email,)
        ).fetchone()

        if personel and sifre_dogru_mu(sifre, personel['sifre_hash']):
            # rol='admin' ise admin paneline, değilse personel paneline
            personel_giris_yap(personel['id'], personel['ad_soyad'], personel['rol'])
            flash(f'Hoş geldiniz, {personel["ad_soyad"]}!', 'success')
            return _rol_yonlendir(personel['rol'])
        else:
            flash('E-posta veya şifre hatalı.', 'danger')

    return render_template('auth/personel_login.html')


# ==============================================================
# ÇIKIŞ
# ==============================================================

@auth_bp.route('/cikis')
def cikis():
    """
    Oturumu sonlandırır ve giriş sayfasına yönlendirir.
    session.clear() → tüm session verilerini siler.
    """
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login_page'))


# ==============================================================
# YARDIMCI FONKSİYON
# ==============================================================

def _rol_yonlendir(rol: str):
    """
    Kullanıcı rolüne göre uygun panele yönlendirir.
    Özel (private) fonksiyon – _ öneki bunu belirtir.
    """
    if rol == 'musteri':
        return redirect(url_for('musteri.panel'))
    elif rol == 'personel':
        return redirect(url_for('personel.panel'))
    elif rol == 'admin':
        return redirect(url_for('admin.panel'))
    return redirect(url_for('auth.login_page'))


