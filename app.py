from flask import Flask, render_template, request, redirect, session, jsonify
from config import Config
from models.user import db, User
from datetime import datetime
from models.transaksi import Barang, BarangMasuk
from sqlalchemy import func
from datetime import datetime
from models.transaksi import (
    Barang,
    BarangMasuk,
    Transaksi,
    DetailTransaksi,
    Retur,
    Pengiriman
)


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

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            if user.role.lower() == "admin":
                return redirect("/admin/dashboard")
            elif user.role.lower() == "kasir":
                return redirect("/kasir/dashboard")
            elif user.role.lower() in ["staf gudang", "gudang"]:
                return redirect("/gudang/dashboard")

        return render_template("login.html", error="Username atau Password Salah")

    return render_template("login.html")


# ==================== ADMIN ====================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role").lower() != "admin":
        return "Akses Ditolak: Anda bukan Admin", 403
    return render_template("admin/dashboard.html")

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
    return render_template("kasir/dashboard.html")

@app.route("/kasir/transaksi", methods=["GET", "POST"])
def kasir_transaksi():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        data = request.get_json()
        items = data.get("items", [])
        kasir_id = session["user_id"]  # Ambil dari session, bukan client

        total = 0
        for item in items:
            barang = Barang.query.get(item["barang_id"])
            if not barang:
                return jsonify({"error": f"Barang ID {item['barang_id']} tidak ditemukan"}), 404
            if barang.stok < item["qty"]:
                return jsonify({"error": f"Stok {barang.nama_barang} tidak cukup"}), 400
            total += barang.harga * item["qty"]

        transaksi = Transaksi(kasir_id=kasir_id, total=total)
        db.session.add(transaksi)
        db.session.flush()

        for item in items:
            barang = Barang.query.get(item["barang_id"])
            detail = DetailTransaksi(
                transaksi_id=transaksi.id,
                barang_id=item["barang_id"],
                qty=item["qty"],
                subtotal=barang.harga * item["qty"]
            )
            barang.stok -= item["qty"]
            db.session.add(detail)

        db.session.commit()
        return jsonify({"success": True, "total": total})

    barang_list = Barang.query.filter(Barang.stok > 0).all()
    return render_template("kasir/transaksi.html", barang_list=barang_list)

@app.route("/kasir/retur", methods=["GET", "POST"])
def kasir_retur():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        retur = Retur(
            id_retur=request.form.get("id_retur"),
            tanggal=request.form.get("tanggal"),
            nama_barang=request.form.get("barang"),
            jumlah=request.form.get("jumlah"),
            alasan=request.form.get("alasan"),
            status=request.form.get("status", "Pending"),
            kasir_id=session["user_id"]
        )
        db.session.add(retur)
        db.session.commit()
        return redirect("/kasir/retur")

    retur_list = Retur.query.order_by(Retur.tanggal.desc()).all()
    return render_template("kasir/retur.html", retur_list=retur_list)

@app.route("/kasir/pengiriman", methods=["GET", "POST"])
def kasir_pengiriman():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        pengiriman = Pengiriman(
            no_pengiriman=request.form.get("no_pengiriman"),
            tanggal=request.form.get("tanggal"),
            nama_penerima=request.form.get("nama_penerima"),
            nama_barang=request.form.get("barang"),
            jumlah=request.form.get("jumlah"),
            status=request.form.get("status", "Diproses"),
            kasir_id=session["user_id"]
        )
        db.session.add(pengiriman)
        db.session.commit()
        return redirect("/kasir/pengiriman")

    pengiriman_list = Pengiriman.query.order_by(Pengiriman.tanggal.desc()).all()
    return render_template("kasir/pengiriman.html", pengiriman_list=pengiriman_list)


# ==================== GUDANG ====================
@app.route("/gudang/dashboard")
def gudang_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    # Barang masuk bulan ini
    barang_masuk = BarangMasuk.query.filter(
        func.month(BarangMasuk.tanggal_masuk) == datetime.now().month,
        func.year(BarangMasuk.tanggal_masuk) == datetime.now().year
    ).all()

    total_masuk = sum(x.jumlah for x in barang_masuk)

    # Total stok tersedia
    total_stok = db.session.query(
        func.sum(Barang.stok)
    ).scalar() or 0

    # Barang keluar bulan ini
    detail = DetailTransaksi.query.all()

    total_keluar = sum(x.qty for x in detail)

    return render_template(
        "gudang/dashboard.html",
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        total_stok=total_stok
    )

@app.route("/gudang/barang-masuk", methods=["GET", "POST"])
def gudang_barang_masuk():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        barang_id = request.form["barang_id"]
        supplier = request.form["supplier"]
        jumlah = int(request.form["jumlah"])
        tanggal_masuk = datetime.strptime(
            request.form["tanggal_masuk"],
            "%Y-%m-%d"
        ).date()

        tanggal_expired = datetime.strptime(
            request.form["tanggal_expired"],
            "%Y-%m-%d"
        ).date()

        data = BarangMasuk(
            barang_id=barang_id,
            supplier=supplier,
            jumlah=jumlah,
            tanggal_masuk=tanggal_masuk,
            tanggal_expired=tanggal_expired,
            gudang_id=session["user_id"]
        )

        db.session.add(data)

        barang = Barang.query.get(barang_id)
        barang.stok += jumlah

        db.session.commit()

        return redirect("/gudang/barang-masuk")

    barang = Barang.query.all()

    histori = BarangMasuk.query.order_by(
        BarangMasuk.id.desc()
    ).all()

    return render_template(
        "gudang/barang_masuk.html",
        barang=barang,
        histori=histori
    )

@app.route("/gudang/barang-masuk/hapus/<int:id>")
def hapus_barang_masuk(id):

    if "user_id" not in session:
        return redirect("/login")

    data = BarangMasuk.query.get_or_404(id)

    barang = Barang.query.get(data.barang_id)

    barang.stok -= data.jumlah

    db.session.delete(data)

    db.session.commit()

    return redirect("/gudang/barang-masuk")

@app.route("/gudang/barang-masuk/edit/<int:id>", methods=["GET", "POST"])
def edit_barang_masuk(id):

    if "user_id" not in session:
        return redirect("/login")

    data = BarangMasuk.query.get_or_404(id)

    if request.method == "POST":

        # Barang lama
        barang_lama = Barang.query.get(data.barang_id)

        # Kembalikan stok lama
        barang_lama.stok -= data.jumlah

        # Ambil data baru
        barang_baru = Barang.query.get(int(request.form["barang_id"]))

        data.barang_id = barang_baru.id
        data.supplier = request.form["supplier"]
        data.jumlah = int(request.form["jumlah"])
        data.tanggal_masuk = request.form["tanggal_masuk"]
        data.tanggal_expired = request.form["tanggal_expired"]

        # Tambahkan stok baru
        barang_baru.stok += data.jumlah

        db.session.commit()

        return redirect("/gudang/barang-masuk")

    barang_list = Barang.query.all()

    return render_template(
        "gudang/edit_barang_masuk.html",
        data=data,
        barang_list=barang_list
    )

@app.route("/gudang/laporan-stok")
def gudang_laporan_stok():

    if "user_id" not in session:
        return redirect("/login")

    keyword = request.args.get("keyword", "")

    if keyword:
        barang = Barang.query.filter(
            Barang.nama_barang.like(f"%{keyword}%")
        ).all()
    else:
        barang = Barang.query.all()

    return render_template(
        "gudang/laporan_stok.html",
        barang=barang,
        keyword=keyword
    )


# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)