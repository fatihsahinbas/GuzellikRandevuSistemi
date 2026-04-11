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
    db = get_db()

<<<<<<< HEAD
    # Uzmanlığa göre personel — hizmet adlarıyla birlikte getir
    personeller_raw = db.execute('''
=======
    # Uzmanlığa göre personel — hizmetler ile JOIN
    personeller = db.execute('''
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
        SELECT DISTINCT p.id, p.ad_soyad
        FROM personeller p
        JOIN personel_uzmanliklar pu ON p.id = pu.personel_id
        JOIN hizmetler h ON pu.hizmet_id = h.id
        WHERE p.aktif = 1 AND p.rol = 'personel' AND h.aktif = 1
        ORDER BY p.ad_soyad
    ''').fetchall()

<<<<<<< HEAD
    # Her personelin uzmanlık isimlerini liste olarak ekle
    personeller = []
    for p in personeller_raw:
        hizmetler_row = db.execute('''
            SELECT h.ad FROM hizmetler h
            JOIN personel_uzmanliklar pu ON h.id = pu.hizmet_id
            WHERE pu.personel_id = ? AND h.aktif = 1
        ''', (p['id'],)).fetchall()
        uzmanlik_listesi = [h['ad'] for h in hizmetler_row]
        personeller.append({
            'id': p['id'],
            'ad_soyad': p['ad_soyad'],
            'uzmanlik': uzmanlik_listesi,           # liste: ['Botoks', 'Dolgu']
            'uzmanlik_str': ', '.join(uzmanlik_listesi)  # gösterim için
        })

=======
>>>>>>> cba97dee2e250d3553d98cbaeef0ffe1ea1868e1
    islemler = db.execute(
        'SELECT * FROM hizmetler WHERE aktif=1 ORDER BY ad'
    ).fetchall()

    if request.method == 'POST':
        from utils.validators import cakisma_var_mi
        from utils.logger import log_randevu
        from datetime import datetime, timedelta

        personel_id = int(request.form.get('personel_id', 0))
        islem       = request.form.get('islem', '').strip()
        tarih       = request.form.get('tarih', '').strip()
        saat        = request.form.get('saat', '').strip()

        # --- Tatil günü kontrolü ---
        # Hem sistem geneli hem o personele özel tatil var mı?
        tatil = db.execute('''
            SELECT aciklama FROM tatil_gunleri
            WHERE tarih = ?
              AND (personel_id IS NULL OR personel_id = ?)
            LIMIT 1
        ''', (tarih, personel_id)).fetchone()

        if tatil:
            flash(
                f'{tarih} tarihi tatil/izin günü: '
                f'{tatil["aciklama"] or "Kapalı"}. '
                'Lütfen başka bir tarih seçin.',
                'warning'
            )
            return render_template('musteri/randevu_al.html',
                                   personeller=personeller, islemler=islemler)

        # --- Çalışma saati kontrolü ---
        # Python weekday(): 0=Pazartesi, 6=Pazar
        tarih_dt = datetime.strptime(tarih, '%Y-%m-%d')
        gun_idx  = tarih_dt.weekday()

        calisma = db.execute('''
            SELECT baslangic_saat, bitis_saat
            FROM personel_calisma_saatleri
            WHERE personel_id = ? AND gun = ?
        ''', (personel_id, gun_idx)).fetchone()

        if calisma:
            # Seçilen saat çalışma aralığında mı?
            if not (calisma['baslangic_saat'] <= saat < calisma['bitis_saat']):
                flash(
                    f'Bu personel {["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"][gun_idx]} '
                    f'günü {calisma["baslangic_saat"]}–{calisma["bitis_saat"]} saatleri arasında çalışmaktadır.',
                    'warning'
                )
                return render_template('musteri/randevu_al.html',
                                       personeller=personeller, islemler=islemler)
        # Çalışma saati tanımlanmamışsa kısıtlama yok (varsayılan: her saat açık)

        # --- Akıllı çakışma kontrolü (madde 3'ten) ---
        hizmet   = db.execute('SELECT sure_dakika FROM hizmetler WHERE ad=?', (islem,)).fetchone()
        yeni_sure = hizmet['sure_dakika'] if hizmet else 30

        if cakisma_var_mi(db, personel_id, tarih, saat, yeni_sure):
            flash(
                f'Seçilen saat ({saat}) dolu — önceki randevu henüz tamamlanmamış. '
                f'En az {yeni_sure} dakika sonrasına bir saat seçin.',
                'warning'
            )
            return render_template('musteri/randevu_al.html',
                                   personeller=personeller, islemler=islemler)

        # --- Randevuyu kaydet ---
        musteri_id = session['kullanici_id']
        cursor = db.execute('''
            INSERT INTO randevular (musteri_id, personel_id, islem, tarih, saat)
            VALUES (?, ?, ?, ?, ?)
        ''', (musteri_id, personel_id, islem, tarih, saat))
        db.commit()

        log_randevu('olustur', cursor.lastrowid,
                    f'{islem} — {tarih} {saat}')

        flash(f'Randevu talebiniz alındı! {tarih} {saat} — onay bekleniyor.', 'success')
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
    
import json

@musteri_bp.route('/takvim')
@giris_gerekli
def takvim():
    """
    Müşterinin randevularını takvim görünümünde gösterir.
    FullCalendar.js için veriyi ayrı bir endpoint'ten (takvim_veri) çekeriz.
    """
    return render_template('musteri/takvim.html')


@musteri_bp.route('/takvim-veri')
@giris_gerekli
def takvim_veri():
    """
    FullCalendar.js'in beklediği JSON formatında randevu verisi döndürür.

    FullCalendar her olayı şu yapıda bekler:
    {
        "title": "Görünen başlık",
        "start": "2024-03-15T10:30:00",   ← ISO 8601 format
        "color": "#renk_kodu",
        "extendedProps": { ... }           ← ekstra veri
    }
    """
    from flask import jsonify
    db = get_db()
    musteri_id = session['kullanici_id']

    randevular = db.execute('''
        SELECT r.tarih, r.saat, r.islem, r.durum,
               p.ad_soyad AS personel_adi
        FROM randevular r
        JOIN personeller p ON r.personel_id = p.id
        WHERE r.musteri_id = ?
    ''', (musteri_id,)).fetchall()

    # Durum → renk eşlemesi
    # Tıpkı trafik ışıkları gibi: beklemede=sarı, onaylı=yeşil, iptal=kırmızı
    renk_haritasi = {
        'beklemede':   '#f39c12',   # turuncu-sarı
        'onaylandi':   '#27ae60',   # yeşil
        'tamamlandi':  '#2980b9',   # mavi
        'reddedildi':  '#e74c3c',   # kırmızı
        'gelmedi':     '#95a5a6',   # gri
    }

    etkinlikler = []
    for r in randevular:
        etkinlikler.append({
            'title': f"{r['saat']} – {r['islem']}",
            # FullCalendar "YYYY-MM-DDTHH:MM" formatını anlar
            'start': f"{r['tarih']}T{r['saat']}:00",
            'color': renk_haritasi.get(r['durum'], '#7f8c8d'),
            'extendedProps': {
                'durum':       r['durum'],
                'personel':    r['personel_adi'],
                'islem':       r['islem'],
            }
        })

    return jsonify(etkinlikler)    


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