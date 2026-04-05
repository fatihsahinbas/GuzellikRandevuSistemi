"""
============================================================
 routes/personel_routes.py  –  Personel İşlemleri
============================================================
DFD'de personel tarafındaki akışlar:

  4.0 → Onaylanan Randevu Kaydı   → randevu_onayla()
  5.0 → Randevu Bilgisi Hatırlatma → hatirlatma_gonder()
  6.0 → Randevu Gelme Durumu      → gelme_durumu_guncelle()
  7.0 → Personel Değerlendirme    → degerlendirmeleri_goruntule()

ROUTE TABLOSU:
    GET  /personel/panel             → Personel ana paneli
    GET  /personel/randevular        → Randevu listesi
    POST /personel/onayla/<id>       → Randevu onayla
    POST /personel/reddet/<id>       → Randevu reddet
    POST /personel/gelme/<id>        → Gelme durumu güncelle
    POST /personel/hatirlatma/<id>   → Hatırlatma e-postası gönder
    GET  /personel/degerlendirmelerim → Kendi değerlendirmeleri
============================================================
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from database import get_db
from utils.auth_helper import personel_mi, admin_mi
from utils.email_helper import (email_gonder, hatirlatma_emaili_olustur,
                                 randevu_onay_emaili_olustur)

personel_bp = Blueprint('personel', __name__)


def personel_giris_gerekli(f):
    """
    Decorator: Personel veya Admin girişi gerektiren sayfalar için.
    Admin de personel yetkisine sahip olduğundan her ikisi de geçer.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not (personel_mi() or admin_mi()):
            flash('Bu sayfaya erişmek için personel girişi gereklidir.', 'warning')
            return redirect(url_for('auth.personel_login_page'))
        return f(*args, **kwargs)
    return decorated


