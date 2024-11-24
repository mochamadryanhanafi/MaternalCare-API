from firebase_admin import credentials, firestore, initialize_app

# Muat kredensial dari file serviceAccountKey.json
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)

# Sambungkan ke Firestore
db = firestore.client()

# Tambahkan dokumen ke koleksi 'maternalcaredb'
doc_ref = db.collection("maternalcaredb").document("user1")
doc_ref.set({"name": "Jane Doe", "email": "janedoe@example.com"})

print("Dokumen berhasil ditambahkan ke Firestore!")
