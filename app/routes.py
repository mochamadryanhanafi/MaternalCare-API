import requests
import traceback
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import firestore
import uuid
import datetime

bp = Blueprint('routes', __name__)
db = firestore.client()

NEWS_API_KEY = "33774f0536514ef78e8eb0b72a4afe6f"



@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    email = data['email']
    username = data['username']  # Menggunakan username sebagai field baru
    full_name = data['full_name']

    # Periksa apakah email atau username sudah ada
    users_ref = db.collection('users')
    existing_email = users_ref.where('email', '==', email).get()
    existing_username = users_ref.where('username', '==', username).get()

    if len(existing_email) > 0:
        return jsonify({"error": "Email already exists"}), 400
    if len(existing_username) > 0:
        return jsonify({"error": "Username already exists"}), 400

    # Tambahkan pengguna baru
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user_data = {
        "username": username,  # Menggunakan username
        "full_name": full_name,
        "email": email,
        "password": hashed_password,
        "date_of_birth": None  # Tanggal lahir kosong saat registrasi
    }
    try:
        users_ref.add(user_data)  # Menambahkan data pengguna ke Firestore
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    email = data['email']
    password = data['password']

    # Cari pengguna berdasarkan email
    users_ref = db.collection('users')
    user_docs = users_ref.where('email', '==', email).get()
    if len(user_docs) == 0:
        return jsonify({"error": "Invalid credentials"}), 401

    user = user_docs[0].to_dict()
    if not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "username": user['username'],
            "email": user['email'],
            "fullname": user['full_name']  # Menambahkan fullname ke dalam respons
        }
    }), 200

