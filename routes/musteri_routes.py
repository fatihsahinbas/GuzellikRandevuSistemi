"""
============================================================
 routes/musteri_routes.py  –  Müşteri İşlemleri
============================================================
DFD'de müşteri tarafındaki tüm akışlar burada karşılık bulur:

  1.0 → login (auth_routes.py'de)
  2.0 → Randevu Talebi Oluştur  → randevu_al()
  3.0 → Uygunluk Kontrolü       → randevu_al() içinde
  8.0 → Müşterinin Formu Doldurması → degerlendirme_yap()

ROUTE TABLOSU:
    GET  /musteri/panel           → Müşteri ana paneli
    GET  /musteri/randevu-al      → Randevu alma formu
    POST /musteri/randevu-al      → Randevu talebini işle
    GET  /musteri/randevularim    → Randevuları listele
    POST /musteri/degerlendirme   → Değerlendirme formu gönder
============================================================
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from database import get_db
from utils.auth_helper import musteri_mi, guncel_musteri
from utils.email_helper import (email_gonder, iptal_emaili_olustur)
from utils.validators import tarih_gecerli_mi

musteri_bp = Blueprint('musteri', __name__)


def giris_gerekli(f):
    """
    Decorator: Müşteri girişi gerektiren sayfalarda kullanılır.

    ANAHTAR KAVRAM – Decorator (@):
        Bir fonksiyonu "sarmalar". Tıpkı bir güvenlik görevlisi
        gibi: "Bu odaya girebilmek için kartınızı okutun."
        Kart yoksa kapıda bekletir.

    Kullanım:
        @giris_gerekli
        def korunan_sayfa():
            ...
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not musteri_mi():
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@musteri_bp.route('/panel')
@giris_gerekli
def panel():
    """
    Müşteri ana paneli.
    Beklemedeki ve onaylanan randevuları gösterir.
    Müşteri puanını ve genel istatistikleri gösterir.
    """
    db = get_db()
    musteri_id = session['kullanici_id']

    # Aktif randevuları getir (beklemede veya onaylananlar)
    aktif_randevular = db.execute('''
        SELECT r.*, p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.musteri_id = ?
          AND r.durum IN ('beklemede', 'onaylandi')
        ORDER BY r.tarih ASC, r.saat ASC
    ''', (musteri_id,)).fetchall()

    # Müşteri bilgilerini getir (puan dahil)
    musteri = guncel_musteri()

    # Geçmiş randevuları say
    gecmis_sayi = db.execute(
        'SELECT COUNT(*) FROM randevular WHERE musteri_id = ? AND durum = "tamamlandi"',
        (musteri_id,)
    ).fetchone()[0]

    return render_template('musteri/panel.html',
                           aktif_randevular=aktif_randevular,
                           musteri=musteri,
                           gecmis_sayi=gecmis_sayi)


@musteri_bp.route('/randevu-al', methods=['GET', 'POST'])
@giris_gerekli
def randevu_al():
    """
    Randevu talebi oluşturma sayfası.

    DFD 2.0 – Randevu Talebi Oluştur:
        Müşteri: işlem seçer → personel seçer → tarih/saat seçer

    DFD 3.0 – Uygunluk Kontrolü:
        Seçilen tarih+saat+personel için randevu veritabanını
        kontrol eder. Müsait ise onaylar, değilse reddeder.

    DFD notlarından:
        Adım 3, 4 ve 5 aynı sayfada (tek formda) olacak.
    """
    db = get_db()

    # Tüm aktif personelleri getir (işlem seçimi için)
    personeller = db.execute(
        'SELECT * FROM personeller WHERE aktif = 1 AND rol = "personel" ORDER BY ad_soyad'
    ).fetchall()

    # Mevcut işlem türlerini personel uzmanlıklarından derle
    islemler = db.execute(
        'SELECT * FROM hizmetler WHERE aktif = 1 ORDER BY ad ASC'
    ).fetchall()

    if request.method == 'POST':
        # Form verilerini al
        islem      = request.form.get('islem', '').strip()
        personel_id = request.form.get('personel_id', '').strip()
        tarih      = request.form.get('tarih', '').strip()
        saat       = request.form.get('saat', '').strip()

        # --------------------------------------------------
        # Temel boşluk kontrolü
        # --------------------------------------------------
        if not all([islem, personel_id, tarih, saat]):
            flash('Tüm alanları doldurunuz.', 'danger')
            return render_template('musteri/randevu_al.html',
                                   personeller=personeller, islemler=islemler)

        # --------------------------------------------------
        # Tarih validasyonu
        # --------------------------------------------------
        gecerli, mesaj = tarih_gecerli_mi(tarih)
        if not gecerli:
            flash(mesaj, 'danger')
            return render_template('musteri/randevu_al.html',
                                   personeller=personeller, islemler=islemler)

        # --------------------------------------------------
        # DFD 3.0 – Uygunluk Kontrolü
        # Aynı personel, aynı tarih, aynı saatte başka randevu var mı?
        # --------------------------------------------------
        cakisan = db.execute('''
            SELECT id FROM randevular
            WHERE personel_id = ?
              AND tarih = ?
              AND saat = ?
              AND durum IN ('beklemede', 'onaylandi')
        ''', (personel_id, tarih, saat)).fetchone()

        if cakisan:
            # Müsait değil → reddet ve alternatif saat öner
            flash(
                f'Seçilen tarih ve saat ({tarih} {saat}) dolu. '
                'Lütfen farklı bir saat seçiniz.',
                'warning'
            )
            return render_template('musteri/randevu_al.html',
                                   personeller=personeller, islemler=islemler)

        # --------------------------------------------------
        # Müsait → Randevu talebini kaydet (durum='beklemede')
        # DFD 4.0 – Onaylanan Randevu Kaydı (personel onaylar)
        # --------------------------------------------------
        musteri_id = session['kullanici_id']
        db.execute('''
            INSERT INTO randevular (musteri_id, personel_id, islem, tarih, saat, durum)
            VALUES (?, ?, ?, ?, ?, 'beklemede')
        ''', (musteri_id, personel_id, islem, tarih, saat))
        db.commit()

        flash(
            f'Randevu talebiniz alındı! {tarih} tarihinde {saat} saatinde '
            f'"{islem}" işlemi için onay bekleniyor.',
            'success'
        )
        return redirect(url_for('musteri.randevularim'))

    return render_template('musteri/randevu_al.html',
                           personeller=personeller, islemler=islemler)