@personel_bp.route('/panel')
@personel_giris_gerekli
def panel():
    """
    Personel ana paneli.

    Personel yalnızca kendi randevularını görür.
    Bugünkü randevular öne çıkarılır.
    """
    from datetime import date
    db = get_db()
    personel_id = session['kullanici_id']
    bugun = date.today().isoformat()

    # Bugünkü randevular
    bugunun_randevulari = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi, m.telefon AS musteri_telefon
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        WHERE r.personel_id = ?
          AND r.tarih = ?
          AND r.durum IN ('beklemede', 'onaylandi')
        ORDER BY r.saat ASC
    ''', (personel_id, bugun)).fetchall()

    # Bekleyen onay talepleri
    bekleyen_sayi = db.execute(
        'SELECT COUNT(*) FROM randevular WHERE personel_id = ? AND durum = "beklemede"',
        (personel_id,)
    ).fetchone()[0]

    # Bu hafta tamamlanan randevular
    tamamlanan_sayi = db.execute(
        'SELECT COUNT(*) FROM randevular WHERE personel_id = ? AND durum = "tamamlandi"',
        (personel_id,)
    ).fetchone()[0]

    return render_template('personel/panel.html',
                           bugunun_randevulari=bugunun_randevulari,
                           bekleyen_sayi=bekleyen_sayi,
                           tamamlanan_sayi=tamamlanan_sayi)


@personel_bp.route('/randevular')
@personel_giris_gerekli
def randevular():
    """
    Personelin tüm randevularını listeler.
    Durum filtresi ile filtreleme yapılabilir.
    """
    db = get_db()
    personel_id = session['kullanici_id']
    durum_filtre = request.args.get('durum', 'hepsi')  # URL ?durum=beklemede

    # Filtre koşulunu oluştur
    if durum_filtre == 'hepsi':
        randevu_listesi = db.execute('''
            SELECT r.*, m.ad_soyad AS musteri_adi, m.telefon AS musteri_telefon,
                   m.email AS musteri_email
            FROM randevular r
            JOIN musteriler m ON r.musteri_id = m.id
            WHERE r.personel_id = ?
            ORDER BY r.tarih DESC, r.saat DESC
        ''', (personel_id,)).fetchall()
    else:
        randevu_listesi = db.execute('''
            SELECT r.*, m.ad_soyad AS musteri_adi, m.telefon AS musteri_telefon,
                   m.email AS musteri_email
            FROM randevular r
            JOIN musteriler m ON r.musteri_id = m.id
            WHERE r.personel_id = ? AND r.durum = ?
            ORDER BY r.tarih DESC, r.saat DESC
        ''', (personel_id, durum_filtre)).fetchall()

    return render_template('personel/randevular.html',
                           randevular=randevu_listesi,
                           aktif_filtre=durum_filtre)


@personel_bp.route('/onayla/<int:randevu_id>', methods=['POST'])
@personel_giris_gerekli
def randevu_onayla(randevu_id):
    """
    DFD 4.0 – Onaylanan Randevu Kaydı.

    Beklemedeki randevuyu onaylar ve:
    1. Randevu durumunu 'onaylandi' yapar
    2. Müşteriye onay e-postası gönderir (müşteri e-postası varsa)

    Yalnızca randevunun atandığı personel onaylayabilir.
    """
    db = get_db()
    personel_id = session['kullanici_id']

    # Randevuyu getir ve bu personele ait mi kontrol et
    randevu = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi, m.email AS musteri_email
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        WHERE r.id = ? AND r.personel_id = ?
    ''', (randevu_id, personel_id)).fetchone()

    if not randevu:
        flash('Randevu bulunamadı veya yetkiniz yok.', 'danger')
        return redirect(url_for('personel.randevular'))

    if randevu['durum'] != 'beklemede':
        flash('Yalnızca beklemedeki randevular onaylanabilir.', 'warning')
        return redirect(url_for('personel.randevular'))

    # Durumu güncelle
    db.execute(
        'UPDATE randevular SET durum = "onaylandi" WHERE id = ?',
        (randevu_id,)
    )
    db.commit()

    # Müşteri e-postası varsa onay maili gönder
    if randevu['musteri_email']:
        html = randevu_onay_emaili_olustur(
            randevu['musteri_adi'],
            randevu['tarih'],
            randevu['saat'],
            randevu['islem']
        )
        email_gonder(
            randevu['musteri_email'],
            'Randevunuz Onaylandı – Güzellik Salonu',
            html
        )

    flash(f'{randevu["musteri_adi"]} adlı müşterinin randevusu onaylandı.', 'success')
    return redirect(url_for('personel.randevular'))


@personel_bp.route('/reddet/<int:randevu_id>', methods=['POST'])
@personel_giris_gerekli
def randevu_reddet(randevu_id):
    """
    Beklemedeki randevuyu reddeder.

    DFD 3.0'daki ONAY/RED akışının RED kısmı:
    Personel uygun değilse randevuyu reddeder.
    """
    db = get_db()
    personel_id = session['kullanici_id']

    randevu = db.execute(
        'SELECT * FROM randevular WHERE id = ? AND personel_id = ?',
        (randevu_id, personel_id)
    ).fetchone()

    if not randevu:
        flash('Randevu bulunamadı.', 'danger')
        return redirect(url_for('personel.randevular'))

    db.execute(
        'UPDATE randevular SET durum = "reddedildi" WHERE id = ?',
        (randevu_id,)
    )
    db.commit()

    flash('Randevu reddedildi.', 'info')
    return redirect(url_for('personel.randevular'))


