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
    Müşteri listesi — ada, telefona veya e-postaya göre arama destekler.

    Arama, URL query parametresiyle çalışır: /admin/musteriler?q=ahmet
    Bu sayede arama sonucu URL'de kalır, sayfa yenilenince kaybolmaz.
    """
    db = get_db()
    q = request.args.get('q', '').strip()   # Arama terimi

    if q:
        # LIKE ile kısmi eşleşme: %ahmet% → "ahmet" içeren her şey
        # Hem ad-soyad hem telefon hem e-postada ara
        arama = f'%{q}%'
        musteri_listesi = db.execute('''
            SELECT * FROM musteriler
            WHERE (ad_soyad LIKE ?
               OR  telefon  LIKE ?
               OR  email    LIKE ?)
            ORDER BY ad_soyad
        ''', (arama, arama, arama)).fetchall()
    else:
        musteri_listesi = db.execute(
            'SELECT * FROM musteriler ORDER BY ad_soyad'
        ).fetchall()

    return render_template('admin/musteriler.html',
                           musteriler=musteri_listesi,
                           arama_terimi=q)


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

    # Her personel için uzmanlık isimlerini ayrıca çek
    personel_uzmanliklar = {}
    for p in personel_listesi:
        hizmetler = db.execute('''
            SELECT h.ad FROM hizmetler h
            JOIN personel_uzmanliklar pu ON h.id = pu.hizmet_id
            WHERE pu.personel_id = ?
            ORDER BY h.ad
        ''', (p['id'],)).fetchall()
        personel_uzmanliklar[p['id']] = [h['ad'] for h in hizmetler]

    return render_template('admin/personeller.html',
                           personeller=personel_listesi,
                           personel_uzmanliklar=personel_uzmanliklar)


@admin_bp.route('/personel-ekle', methods=['GET', 'POST'])
@admin_gerekli
def personel_ekle():
    """
    Yeni personel ekler. Uzmanlıklar artık çoklu seçimli (checkbox).
    Her seçilen hizmet personel_uzmanliklar tablosuna ayrı satır olarak girer.
    """
    from utils.logger import log_admin
    db = get_db()
    hizmetler = db.execute(
        'SELECT * FROM hizmetler WHERE aktif=1 ORDER BY ad'
    ).fetchall()

    if request.method == 'POST':
        ad_soyad       = request.form.get('ad_soyad', '').strip()
        email          = request.form.get('email', '').strip()
        sifre          = request.form.get('sifre', '').strip()
        # getlist → birden fazla checkbox değerini liste olarak alır
        uzmanlik_idler = request.form.getlist('uzmanlik_ids')

        hatalar = []
        gecerli, mesaj = ad_soyad_gecerli_mi(ad_soyad)
        if not gecerli: hatalar.append(mesaj)

        gecerli, mesaj = email_gecerli_mi(email)
        if not gecerli: hatalar.append('Geçerli bir e-posta giriniz.')

        gecerli, mesaj = sifre_gecerli_mi(sifre)
        if not gecerli: hatalar.append(mesaj)

        if not uzmanlik_idler:
            hatalar.append('En az bir uzmanlık seçmelisiniz.')

        if hatalar:
            for h in hatalar: flash(h, 'danger')
            return render_template('admin/personel_ekle.html', hizmetler=hizmetler)

        if db.execute('SELECT id FROM personeller WHERE email=?', (email,)).fetchone():
            flash('Bu e-posta zaten kayıtlı.', 'danger')
            return render_template('admin/personel_ekle.html', hizmetler=hizmetler)

        # Personeli ekle
        cursor = db.execute('''
            INSERT INTO personeller (ad_soyad, email, sifre_hash, uzmanlik, rol)
            VALUES (?, ?, ?, ?, 'personel')
        ''', (ad_soyad, email, hash_sifre(sifre), ','.join(uzmanlik_idler)))
        db.commit()
        personel_id = cursor.lastrowid

        # Uzmanlıkları ilişki tablosuna ekle
        for hizmet_id in uzmanlik_idler:
            db.execute('''
                INSERT OR IGNORE INTO personel_uzmanliklar (personel_id, hizmet_id)
                VALUES (?, ?)
            ''', (personel_id, int(hizmet_id)))
        db.commit()

        log_admin('personel_ekle', f'{ad_soyad} eklendi, {len(uzmanlik_idler)} uzmanlık')
        flash(f'{ad_soyad} başarıyla eklendi.', 'success')
        return redirect(url_for('admin.personeller'))

    return render_template('admin/personel_ekle.html', hizmetler=hizmetler)



@admin_bp.route('/personel-duzenle/<int:personel_id>', methods=['GET', 'POST'])
@admin_gerekli
def personel_duzenle(personel_id):
    """
    Mevcut personelin tüm bilgilerini tek sayfada düzenler:
      - Ad-soyad, e-posta
      - Şifre (boş bırakılırsa değişmez)
      - Uzmanlıklar (checkbox)
      - Çalışma saatleri (7 gün)
    """
    from utils.logger import log_admin
    db = get_db()

    personel = db.execute(
        'SELECT * FROM personeller WHERE id=?', (personel_id,)
    ).fetchone()

    if not personel:
        flash('Personel bulunamadı.', 'danger')
        return redirect(url_for('admin.personeller'))

    hizmetler = db.execute(
        'SELECT * FROM hizmetler WHERE aktif=1 ORDER BY ad'
    ).fetchall()

    mevcut_uzmanliklar = set(
        row['hizmet_id'] for row in db.execute(
            'SELECT hizmet_id FROM personel_uzmanliklar WHERE personel_id=?',
            (personel_id,)
        ).fetchall()
    )

    GUNLER = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

    mevcut_saatler = {
        row['gun']: row
        for row in db.execute(
            'SELECT * FROM personel_calisma_saatleri WHERE personel_id=?',
            (personel_id,)
        ).fetchall()
    }

    if request.method == 'POST':
        ad_soyad       = request.form.get('ad_soyad', '').strip()
        email          = request.form.get('email', '').strip()
        sifre          = request.form.get('sifre', '').strip()
        uzmanlik_idler = request.form.getlist('uzmanlik_ids')

        hatalar = []
        gecerli, mesaj = ad_soyad_gecerli_mi(ad_soyad)
        if not gecerli: hatalar.append(mesaj)
        gecerli, mesaj = email_gecerli_mi(email)
        if not gecerli: hatalar.append('Geçerli bir e-posta giriniz.')
        if not uzmanlik_idler: hatalar.append('En az bir uzmanlık seçmelisiniz.')

        baska = db.execute(
            'SELECT id FROM personeller WHERE email=? AND id!=?', (email, personel_id)
        ).fetchone()
        if baska: hatalar.append('Bu e-posta başka bir personele ait.')

        if hatalar:
            for h in hatalar: flash(h, 'danger')
            return render_template('admin/personel_duzenle.html',
                                   personel=personel, hizmetler=hizmetler,
                                   mevcut_uzmanliklar=mevcut_uzmanliklar,
                                   gunler=GUNLER, mevcut_saatler=mevcut_saatler)

        if sifre:
            db.execute('UPDATE personeller SET ad_soyad=?, email=?, sifre_hash=? WHERE id=?',
                       (ad_soyad, email, hash_sifre(sifre), personel_id))
        else:
            db.execute('UPDATE personeller SET ad_soyad=?, email=? WHERE id=?',
                       (ad_soyad, email, personel_id))

        db.execute('DELETE FROM personel_uzmanliklar WHERE personel_id=?', (personel_id,))
        for hizmet_id in uzmanlik_idler:
            db.execute('INSERT OR IGNORE INTO personel_uzmanliklar (personel_id, hizmet_id) VALUES (?, ?)',
                       (personel_id, int(hizmet_id)))

        db.execute('DELETE FROM personel_calisma_saatleri WHERE personel_id=?', (personel_id,))
        for gun_idx in range(7):
            bas   = request.form.get(f'bas_{gun_idx}', '').strip()
            bitis = request.form.get(f'bitis_{gun_idx}', '').strip()
            if bas and bitis and bas < bitis:
                db.execute('''INSERT INTO personel_calisma_saatleri
                    (personel_id, gun, baslangic_saat, bitis_saat) VALUES (?, ?, ?, ?)''',
                    (personel_id, gun_idx, bas, bitis))

        db.commit()
        log_admin('personel_duzenle', f'{ad_soyad} güncellendi')
        flash(f'{ad_soyad} başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.personeller'))

    return render_template('admin/personel_duzenle.html',
                           personel=personel, hizmetler=hizmetler,
                           mevcut_uzmanliklar=mevcut_uzmanliklar,
                           gunler=GUNLER, mevcut_saatler=mevcut_saatler)

@admin_bp.route('/personel-calisma/<int:personel_id>', methods=['GET', 'POST'])
@admin_gerekli
def personel_calisma(personel_id):
    """
    Personelin haftalık çalışma saatlerini tanımlar.
    Her gün için ayrı başlangıç-bitiş saati girilebilir.
    Çalışılmayan günler boş bırakılır.
    """
    from utils.logger import log_admin
    db  = get_db()
    p   = db.execute('SELECT * FROM personeller WHERE id=?', (personel_id,)).fetchone()
    if not p:
        flash('Personel bulunamadı.', 'danger')
        return redirect(url_for('admin.personeller'))

    GUNLER = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

    if request.method == 'POST':
        # Mevcut saatleri sil, yenileriyle değiştir
        db.execute('DELETE FROM personel_calisma_saatleri WHERE personel_id=?', (personel_id,))

        for gun_idx in range(7):
            bas  = request.form.get(f'bas_{gun_idx}', '').strip()
            bitis = request.form.get(f'bitis_{gun_idx}', '').strip()
            if bas and bitis and bas < bitis:   # İkisi de doluysa kaydet
                db.execute('''
                    INSERT INTO personel_calisma_saatleri
                        (personel_id, gun, baslangic_saat, bitis_saat)
                    VALUES (?, ?, ?, ?)
                ''', (personel_id, gun_idx, bas, bitis))

        db.commit()
        log_admin('calisma_saati_guncelle', f'{p["ad_soyad"]} çalışma saatleri güncellendi')
        flash('Çalışma saatleri kaydedildi.', 'success')
        return redirect(url_for('admin.personeller'))

    # Mevcut saatleri sözlüğe çevir: {gun_idx: row}
    mevcut = {
        row['gun']: row
        for row in db.execute(
            'SELECT * FROM personel_calisma_saatleri WHERE personel_id=?',
            (personel_id,)
        ).fetchall()
    }

    return render_template('admin/personel_calisma.html',
                           personel=p, gunler=GUNLER, mevcut=mevcut)


@admin_bp.route('/tatil-gunleri', methods=['GET', 'POST'])
@admin_gerekli
def tatil_gunleri():
    """
    Sistem geneli veya personel bazlı tatil/izin günü tanımlar.
    personel_id boş → sistem geneli tatil (resmi tatil, bayram vb.)
    personel_id dolu → o personelin izin günü
    """
    from utils.logger import log_admin
    db = get_db()

    if request.method == 'POST':
        eylem = request.form.get('eylem')

        if eylem == 'ekle':
            tarih       = request.form.get('tarih', '').strip()
            aciklama    = request.form.get('aciklama', '').strip()
            personel_id = request.form.get('personel_id') or None

            if not tarih:
                flash('Tarih zorunludur.', 'danger')
            else:
                db.execute('''
                    INSERT INTO tatil_gunleri (personel_id, tarih, aciklama)
                    VALUES (?, ?, ?)
                ''', (personel_id, tarih, aciklama))
                db.commit()
                hedef = 'Sistem geneli' if not personel_id else 'Personel izni'
                log_admin('tatil_ekle', f'{hedef}: {tarih} — {aciklama}')
                flash(f'{tarih} tarihi tatil olarak eklendi.', 'success')

        elif eylem == 'sil':
            tatil_id = request.form.get('tatil_id')
            db.execute('DELETE FROM tatil_gunleri WHERE id=?', (tatil_id,))
            db.commit()
            log_admin('tatil_sil', f'Tatil #{tatil_id} silindi')
            flash('Tatil günü silindi.', 'info')

        return redirect(url_for('admin.tatil_gunleri'))

    # Tüm tatilleri çek — personel adıyla birlikte
    tatiller = db.execute('''
        SELECT t.*, p.ad_soyad AS personel_adi
        FROM tatil_gunleri t
        LEFT JOIN personeller p ON t.personel_id = p.id
        ORDER BY t.tarih DESC
    ''').fetchall()

    personel_listesi = db.execute(
        "SELECT id, ad_soyad FROM personeller WHERE rol='personel' AND aktif=1"
    ).fetchall()

    return render_template('admin/tatil_gunleri.html',
                           tatiller=tatiller, personeller=personel_listesi)


@admin_bp.route('/loglar')
@admin_gerekli
def loglar():
    """
    Sistem loglarını admin panelinde gösterir.
    Seviye ve islem bazlı filtreleme destekler.
    """
    db  = get_db()
    seviye = request.args.get('seviye', '')
    islem  = request.args.get('islem', '')

    sorgu  = 'SELECT * FROM loglar WHERE 1=1'
    params = []

    if seviye:
        sorgu += ' AND seviye = ?'
        params.append(seviye)
    if islem:
        sorgu += ' AND islem LIKE ?'
        params.append(f'%{islem}%')

    sorgu += ' ORDER BY id DESC LIMIT 500'

    log_listesi = db.execute(sorgu, params).fetchall()
    return render_template('admin/loglar.html',
                           loglar=log_listesi,
                           aktif_seviye=seviye,
                           aktif_islem=islem)


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
                #db.execute('INSERT INTO hizmetler (ad) VALUES (?)', (ad,))
                
                sure = int(request.form.get('sure_dakika', 30))
                db.execute(
                    'INSERT INTO hizmetler (ad, sure_dakika) VALUES (?, ?)',
                    (ad, sure)
                )
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