@musteri_bp.route('/randevularim')
@giris_gerekli
def randevularim():
    """
    Müşterinin tüm randevularını listeler.
    Durum renklerine göre filtreleme yapılabilir.
    """
    db = get_db()
    musteri_id = session['kullanici_id']

    randevular = db.execute('''
        SELECT r.*, p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.musteri_id = ?
        ORDER BY r.tarih DESC, r.saat DESC
    ''', (musteri_id,)).fetchall()

    # Değerlendirilmiş randevu ID'lerini set olarak topla
    # (Set → O(1) arama, listeden çok daha hızlı)
    degerlendirilmis = set(
        row['randevu_id'] for row in db.execute(
            'SELECT randevu_id FROM degerlendirmeler WHERE musteri_id = ?',
            (musteri_id,)
        ).fetchall()
    )

    return render_template('musteri/randevularim.html',
                           randevular=randevular,
                           degerlendirilmis=degerlendirilmis)


@musteri_bp.route('/degerlendirme/<int:randevu_id>', methods=['GET', 'POST'])
@giris_gerekli
def degerlendirme_yap(randevu_id):
    """
    DFD 8.0 – Müşterinin Formu Doldurması.

    Tamamlanan randevu için personel değerlendirmesi yapılır.
    Değerlendirme kriterleri:
        - Hizmet kalitesi (1-5)
        - Personel tutumu   (1-5)
        - İşlem süresi      (1-5)
        - Yorum (isteğe bağlı)

    Her randevu yalnızca bir kez değerlendirilebilir.
    """
    db = get_db()
    musteri_id = session['kullanici_id']

    # Randevuyu getir ve sahipliği kontrol et
    randevu = db.execute('''
        SELECT r.*, p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.id = ? AND r.musteri_id = ?
    ''', (randevu_id, musteri_id)).fetchone()

    if not randevu:
        flash('Randevu bulunamadı.', 'danger')
        return redirect(url_for('musteri.randevularim'))

    # Sadece tamamlanmış randevular değerlendirilebilir
    if randevu['durum'] != 'tamamlandi':
        flash('Yalnızca tamamlanmış randevular değerlendirilebilir.', 'warning')
        return redirect(url_for('musteri.randevularim'))

    # Daha önce değerlendirilmiş mi?
    mevcut = db.execute(
        'SELECT id FROM degerlendirmeler WHERE randevu_id = ?', (randevu_id,)
    ).fetchone()

    if mevcut:
        flash('Bu randevuyu daha önce değerlendirdiniz.', 'info')
        return redirect(url_for('musteri.randevularim'))

    if request.method == 'POST':
        # Puanları al ve integer'a çevir
        try:
            hizmet_puani = int(request.form.get('hizmet_puani', 0))
            tutum_puani  = int(request.form.get('tutum_puani', 0))
            sure_puani   = int(request.form.get('sure_puani', 0))
        except ValueError:
            flash('Geçersiz puan değeri.', 'danger')
            return render_template('musteri/degerlendirme.html', randevu=randevu)

        yorum = request.form.get('yorum', '').strip()

        # Puan aralığı kontrolü (1-5 arası olmalı)
        if not all(1 <= p <= 5 for p in [hizmet_puani, tutum_puani, sure_puani]):
            flash('Puanlar 1-5 arasında olmalıdır.', 'danger')
            return render_template('musteri/degerlendirme.html', randevu=randevu)

        # Değerlendirmeyi kaydet (D6 - Dolu Değerlendirme Formları)
        db.execute('''
            INSERT INTO degerlendirmeler
                (randevu_id, musteri_id, personel_id, hizmet_puani, tutum_puani, sure_puani, yorum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (randevu_id, musteri_id, randevu['personel_id'],
              hizmet_puani, tutum_puani, sure_puani, yorum or None))
        db.commit()

        flash('Değerlendirmeniz için teşekkür ederiz!', 'success')
        return redirect(url_for('musteri.randevularim'))

    return render_template('musteri/degerlendirme.html', randevu=randevu)


@musteri_bp.route('/randevu-iptal/<int:randevu_id>', methods=['POST'])
@giris_gerekli
def randevu_iptal(randevu_id):
    """
    Beklemedeki bir randevuyu iptal eder.
    İptal sonrası müşteriye e-posta bildirimi gönderir.

    Kurallar:
      - Yalnızca 'beklemede' durumundaki randevular iptal edilebilir.
      - Müşteri yalnızca kendi randevusunu iptal edebilir.
      - E-posta adresi kayıtlıysa iptal bildirimi gönderilir.
        Kayıtlı değilse iptal yine gerçekleşir, sadece e-posta atlanır.
    """
    db = get_db()
    musteri_id = session['kullanici_id']

    # Randevuyu çek; JOIN ile müşteri ve personel bilgilerini de al
    randevu = db.execute('''
        SELECT r.*,
               m.ad_soyad AS musteri_adi,
               m.email    AS musteri_email,
               p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN musteriler  m ON r.musteri_id  = m.id
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.id = ? AND r.musteri_id = ?
    ''', (randevu_id, musteri_id)).fetchone()

    if not randevu:
        flash('Randevu bulunamadı.', 'danger')
        return redirect(url_for('musteri.randevularim'))

    if randevu['durum'] != 'beklemede':
        flash('Yalnızca beklemedeki randevular iptal edilebilir.', 'warning')
        return redirect(url_for('musteri.randevularim'))

    # Durumu güncelle
    db.execute(
        'UPDATE randevular SET durum = "reddedildi" WHERE id = ?',
        (randevu_id,)
    )
    db.commit()

    # E-posta bildirimi — müşterinin e-postası varsa gönder
    if randevu['musteri_email']:
        html = iptal_emaili_olustur(
            musteri_adi=randevu['musteri_adi'],
            tarih=randevu['tarih'],
            saat=randevu['saat'],
            islem=randevu['islem'],
            personel=randevu['personel_adi']
        )
        email_gonder(
            randevu['musteri_email'],
            f'Randevu İptal Bildirimi – {randevu["tarih"]} {randevu["saat"]}',
            html
        )
        # Not: E-posta başarısız olsa bile iptal işlemi geri alınmaz.
        # Kullanıcıya hata göstermek yerine sessizce geçiyoruz,
        # çünkü asıl işlem (iptal) zaten tamamlandı.

    flash('Randevunuz iptal edildi. Bilgilendirme e-postası gönderildi.', 'info')
    return redirect(url_for('musteri.randevularim'))

@musteri_bp.route('/profil', methods=['GET', 'POST'])
@giris_gerekli
def profil():
    """
    Müşterinin kendi profil bilgilerini güncellemesi.
    Ad-Soyad, e-posta ve telefon güncellenebilir.
    """
    db = get_db()
    musteri = guncel_musteri()

    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad', '').strip()
        telefon  = request.form.get('telefon', '').strip()
        email    = request.form.get('email', '').strip()

        # Validasyon
        from utils.validators import ad_soyad_gecerli_mi, telefon_gecerli_mi, email_gecerli_mi
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

        if hatalar:
            for hata in hatalar:
                flash(hata, 'danger')
            return render_template('musteri/profil.html', musteri=musteri)

        # Telefon başkasına ait mi kontrol et
        baska_musteri = db.execute(
            'SELECT id FROM musteriler WHERE telefon = ? AND id != ?',
            (telefon, session['kullanici_id'])
        ).fetchone()

        if baska_musteri:
            flash('Bu telefon numarası başka bir hesaba kayıtlı.', 'danger')
            return render_template('musteri/profil.html', musteri=musteri)

        # Güncelle
        db.execute('''
            UPDATE musteriler
            SET ad_soyad = ?, telefon = ?, email = ?
            WHERE id = ?
        ''', (ad_soyad, telefon, email or None, session['kullanici_id']))
        db.commit()

        # Session'daki adı da güncelle
        session['kullanici_adi'] = ad_soyad

        flash('Profil bilgileriniz güncellendi.', 'success')
        return redirect(url_for('musteri.profil'))

    return render_template('musteri/profil.html', musteri=musteri)