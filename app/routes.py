from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import firestore

bp = Blueprint('routes', __name__)
db = firestore.client()

@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    email = data['email']

    # Periksa apakah pengguna sudah ada
    users_ref = db.collection('users')
    existing_user = users_ref.where('email', '==', email).get()
    if len(existing_user) > 0:  # Periksa jika sudah ada pengguna dengan email yang sama
        return jsonify({"error": "Email already exists"}), 400

    # Tambahkan pengguna baru
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user_data = {
        "name": data['name'],
        "email": email,
        "password": hashed_password
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
    if len(user_docs) == 0:  # Tidak ditemukan pengguna dengan email tersebut
        return jsonify({"error": "Invalid credentials"}), 401

    user = user_docs[0].to_dict()
    if not check_password_hash(user['password'], password):  # Verifikasi password
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": {"name": user['name'], "email": user['email']}}), 200

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data['email']

    # Cari pengguna berdasarkan email
    users_ref = db.collection('users')
    user_docs = users_ref.where('email', '==', email).get()
    if len(user_docs) == 0:  # Jika email tidak ditemukan
        return jsonify({"error": "Email not found"}), 404

    # Buat tautan reset password (mocked)
    reset_link = f"http://localhost:8080/reset-password?email={email}"
    return jsonify({"message": "Reset link sent", "reset_link": reset_link}), 200