def generate_reset_token(email):
    """Generate a reset token and store it in Firestore."""
    reset_token = str(uuid.uuid4())
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)

    # Simpan token ke database
    db.collection('reset_tokens').document(reset_token).set({
        'email': email,
        'expires_at': expiration_time.isoformat()
    })

    return reset_token

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    # Validasi email
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Cek apakah email ada di database
    users_ref = db.collection('users')
    user_docs = users_ref.where('email', '==', email).get()
    if not user_docs:
        return jsonify({"error": "Email not found"}), 404

    # Buat token reset password
    reset_token = generate_reset_token(email)

    # Redirect ke halaman reset password dengan token
    reset_link = f"http://34.128.90.238/reset-password.html?token={reset_token}"
    return jsonify({"redirect_url": reset_link}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    # Validasi input
    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    # Validasi token
    token_doc = db.collection('reset_tokens').document(token).get()
    if not token_doc.exists:
        return jsonify({"error": "Invalid or expired token"}), 400

    token_data = token_doc.to_dict()
    if datetime.datetime.fromisoformat(token_data['expires_at']) < datetime.datetime.now():
        return jsonify({"error": "Token has expired"}), 400

    # Perbarui password pengguna
    email = token_data['email']
    users_ref = db.collection('users')
    user_docs = users_ref.where('email', '==', email).get()
    if not user_docs:
        return jsonify({"error": "User not found"}), 404

    user_doc = user_docs[0]
    user_ref = user_doc.reference
    hashed_password = generate_password_hash(new_password)
    user_ref.update({'password': hashed_password})

    # Hapus token setelah digunakan
    db.collection('reset_tokens').document(token).delete()

    return jsonify({"message": "Password reset successfully"}), 200

@bp.route('/date', methods=['POST'])
def add_date_of_birth_and_phone():
    data = request.json
    username = data['username']
    date_of_birth = data['date_of_birth']  # Format tanggal lahir: "YYYY-MM-DD"
    phone_number = data['phone_number']   # Nomor telepon pengguna

    # Cari pengguna berdasarkan username
    users_ref = db.collection('users')
    user_docs = users_ref.where('username', '==', username).get()
    if len(user_docs) == 0:
        return jsonify({"error": "User not found"}), 404

    # Update tanggal lahir dan nomor telepon
    user_doc = user_docs[0]
    try:
        user_ref = user_doc.reference
        user_ref.update({
            "date_of_birth": date_of_birth,
            "phone_number": phone_number
        })
        return jsonify({"message": "Date of birth and phone number added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/add-user', methods=['POST'])
def add_user():
    """
    Route untuk menambahkan pengguna baru dengan error handling berbeda untuk setiap input.
    """
    data = request.json

    # Validasi setiap field
    if 'email' not in data or not data['email']:
        return jsonify({"error": "Email is required"}), 400
    if 'username' not in data or not data['username']:
        return jsonify({"error": "Username is required"}), 400
    if 'full_name' not in data or not data['full_name']:
        return jsonify({"error": "Full name is required"}), 400
    if 'password' not in data or not data['password']:
        return jsonify({"error": "Password is required"}), 400
    if 'confirm_password' not in data or not data['confirm_password']:
        return jsonify({"error": "Confirm password is required"}), 400
    if 'date_of_birth' not in data or not data['date_of_birth']:
        return jsonify({"error": "Date of birth is required"}), 400
    if 'phone_number' not in data or not data['phone_number']:
        return jsonify({"error": "Phone number is required"}), 400

    email = data['email']
    username = data['username']
    full_name = data['full_name']
    password = data['password']
    confirm_password = data['confirm_password']
    date_of_birth = data['date_of_birth']
    phone_number = data['phone_number']

    # Validasi format email
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({"error": "Invalid email format"}), 400

    # Validasi panjang username
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters long"}), 400

    # Validasi panjang password
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    # Validasi kesesuaian password dan confirm password
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Validasi format tanggal lahir (YYYY-MM-DD)
    try:
        from datetime import datetime
        datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Validasi panjang nomor telepon
    if not phone_number.isdigit() or len(phone_number) < 10:
        return jsonify({"error": "Invalid phone number. Must contain at least 10 digits"}), 400

    # Periksa apakah email atau username sudah ada
    users_ref = db.collection('users')
    existing_email = users_ref.where('email', '==', email).get()
    if len(existing_email) > 0:
        return jsonify({"error": "Email already exists"}), 400

    existing_username = users_ref.where('username', '==', username).get()
    if len(existing_username) > 0:
        return jsonify({"error": "Username already exists"}), 400

    # Hash password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Buat data pengguna
    user_data = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "password": hashed_password,
        "date_of_birth": date_of_birth,
        "phone_number": phone_number
    }

    try:
        # Tambahkan pengguna ke Firestore
        users_ref.add(user_data)
        return jsonify({"message": "User added successfully", "user": user_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
import traceback

@bp.route('/articles', methods=['GET'])
def get_articles():
    try:
        # Ambil query dan page_size dari parameter URL
        query = request.args.get('query', 'kesehatan ibu hamil')  # Default query adalah "kehamilan"
        page_size = int(request.args.get('page_size', 5))  # Jumlah artikel, default 5
        url = f"https://newsapi.org/v2/everything?q={query}&language=id&apiKey={NEWS_API_KEY}&pageSize={page_size}"

        # Ambil artikel dari NewsAPI
        response = requests.get(url)
        data = response.json()

        # Cek jika response dari API berhasil dan mengandung artikel
        if response.status_code != 200 or 'articles' not in data:
            return jsonify({'error': 'Failed to fetch articles', 'details': data}), response.status_code

        # Format artikel
        articles = [
            {
                "title": article.get('title', 'No Title'),
                "description": article.get('description', 'No Description'),
                "url": article.get('url', 'No URL'),
                "source": article.get('source', {}).get('name', 'Unknown Source')
            }
            for article in data['articles']
        ]

        # Kembalikan response JSON
        return jsonify({
            "query": query,
            "articles": articles
        })

    except Exception as e:
        # Log error detail
        print(f"Error occurred: {str(e)}")
        print(traceback.format_exc())  # Tampilkan traceback untuk debugging

        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@bp.route('/faq', methods=['GET'])
def get_faq():
    try:
        # Ambil parameter dari URL
        category = request.args.get('category')
        search = request.args.get('search')

        # Data FAQ statis untuk contoh
        faq_data = [
            {"question": "Apa makanan sehat untuk ibu hamil?", "answer": "Makan sayur dan buah.", "category": "nutrisi"},
            {"question": "Apakah ibu hamil boleh olahraga?", "answer": "Boleh, dengan intensitas ringan.", "category": "olahraga"},
            {"question": "Apa tanda bahaya kehamilan?", "answer": "Nyeri hebat atau pendarahan.", "category": "kesehatan"}
        ]

        # Filter berdasarkan kategori (case-insensitive)
        filtered_faq = faq_data
        if category:
            filtered_faq = [faq for faq in filtered_faq if faq['category'].lower() == category.lower()]

        # Filter berdasarkan kata kunci di pertanyaan (case-insensitive)
        if search:
            filtered_faq = [faq for faq in filtered_faq if search.lower() in faq['question'].lower()]

        # Jika tidak ada hasil
        if not filtered_faq:
            return jsonify({
                "status": "error",
                "message": "FAQ tidak ditemukan untuk kategori atau kata kunci yang diberikan."
            }), 404

        # Kembalikan hasil pencarian
        return jsonify({
            "status": "success",
            "faqs": filtered_faq
        }), 200

    except Exception as e:
        # Tangani error dengan pesan jelas
        print(f"Error occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Terjadi kesalahan saat memproses permintaan.",
            "details": str(e)
        }), 500
