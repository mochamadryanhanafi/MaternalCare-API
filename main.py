from app import create_app
from app.routes import bp  # Mengimpor blueprint dari app.routes

# Mendapatkan objek Flask (app) dan koleksi Firestore
app, maternalcare_collection = create_app()

# Daftarkan blueprint ke aplikasi Flask
app.register_blueprint(bp)

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
