"""
============================================================
 utils/validators.py  –  Form Doğrulama Fonksiyonları
============================================================
Kullanıcıdan gelen verilerin geçerliliğini kontrol eder.

ANAHTAR KAVRAM – Validasyon (Doğrulama):
    Kullanıcıdan gelen her veri güvenilmez kabul edilir.
    "Hiçbir zaman kullanıcıya güvenme" – güvenlik altın kuralı.
    Frontend'de JS ile kontrol + Backend'de Python ile kontrol.

NOT: DFD notlarında belirtilen özel kurallar uygulanır:
    - Ad-Soyad: Harf dışı karakter girilirse hata ver
    - Telefon: Sayı dışı karakter girilirse hata ver
============================================================
"""

import re


def ad_soyad_gecerli_mi(ad_soyad: str) -> tuple[bool, str]:
    """
    Ad-Soyad alanının geçerliliğini kontrol eder.

    KURAL (DFD notlarından):
        Ad-Soyad bölümüne harf dışında bir şey girildiğinde hata ver.
        Türkçe karakterler (ğ, ü, ş, ı, ö, ç) de geçerli sayılır.

    Args:
        ad_soyad: Kullanıcının girdiği ad-soyad

    Returns:
        (True, "") = geçerli
        (False, "hata mesajı") = geçersiz

    Örnek:
        ad_soyad_gecerli_mi("Ahmet Yılmaz") → (True, "")
        ad_soyad_gecerli_mi("Ahmet123")     → (False, "Ad-soyad...")
    """
    if not ad_soyad or not ad_soyad.strip():
        return False, "Ad-soyad boş bırakılamaz."

    # Türkçe dahil sadece harf ve boşluk karakterlerine izin ver
    # \u00C0-\u017E aralığı → Türkçe ve Avrupa dil karakterleri
    pattern = r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$'
    if not re.match(pattern, ad_soyad.strip()):
        return False, "Ad-soyad bölümüne yalnızca harf girilebilir."

    if len(ad_soyad.strip()) < 3:
        return False, "Ad-soyad en az 3 karakter olmalıdır."

    if len(ad_soyad.strip()) > 100:
        return False, "Ad-soyad en fazla 100 karakter olabilir."

    return True, ""


def telefon_gecerli_mi(telefon: str) -> tuple[bool, str]:
    """
    Telefon numarasının geçerliliğini kontrol eder.

    KURAL (DFD notlarından):
        Telefon numarasına sayı dışında bir şey girildiğinde hata ver.

    Geçerli formatlar:
        05551234567  (11 haneli, 0 ile başlayan)
        5551234567   (10 haneli)
        +905551234567 (uluslararası format, + işareti kabul)

    Args:
        telefon: Kullanıcının girdiği telefon numarası

    Returns:
        (True, "") = geçerli
        (False, "hata mesajı") = geçersiz
    """
    if not telefon or not telefon.strip():
        return False, "Telefon numarası boş bırakılamaz."

    # Boşlukları ve tire işaretini temizle (05XX XXX XX XX → 05XXXXXXXXX)
    temiz = telefon.strip().replace(' ', '').replace('-', '')

    # + işareti kabul ediliyor (uluslararası format)
    if temiz.startswith('+'):
        temiz = temiz[1:]  # + işaretini kaldır

    # Sadece rakam içermeli
    if not temiz.isdigit():
        return False, "Telefon numarasına yalnızca sayı girilebilir."

    # Uzunluk kontrolü (10-12 hane arası kabul)
    if len(temiz) < 10 or len(temiz) > 12:
        return False, "Telefon numarası 10-12 hane arasında olmalıdır."

    return True, ""


def sifre_gecerli_mi(sifre: str) -> tuple[bool, str]:
    """
    Şifrenin güçlülüğünü kontrol eder.

    Kurallar:
        - En az 6 karakter
        - En az 1 rakam
        - En az 1 harf

    Args:
        sifre: Kullanıcının girdiği şifre

    Returns:
        (True, "") = geçerli
        (False, "hata mesajı") = geçersiz
    """
    if not sifre:
        return False, "Şifre boş bırakılamaz."

    if len(sifre) < 6:
        return False, "Şifre en az 6 karakter olmalıdır."

    if not any(c.isdigit() for c in sifre):
        return False, "Şifre en az bir rakam içermelidir."

    if not any(c.isalpha() for c in sifre):
        return False, "Şifre en az bir harf içermelidir."

    return True, ""


