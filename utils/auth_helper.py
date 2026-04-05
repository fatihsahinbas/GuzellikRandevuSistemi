"""
============================================================
 utils/auth_helper.py  –  Kimlik Doğrulama Yardımcıları
============================================================
Şifre hash'leme, session yönetimi ve giriş doğrulama
işlemleri için yardımcı fonksiyonlar.

ANAHTAR KAVRAM – Hash:
    Hash, bir metni geri dönüşü olmayan şekilde şifreler.
    Tıpkı bir et kıyma makinesinden geçirmek gibi:
    et → kıyma olur ama kıyma → ete geri dönemez.
    Veritabanına şifre değil, hash kaydedilir.

ANAHTAR KAVRAM – Session:
    Kullanıcının giriş durumunu hatırlamak için kullanılır.
    Flask, session verilerini şifreli cookie olarak tarayıcıya
    gönderir. SECRET_KEY ile imzalanır.
============================================================
"""

import hashlib
from flask import session
from database import get_db


def hash_sifre(sifre: str) -> str:
    """
    Şifreyi SHA-256 algoritması ile hash'ler.

    Args:
        sifre: Düz metin şifre

    Returns:
        64 karakterlik hexadecimal hash string

    Örnek:
        hash_sifre("abc123") → "6ca13d52ca70c883e0f0..."
    """
    return hashlib.sha256(sifre.encode('utf-8')).hexdigest()


def sifre_dogru_mu(duz_sifre: str, hash_deger: str) -> bool:
    """
    Girilen şifrenin hash'i ile veritabanındaki hash'i karşılaştırır.

    Args:
        duz_sifre: Kullanıcının girdiği şifre
        hash_deger: Veritabanındaki hash

    Returns:
        True = şifre doğru, False = yanlış
    """
    return hash_sifre(duz_sifre) == hash_deger


def musteri_giris_yap(musteri_id: int, ad_soyad: str):
    """
    Müşteri bilgilerini session'a kaydeder (oturum açar).

    Session'a kaydettiğimiz bilgiler tarayıcıya şifreli
    cookie olarak gönderilir.
    """
    session.clear()                        # Önceki oturumu temizle
    session['kullanici_id']  = musteri_id
    session['kullanici_adi'] = ad_soyad
    session['kullanici_rol'] = 'musteri'


def personel_giris_yap(personel_id: int, ad_soyad: str, rol: str):
    """
    Personel veya Admin bilgilerini session'a kaydeder.

    Args:
        rol: 'personel' veya 'admin'
    """
    session.clear()
    session['kullanici_id']  = personel_id
    session['kullanici_adi'] = ad_soyad
    session['kullanici_rol'] = rol


def oturum_ac_mi() -> bool:
    """Kullanıcı oturum açmış mı? True/False döndürür."""
    return 'kullanici_id' in session


def musteri_mi() -> bool:
    """Oturumdaki kullanıcı müşteri mi?"""
    return session.get('kullanici_rol') == 'musteri'


def personel_mi() -> bool:
    """Oturumdaki kullanıcı personel mi? (Admin dahil değil)"""
    return session.get('kullanici_rol') == 'personel'


def admin_mi() -> bool:
    """Oturumdaki kullanıcı admin mi?"""
    return session.get('kullanici_rol') == 'admin'


def guncel_musteri():
    """
    Session'daki ID ile veritabanından müşteri kaydını getirir.

    Returns:
        sqlite3.Row nesnesi veya None
    """
    if not musteri_mi():
        return None
    db = get_db()
    return db.execute(
        'SELECT * FROM musteriler WHERE id = ?',
        (session['kullanici_id'],)
    ).fetchone()


def guncel_personel():
    """
    Session'daki ID ile veritabanından personel kaydını getirir.

    Returns:
        sqlite3.Row nesnesi veya None
    """
    if session.get('kullanici_rol') not in ('personel', 'admin'):
        return None
    db = get_db()
    return db.execute(
        'SELECT * FROM personeller WHERE id = ?',
        (session['kullanici_id'],)
    ).fetchone()
