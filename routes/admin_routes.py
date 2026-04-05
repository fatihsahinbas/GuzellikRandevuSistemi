"""
============================================================
 routes/admin_routes.py  –  Admin Paneli
============================================================
Admin tüm sistem üzerinde tam yetkiye sahiptir:

    - Müşteri listesi ve yönetimi
    - Personel ekleme / düzenleme
    - Tüm randevuları görme
    - Sistem istatistikleri
    - Hatırlatma toplu gönderimi

ROUTE TABLOSU:
    GET  /admin/panel             → Admin ana sayfası
    GET  /admin/musteriler        → Müşteri listesi
    GET  /admin/personeller       → Personel listesi
    POST /admin/personel-ekle     → Yeni personel ekle
    GET  /admin/tum-randevular    → Tüm sistem randevuları
    GET  /admin/istatistikler     → Raporlar ve grafikler
    POST /admin/toplu-hatirlatma  → Toplu e-posta gönder
============================================================
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from database import get_db
from utils.auth_helper import admin_mi, hash_sifre
from utils.validators import (ad_soyad_gecerli_mi, email_gecerli_mi,
                               sifre_gecerli_mi)
from utils.email_helper import email_gonder, hatirlatma_emaili_olustur

admin_bp = Blueprint('admin', __name__)


def admin_gerekli(f):
    """
    Decorator: Yalnızca admin rolüne sahip kullanıcılar erişebilir.
    Personeller bu sayfaları göremez.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not admin_mi():
            flash('Bu sayfaya yalnızca yönetici erişebilir.', 'danger')
            return redirect(url_for('auth.personel_login_page'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/panel')
@admin_gerekli
def panel():
    """
    Admin ana paneli – genel sistem istatistikleri.

    Gösterilen metrikler:
        - Toplam müşteri / personel sayısı
        - Bugünkü randevu sayısı
        - Bekleyen onay sayısı
        - Son 5 randevu
    """
    from datetime import date
    db = get_db()
    bugun = date.today().isoformat()

    # Genel sayımlar
    toplam_musteri  = db.execute('SELECT COUNT(*) FROM musteriler WHERE aktif=1').fetchone()[0]
    toplam_personel = db.execute(
        'SELECT COUNT(*) FROM personeller WHERE aktif=1 AND rol="personel"'
    ).fetchone()[0]
    bugun_randevu   = db.execute(
        'SELECT COUNT(*) FROM randevular WHERE tarih=?', (bugun,)
    ).fetchone()[0]
    bekleyen        = db.execute(
        'SELECT COUNT(*) FROM randevular WHERE durum="beklemede"'
    ).fetchone()[0]

    # Son 10 randevu (tüm sistemden)
    son_randevular = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi, p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        JOIN personeller p ON r.personel_id = p.id
        ORDER BY r.olusturma_tarihi DESC
        LIMIT 10
    ''').fetchall()

    return render_template('admin/panel.html',
                           toplam_musteri=toplam_musteri,
                           toplam_personel=toplam_personel,
                           bugun_randevu=bugun_randevu,
                           bekleyen=bekleyen,
                           son_randevular=son_randevular)


@admin_bp.route('/musteriler')
@admin_gerekli
def musteriler():
    """
    Tüm müşterileri listeler.
    Puan sıralaması ve gelmeme sayısı ile birlikte gösterir.
    """
    db = get_db()

    # Müşteri listesi + randevu sayısı
    musteri_listesi = db.execute('''
        SELECT m.*,
               COUNT(r.id) AS toplam_randevu,
               SUM(CASE WHEN r.durum='tamamlandi' THEN 1 ELSE 0 END) AS tamamlanan
        FROM musteriler m
        LEFT JOIN randevular r ON m.id = r.musteri_id
        GROUP BY m.id
        ORDER BY m.puan DESC
    ''').fetchall()

    return render_template('admin/musteriler.html', musteriler=musteri_listesi)


@admin_bp.route('/musteri-durum/<int:musteri_id>', methods=['POST'])
@admin_gerekli
def musteri_durum_degistir(musteri_id):
    """
    Müşteriyi aktif/pasif yapar (ban/unban işlemi).
    Pasif müşteriler sisteme giriş yapamaz.
    """
    db = get_db()
    musteri = db.execute('SELECT * FROM musteriler WHERE id=?', (musteri_id,)).fetchone()

    if not musteri:
        flash('Müşteri bulunamadı.', 'danger')
        return redirect(url_for('admin.musteriler'))

    yeni_durum = 0 if musteri['aktif'] else 1
    db.execute('UPDATE musteriler SET aktif=? WHERE id=?', (yeni_durum, musteri_id))
    db.commit()

    durum_metni = 'aktifleştirildi' if yeni_durum else 'pasife alındı'
    flash(f'{musteri["ad_soyad"]} {durum_metni}.', 'info')
    return redirect(url_for('admin.musteriler'))


@admin_bp.route('/personeller')
@admin_gerekli
def personeller():
    """
    Tüm personelleri listeler.
    Her personelin ortalama değerlendirme puanını gösterir.
    """
    db = get_db()

    personel_listesi = db.execute('''
        SELECT p.*,
               COUNT(DISTINCT r.id) AS toplam_randevu,
               AVG(d.hizmet_puani + d.tutum_puani + d.sure_puani) / 3.0 AS ort_puan
        FROM personeller p
        LEFT JOIN randevular r ON p.id = r.personel_id
        LEFT JOIN degerlendirmeler d ON p.id = d.personel_id
        WHERE p.rol = 'personel'
        GROUP BY p.id
        ORDER BY ort_puan DESC NULLS LAST
    ''').fetchall()

    return render_template('admin/personeller.html', personeller=personel_listesi)


@admin_bp.route('/personel-ekle', methods=['GET', 'POST'])
@admin_gerekli
def personel_ekle():
    """
    Yeni personel hesabı oluşturur.
    Admin bu sayfadan personel ekler, personeller sisteme kayıt olamaz.
    """
    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad', '').strip()
        email    = request.form.get('email', '').strip()
        sifre    = request.form.get('sifre', '').strip()
        uzmanlik = request.form.get('uzmanlik', '').strip()

        # Validasyon
        hatalar = []
        gecerli, mesaj = ad_soyad_gecerli_mi(ad_soyad)
        if not gecerli: hatalar.append(mesaj)

        gecerli, mesaj = email_gecerli_mi(email)
        if not gecerli or not email: hatalar.append('Geçerli bir e-posta giriniz.')

        gecerli, mesaj = sifre_gecerli_mi(sifre)
        if not gecerli: hatalar.append(mesaj)

        if not uzmanlik:
            hatalar.append('Uzmanlık alanı zorunludur.')

        if hatalar:
            for h in hatalar: flash(h, 'danger')
            return render_template('admin/personel_ekle.html')

        db = get_db()

        # E-posta benzersiz mi?
        if db.execute('SELECT id FROM personeller WHERE email=?', (email,)).fetchone():
            flash('Bu e-posta adresi zaten kayıtlı.', 'danger')
            return render_template('admin/personel_ekle.html')

        db.execute('''
            INSERT INTO personeller (ad_soyad, email, sifre_hash, uzmanlik, rol)
            VALUES (?, ?, ?, ?, 'personel')
        ''', (ad_soyad, email, hash_sifre(sifre), uzmanlik))
        db.commit()

        flash(f'{ad_soyad} personel olarak eklendi.', 'success')
        return redirect(url_for('admin.personeller'))

    return render_template('admin/personel_ekle.html')


@admin_bp.route('/tum-randevular')
@admin_gerekli
def tum_randevular():
    """
    Tüm sistemdeki randevuları gösterir.
    Filtre: tarih, personel, durum.
    """
    db = get_db()

    # URL parametrelerinden filtreleri al
    filtre_durum    = request.args.get('durum', 'hepsi')
    filtre_tarih    = request.args.get('tarih', '')

    sorgu = '''
        SELECT r.*, m.ad_soyad AS musteri_adi, p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        JOIN personeller p ON r.personel_id = p.id
        WHERE 1=1
    '''
    parametreler = []

    if filtre_durum != 'hepsi':
        sorgu += ' AND r.durum = ?'
        parametreler.append(filtre_durum)

    if filtre_tarih:
        sorgu += ' AND r.tarih = ?'
        parametreler.append(filtre_tarih)

    sorgu += ' ORDER BY r.tarih DESC, r.saat DESC'

    randevu_listesi = db.execute(sorgu, parametreler).fetchall()

    return render_template('admin/tum_randevular.html',
                           randevular=randevu_listesi,
                           filtre_durum=filtre_durum,
                           filtre_tarih=filtre_tarih)


@admin_bp.route('/toplu-hatirlatma', methods=['POST'])
@admin_gerekli
def toplu_hatirlatma():
    """
    Yarın randevusu olan ve henüz hatırlatma gönderilmemiş
    tüm müşterilere toplu e-posta gönderir.

    DFD 5.0 – Randevu Bilgisi Hatırlatma (otomatik toplu versiyon).
    """
    from datetime import date, timedelta
    db = get_db()

    # Yarının tarihi
    yarin = (date.today() + timedelta(days=1)).isoformat()

    # Yarın randevusu olan, onaylanan ve hatırlatma gönderilmemiş randevular
    randevular = db.execute('''
        SELECT r.*, m.ad_soyad AS musteri_adi, m.email AS musteri_email,
               p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN musteriler m ON r.musteri_id = m.id
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.tarih = ?
          AND r.durum = 'onaylandi'
          AND r.hatirlatma_gonderildi = 0
          AND m.email IS NOT NULL
    ''', (yarin,)).fetchall()

    gonderilen = 0
    for randevu in randevular:
        html = hatirlatma_emaili_olustur(
            randevu['musteri_adi'],
            randevu['tarih'],
            randevu['saat'],
            randevu['islem'],
            randevu['personel_adi']
        )
        if email_gonder(randevu['musteri_email'],
                        'Yarın Randevunuz Var – guzellikmerkezi', html):
            db.execute(
                'UPDATE randevular SET hatirlatma_gonderildi=1 WHERE id=?',
                (randevu['id'],)
            )
            gonderilen += 1

    db.commit()
    flash(f'{gonderilen} müşteriye hatırlatma e-postası gönderildi.', 'success')
    return redirect(url_for('admin.panel'))


@admin_bp.route('/istatistikler')
@admin_gerekli
def istatistikler():
    """
    Sistem istatistikleri sayfası.

    Gösterilen veriler:
        - Aylık randevu sayıları
        - En çok tercih edilen işlemler
        - En yüksek puanlı müşteriler
        - Personel performans sıralaması
    """
    db = get_db()

    # Son 6 ayın randevu dağılımı
    aylik_randevular = db.execute('''
        SELECT strftime('%Y-%m', tarih) AS ay, COUNT(*) AS sayi
        FROM randevular
        GROUP BY ay
        ORDER BY ay DESC
        LIMIT 6
    ''').fetchall()

    # En çok tercih edilen işlemler
    populer_islemler = db.execute('''
        SELECT islem, COUNT(*) AS sayi
        FROM randevular
        GROUP BY islem
        ORDER BY sayi DESC
        LIMIT 5
    ''').fetchall()

    # En yüksek puanlı müşteriler (ilk 10)
    en_iyi_musteriler = db.execute('''
        SELECT ad_soyad, puan, gelmeme_sayisi
        FROM musteriler
        WHERE aktif = 1
        ORDER BY puan DESC
        LIMIT 10
    ''').fetchall()

    # Personel performans sıralaması
    personel_performans = db.execute('''
        SELECT p.ad_soyad,
               COUNT(r.id) AS toplam,
               AVG(d.hizmet_puani) AS ort_hizmet
        FROM personeller p
        LEFT JOIN randevular r ON p.id = r.personel_id AND r.durum='tamamlandi'
        LEFT JOIN degerlendirmeler d ON p.id = d.personel_id
        WHERE p.rol = 'personel'
        GROUP BY p.id
        ORDER BY ort_hizmet DESC NULLS LAST
    ''').fetchall()

    return render_template('admin/istatistikler.html',
                           aylik_randevular=aylik_randevular,
                           populer_islemler=populer_islemler,
                           en_iyi_musteriler=en_iyi_musteriler,
                           personel_performans=personel_performans)

@admin_bp.route('/hizmetler', methods=['GET', 'POST'])
@admin_gerekli
def hizmetler():
    db = get_db()

    if request.method == 'POST':
        ad = request.form.get('ad', '').strip()
        if not ad:
            flash('Hizmet adı boş olamaz.', 'danger')
        else:
            mevcut = db.execute(
                'SELECT id FROM hizmetler WHERE ad = ?', (ad,)
            ).fetchone()
            if mevcut:
                flash('Bu hizmet zaten mevcut.', 'warning')
            else:
                db.execute('INSERT INTO hizmetler (ad) VALUES (?)', (ad,))
                db.commit()
                flash(f'"{ad}" hizmeti eklendi.', 'success')

    hizmet_listesi = db.execute(
        'SELECT * FROM hizmetler ORDER BY ad ASC'
    ).fetchall()

    return render_template('admin/hizmetler.html', hizmetler=hizmet_listesi)


@admin_bp.route('/hizmet-sil/<int:hizmet_id>', methods=['POST'])
@admin_gerekli
def hizmet_sil(hizmet_id):
    db = get_db()
    db.execute('UPDATE hizmetler SET aktif = 0 WHERE id = ?', (hizmet_id,))
    db.commit()
    flash('Hizmet pasife alındı.', 'info')
    return redirect(url_for('admin.hizmetler'))


@admin_bp.route('/hizmet-aktif/<int:hizmet_id>', methods=['POST'])
@admin_gerekli
def hizmet_aktif(hizmet_id):
    db = get_db()
    db.execute('UPDATE hizmetler SET aktif = 1 WHERE id = ?', (hizmet_id,))
    db.commit()
    flash('Hizmet aktifleştirildi.', 'success')
    return redirect(url_for('admin.hizmetler'))