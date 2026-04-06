"""
============================================================
 app.py  –   Randevu Yönetim Sistemi
============================================================
Bu dosya Flask uygulamasının giriş noktasıdır (entry point).
Tüm blueprint'leri (route gruplarını) burada kayıt ederiz ve
veritabanını ilk çalıştırmada otomatik oluştururuz.

ANAHTAR KAVRAM – Blueprint:
    Flask'ta büyük projeleri küçük modüllere bölmek için
    Blueprint kullanılır. Tıpkı bir binanın katlarına benzer:
    her katın kendi odaları (route'ları) vardır ama hepsi
    aynı çatı altındadır (Flask app).
============================================================
"""

from flask import Flask, redirect, url_for
from database import init_db          # Veritabanı başlatma fonksiyonu
from routes.auth_routes import auth_bp          # Kimlik doğrulama route'ları
from routes.musteri_routes import musteri_bp    # Müşteri işlemleri
from routes.personel_routes import personel_bp  # Personel işlemleri
from routes.admin_routes import admin_bp        # Admin paneli
import config                                   # Ayar dosyası

def create_app():
    """
    Uygulama fabrikası (Application Factory Pattern).

    Bu tasarım deseni sayesinde test ortamı için farklı,
    üretim ortamı için farklı ayarlarla uygulama oluşturabiliriz.
    Tıpkı bir araba fabrikasının aynı modeli farklı renklerle
    üretmesi gibi.
    """
    app = Flask(__name__)

    # -------------------------------------------------------
    # Uygulama ayarlarını config.py'den yükle
    # -------------------------------------------------------
    app.config.from_object(config.Config)

    # -------------------------------------------------------
    # Blueprint'leri kayıt et (URL prefix = URL ön eki)
    # Örnek: /musteri/randevu-al → musteri blueprint'i
    # -------------------------------------------------------
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(musteri_bp, url_prefix='/musteri')
    app.register_blueprint(personel_bp, url_prefix='/personel')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # -------------------------------------------------------
    # Veritabanını başlat (tablolar yoksa oluştur)
    # -------------------------------------------------------
    with app.app_context():
        init_db()

    return app


# -------------------------------------------------------
# Ana sayfa yönlendirmesi
# -------------------------------------------------------
app = create_app()
app.jinja_env.globals['enumerate'] = enumerate

@app.route('/')
def index():
    """Kullanıcıyı ana giriş sayfasına yönlendirir."""
    return redirect(url_for('auth.login_page'))


# -------------------------------------------------------
# Uygulamayı başlat (sadece doğrudan çalıştırıldığında)
# -------------------------------------------------------
if __name__ == '__main__':
    # debug=True → kod değişince otomatik yeniden başlar
    # Üretimde (production) debug=False olmalı!
    app.run(debug=True, host='0.0.0.0', port=5001)
