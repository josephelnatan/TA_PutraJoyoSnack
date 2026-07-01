from flask import Flask, render_template, request, redirect, session
from config import Config
from models.user import db, User

# KONFIGURASI: Arahkan template ke folder 'Frontend' sesuai instruksi tugas
app = Flask(__name__)

# Konfigurasi Database & Session Secure Key
app.config['SECRET_KEY'] = 'putrajoyosnack_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///putra_joyo_snack.db' # Menggunakan SQLite lokal agar langsung jalan tanpa ribet setting cloud
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========================================================
# 1. MODEL DATABASE (Sesuai Rekomendasi Dosen)
# ========================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False) # Admin, Kasir, Staf Gudang

class Barang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_barang = db.Column(db.String(100), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    satuan = db.Column(db.String(20), nullable=False) # Pcs, Pack, Bal, Dus
    tanggal_masuk = db.Column(db.String(20), nullable=False) # Tanggal masuk stok
    tanggal_kadaluarsa = db.Column(db.String(20), nullable=False) # Tanggal Expired
    id_admin_fk = db.Column(db.String(50), nullable=False) # Otomatis mencatat siapa yang input

# ========================================================
# 2. RUTE HALAMAN (ROUTES)
# ========================================================

# Rute Utama: Otomatis Lempar ke Login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Rute Login Otomatis Deteksi Role dari Database (Tanpa Dropdown)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            # Harmonisasi string role (samakan dengan huruf di database/enum)
            if user.role.lower() == "admin":
                return redirect("/admin/dashboard")
            elif user.role.lower() == "kasir":
                return redirect("/kasir/dashboard")
            elif user.role.lower() == "staf gudang" or user.role.lower() == "gudang":
                return redirect("/gudang/dashboard")

        return render_template("login.html", error="Username atau Password Salah")

    # Diarahkan ke folder admin/login.html sesuai struktur direktori tugas
    return render_template("login.html")


# Rute Dashboard Admin
@app.route('/admin/dashboard')
def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")
        
    if session.get("role").lower() != "admin":
        return "Akses Ditolak: Anda bukan Admin", 403

    # Mengembalikan file HTML asli, bukan string teks polos lagi
    return render_template("admin/dashboard.html")
# ==================== ROUTE SUB-MENU ADMIN ====================
@app.route("/admin/barang")
def admin_barang():
    if request.method == 'POST':
        # Ambil data dari form barang.html
        nama = request.form['nama_barang']
        harga = request.form['harga']
        stok = request.form['stok']
        satuan = request.form['satuan']
        tgl_masuk = request.form['tanggal_masuk']
        tgl_expired = request.form['tanggal_kadaluarsa']
        
        # Fitur Auto-Capture Admin: Mengambil nama admin yang sedang login dari session
        penginput = session.get('username', 'Unknown Admin')
        
        # Simpan ke database
        barang_baru = Barang(
            nama_barang=nama, harga=harga, stok=stok, satuan=satuan,
            tanggal_masuk=tgl_masuk, tanggal_kadaluarsa=tgl_expired, id_admin_fk=penginput
        )
        db.session.add(barang_baru)
        db.session.commit()
        return redirect(url_for('admin_barang'))
        
    return render_template('admin/barang.html')

# Rute User Management
@app.route('/admin/user')
def admin_user():
    return render_template('admin/user.html')

# Rute Laporan
@app.route('/admin/laporan')
def admin_laporan():
    return render_template('admin/laporan.html')

# Rute Kritik & Saran
@app.route('/admin/kritik')
def admin_kritik():
    return render_template('admin/kritik.html')

# ==================== KASIR ====================
@app.route("/kasir/dashboard")
def kasir_dashboard():
    if "user_id" not in session:
        return redirect("/login")
        
    if session.get("role").lower() != "kasir":
        return "Akses Ditolak: Anda bukan Kasir", 403

    # Ganti dengan path template halaman transaksi utama milik kasir nanti
    return render_template("utama/index.html", mode="kasir")


# ==================== GUDANG ====================
@app.route("/gudang/dashboard")
def gudang_dashboard():
    if "user_id" not in session:
        return redirect("/login")
        
    if session.get("role").lower() not in ["gudang", "staf gudang"]:
        return "Akses Ditolak: Anda bukan Staff Gudang", 403

    # Ganti dengan path template halaman kelola stok milik gudang nanti
    return render_template("utama/index.html", mode="gudang")


# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)