@personel_bp.route('/gelme-durumu/<int:randevu_id>', methods=['POST'])
@personel_giris_gerekli
def gelme_durumu_guncelle(randevu_id):
    """
    DFD 6.0 – Randevu Gelme Durumu.

    Müşterinin randevuya gelip gelmediğini kaydeder ve
    DFD'de belirtilen puan sistemini uygular:

    PUAN KURALLARI:
        Geldi + zamanında → +10 puan
        Geldi + geç       → +0 puan (mevcut puan korunur)
        Gelmedi           → -20 puan

    Bu veriler D1 (Müşteri Kayıtları) veritabanına işlenir.
    """
    db = get_db()
    personel_id = session['kullanici_id']

    # Form'dan durum ve zamanında geldi bilgisini al
    yeni_durum  = request.form.get('durum', '')         # 'tamamlandi' veya 'gelmedi'
    zamaninda   = request.form.get('zamaninda', '0')    # '1' veya '0'

    if yeni_durum not in ('tamamlandi', 'gelmedi'):
        flash('Geçersiz durum.', 'danger')
        return redirect(url_for('personel.randevular'))

    randevu = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        WHERE r.id = ? AND r.personel_id = ?
    ''', (randevu_id, personel_id)).fetchone()

    if not randevu:
        flash('Randevu bulunamadı.', 'danger')
        return redirect(url_for('personel.randevular'))

    if randevu['durum'] not in ('onaylandi',):
        flash('Yalnızca onaylı randevuların gelme durumu güncellenebilir.', 'warning')
        return redirect(url_for('personel.randevular'))

    # --------------------------------------------------
    # Puan hesaplama (DFD 6.0 – Puan Güncelleme)
    # --------------------------------------------------
    puan_degisimi = 0
    gelmeme_degisimi = 0

    if yeni_durum == 'tamamlandi':
        if zamaninda == '1':
            puan_degisimi = 10   # Zamanında geldi → ödül puan
        # Geç geldiyse puan değişmez
    else:  # 'gelmedi'
        puan_degisimi = -20      # Gelmedi → ceza puan
        gelmeme_degisimi = 1

    # Randevu durumunu güncelle
    db.execute(
        'UPDATE randevular SET durum = ? WHERE id = ?',
        (yeni_durum, randevu_id)
    )

    # Müşteri puanını ve gelmeme sayısını güncelle (D1 - Müşteri Kayıtları)
    if puan_degisimi != 0 or gelmeme_degisimi > 0:
        db.execute('''
            UPDATE musteriler
            SET puan = MAX(0, puan + ?),
                gelmeme_sayisi = gelmeme_sayisi + ?
            WHERE id = ?
        ''', (puan_degisimi, gelmeme_degisimi, randevu['musteri_id']))

    db.commit()

    if yeni_durum == 'tamamlandi':
        flash(
            f'{randevu["musteri_adi"]} randevusu tamamlandı. '
            f'Puan değişimi: {"+" if puan_degisimi >= 0 else ""}{puan_degisimi}',
            'success'
        )
    else:
        flash(f'{randevu["musteri_adi"]} randevuya gelmedi. Puan: {puan_degisimi}', 'warning')

    return redirect(url_for('personel.randevular'))


@personel_bp.route('/hatirlatma/<int:randevu_id>', methods=['POST'])
@personel_giris_gerekli
def hatirlatma_gonder(randevu_id):
    """
    DFD 5.0 – Randevu Bilgisi Hatırlatma Mesajı.

    Onaylanan randevu için müşteriye e-posta hatırlatması gönderir.
    Her randevu için yalnızca bir kez gönderilebilir
    (hatirlatma_gonderildi=1 kontrolü).
    """
    db = get_db()
    personel_id = session['kullanici_id']

    randevu = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi, m.email AS musteri_email,
               p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.id = ? AND r.personel_id = ?
    ''', (randevu_id, personel_id)).fetchone()

    if not randevu:
        flash('Randevu bulunamadı.', 'danger')
        return redirect(url_for('personel.randevular'))

    # Daha önce gönderilmiş mi?
    if randevu['hatirlatma_gonderildi']:
        flash('Bu randevu için hatırlatma zaten gönderildi.', 'info')
        return redirect(url_for('personel.randevular'))

    # Müşteri e-postası var mı?
    if not randevu['musteri_email']:
        flash('Müşterinin e-posta adresi kayıtlı değil.', 'warning')
        return redirect(url_for('personel.randevular'))

    # E-postayı oluştur ve gönder
    html = hatirlatma_emaili_olustur(
        randevu['musteri_adi'],
        randevu['tarih'],
        randevu['saat'],
        randevu['islem'],
        randevu['personel_adi']
    )

    basarili = email_gonder(
        randevu['musteri_email'],
        f'Randevu Hatırlatması – {randevu["tarih"]} {randevu["saat"]}',
        html
    )

    if basarili:
        # Hatırlatma gönderildi olarak işaretle
        db.execute(
            'UPDATE randevular SET hatirlatma_gonderildi = 1 WHERE id = ?',
            (randevu_id,)
        )
        db.commit()
        flash('Hatırlatma e-postası başarıyla gönderildi.', 'success')
    else:
        flash('E-posta gönderilemedi. E-posta ayarlarını kontrol edin.', 'danger')

    return redirect(url_for('personel.randevular'))