def tarih_gecerli_mi(tarih: str) -> tuple[bool, str]:
    """
    Randevu tarihinin geçerliliğini kontrol eder.

    Kurallar:
        - YYYY-MM-DD formatında olmalı
        - Geçmişte bir tarih olmamalı

    Args:
        tarih: YYYY-MM-DD formatında tarih string'i

    Returns:
        (True, "") = geçerli
        (False, "hata mesajı") = geçersiz
    """
    from datetime import date

    try:
        # Tarihi parse et (yanlış format ise ValueError fırlatır)
        randevu_tarihi = date.fromisoformat(tarih)
    except ValueError:
        return False, "Geçersiz tarih formatı. YYYY-MM-DD kullanın."

    # Geçmiş tarih kontrolü
    if randevu_tarihi < date.today():
        return False, "Geçmiş bir tarihe randevu alınamaz."

    # Çok uzak gelecek tarihi engelle (1 yıl ötesi)
    from datetime import timedelta
    max_tarih = date.today() + timedelta(days=365)
    if randevu_tarihi > max_tarih:
        return False, "En fazla 1 yıl sonrası için randevu alınabilir."

    return True, ""


def email_gecerli_mi(email: str) -> tuple[bool, str]:
    """
    E-posta adresinin formatını kontrol eder.

    Args:
        email: E-posta adresi

    Returns:
        (True, "") = geçerli
        (False, "hata mesajı") = geçersiz
    """
    if not email:
        return True, ""  # E-posta zorunlu değil, boş geçilebilir

    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Geçerli bir e-posta adresi giriniz."

    return True, ""

def cakisma_var_mi(db, personel_id: int, tarih: str,
                   yeni_saat: str, yeni_sure_dk: int,
                   haric_randevu_id: int | None = None) -> bool:
    """
    Yeni randevunun mevcut randevularla çakışıp çakışmadığını kontrol eder.

    Mantık (zaman çizelgesi analojisi):
        Her randevu bir "blok" gibidir: başlangıç saatinden
        (başlangıç + süre) dakikasına kadar o personeli meşgul eder.
        Yeni randevu bu bloklardan herhangi biriyle örtüşüyorsa çakışır.

    Örnek:
        Mevcut: 10:00, 60 dk  → 10:00–11:00 arası dolu
        Yeni:   10:30, 30 dk  → 10:30–11:00 → ÇAKIŞIR
        Yeni:   11:00, 30 dk  → 11:00–11:30 → ÇAKIŞMAZ

    Args:
        db              : Veritabanı bağlantısı
        personel_id     : Hangi personelin takvimi kontrol edilecek
        tarih           : YYYY-MM-DD formatında tarih
        yeni_saat       : HH:MM formatında yeni randevu saati
        yeni_sure_dk    : Yeni randevunun süresi (dakika)
        hariç_randevu_id: Düzenleme durumunda kendisiyle çakışmasını önler

    Returns:
        True → çakışma VAR (randevuyu reddet)
        False → çakışma YOK (randevuya izin ver)
    """
    from datetime import datetime, timedelta

    # Yeni randevunun başlangıç ve bitiş zamanı
    fmt = '%H:%M'
    yeni_bas  = datetime.strptime(yeni_saat, fmt)
    yeni_bitis = yeni_bas + timedelta(minutes=yeni_sure_dk)

    # O personelin o günkü aktif randevularını çek
    # Her randevuyla birlikte o randevunun hizmet süresini de getir
    sorgu = '''
        SELECT r.saat, h.sure_dakika
        FROM randevular r
        JOIN hizmetler h ON r.islem = h.ad
        WHERE r.personel_id = ?
          AND r.tarih = ?
          AND r.durum IN ('beklemede', 'onaylandi')
    '''
    params = [personel_id, tarih]

    if haric_randevu_id is not None:
        sorgu += ' AND r.id != ?'
        params.append(str(haric_randevu_id))

    mevcut_randevular = db.execute(sorgu, params).fetchall()

    for mevcut in mevcut_randevular:
        m_bas   = datetime.strptime(mevcut['saat'], fmt)
        m_bitis = m_bas + timedelta(minutes=mevcut['sure_dakika'] or 30)

        # Örtüşme kontrolü:
        # İki blok çakışır ←→ biri diğerinden önce biter DEĞİLse
        # Yani: yeni_bas < m_bitis VE yeni_bitis > m_bas
        if yeni_bas < m_bitis and yeni_bitis > m_bas:
            return True   # Çakışma var

    return False   # Çakışma yok