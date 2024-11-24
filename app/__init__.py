from flask import Flask
from firebase_admin import credentials, firestore, initialize_app, get_app

# Inisialisasi Firestore
def create_app():
    app = Flask(__name__)

    # Memeriksa apakah aplikasi Firebase sudah ada, jika belum inisialisasi
    try:
        # Mencoba mengakses aplikasi Firebase yang sudah ada
        get_app()
    except ValueError:
        # Jika aplikasi belum diinisialisasi, maka inisialisasi aplikasi Firebase
        cred = credentials.Certificate("serviceAccountKey.json")
        initialize_app(cred)  # Inisialisasi Firebase Admin SDK

    # Sambungkan ke Firestore
    db = firestore.client()  # Tanpa parameter 'database'

    # Menentukan koleksi yang ingin digunakan, misalnya 'maternalcaredb'
    maternalcare_collection = db.collection('maternalcaredb')

    return app, maternalcare_collection

# Membuat aplikasi
app, maternalcare_collection = create_app()

# Menjalankan aplikasi Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