@personel_bp.route('/degerlendirmelerim')
@personel_giris_gerekli
def degerlendirmelerim():
    """
    DFD 7.0 – Personel Değerlendirme İşlemi.

    Personel, müşterilerin kendisine verdiği değerlendirmeleri görür.
    Ortalama puanlar ve yorumlar listelenir.
    """
    db = get_db()
    personel_id = session['kullanici_id']

    # Tüm değerlendirmeleri getir
    degerlendirmeler = db.execute('''
        SELECT d.*, m.ad_soyad AS musteri_adi,
               r.tarih, r.islem
        FROM degerlendirmeler d
        JOIN musteriler m ON d.musteri_id = m.id
        JOIN randevular r ON d.randevu_id = r.id
        WHERE d.personel_id = ?
        ORDER BY d.olusturma_tarihi DESC
    ''', (personel_id,)).fetchall()

    # Ortalama puanları hesapla
    ortalama = db.execute('''
        SELECT
            AVG(hizmet_puani) AS ort_hizmet,
            AVG(tutum_puani)  AS ort_tutum,
            AVG(sure_puani)   AS ort_sure,
            COUNT(*)          AS toplam_degerlendirme
        FROM degerlendirmeler
        WHERE personel_id = ?
    ''', (personel_id,)).fetchone()

    return render_template('personel/degerlendirmelerim.html',
                           degerlendirmeler=degerlendirmeler,
                           ortalama=ortalama)
@personel_bp.route('/sifre-degistir', methods=['GET', 'POST'])
@personel_giris_gerekli
def sifre_degistir():
    """
    Personelin kendi şifresini değiştirmesi.

    Mevcut şifreyi doğrular, yeni şifreyi kaydeder.
    Admin de bu sayfayı kullanabilir.
    """
    if request.method == 'POST':
        mevcut_sifre = request.form.get('mevcut_sifre', '').strip()
        yeni_sifre   = request.form.get('yeni_sifre', '').strip()
        yeni_sifre2  = request.form.get('yeni_sifre2', '').strip()

        db = get_db()
        personel = db.execute(
            'SELECT * FROM personeller WHERE id = ?',
            (session['kullanici_id'],)
        ).fetchone()

        # Mevcut şifre doğru mu?
        from utils.auth_helper import sifre_dogru_mu, hash_sifre
        if not sifre_dogru_mu(mevcut_sifre, personel['sifre_hash']):
            flash('Mevcut şifreniz hatalı.', 'danger')
            return render_template('personel/sifre_degistir.html')

        # Yeni şifre geçerli mi?
        from utils.validators import sifre_gecerli_mi
        gecerli, mesaj = sifre_gecerli_mi(yeni_sifre)
        if not gecerli:
            flash(mesaj, 'danger')
            return render_template('personel/sifre_degistir.html')

        # Şifreler eşleşiyor mu?
        if yeni_sifre != yeni_sifre2:
            flash('Yeni şifreler birbiriyle eşleşmiyor.', 'danger')
            return render_template('personel/sifre_degistir.html')

        # Yeni şifreyi kaydet
        db.execute(
            'UPDATE personeller SET sifre_hash = ? WHERE id = ?',
            (hash_sifre(yeni_sifre), session['kullanici_id'])
        )
        db.commit()

        flash('Şifreniz başarıyla güncellendi.', 'success')
        return redirect(url_for('personel.panel'))

    return render_template('personel/sifre_degistir.html')