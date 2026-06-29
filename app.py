from flask import Flask, render_template, request, redirect, session
from config import Config
from models.user import db, User

# KONFIGURASI: Arahkan template ke folder 'Frontend' sesuai instruksi tugas
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# ==================== HOME ====================
@app.route("/")
def home():
    return redirect("/login")


# ==================== LOGIN ====================
@app.route("/login", methods=["GET", "POST"])
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


# ==================== ADMIN ====================
@app.route("/admin/dashboard")
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
    if "user_id" not in session:
        return redirect("/login")
    return render_template("admin/barang.html")

@app.route("/admin/user")
def admin_user():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("admin/user.html")

@app.route("/admin/laporan")
def admin_laporan():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("admin/laporan.html")

@app.route("/admin/kritik")
def admin_kritik():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("admin/kritik.html")

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
    return redirect("/login")


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)