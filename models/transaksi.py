from models.user import db
from datetime import datetime

class Barang(db.Model):
    __tablename__ = 'barang'
    id = db.Column(db.Integer, primary_key=True)
    nama_barang = db.Column(db.String(100), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    satuan = db.Column(db.String(20), nullable=False)
    tanggal_masuk = db.Column(db.String(20), nullable=False)
    tanggal_kadaluarsa = db.Column(db.String(20), nullable=False)
    id_admin_fk = db.Column(db.String(50), nullable=False)

class BarangMasuk(db.Model):
    __tablename__ = "barang_masuk"
    id = db.Column(db.Integer, primary_key=True)
    barang_id = db.Column(
        db.Integer,
        db.ForeignKey("barang.id"),
        nullable=False
    )
    supplier = db.Column(
        db.String(100),
        nullable=False
    )
    jumlah = db.Column(
        db.Integer,
        nullable=False
    )
    tanggal_masuk = db.Column(
        db.Date,
        nullable=False
    )
    tanggal_expired = db.Column(
        db.Date,
        nullable=False
    )
    gudang_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    barang = db.relationship("Barang")
    gudang = db.relationship("User")

class Transaksi(db.Model):
    __tablename__ = 'transaksi'
    id = db.Column(db.Integer, primary_key=True)
    kasir_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ← users
    total = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.now)
    kasir = db.relationship('User', backref='transaksi')

class DetailTransaksi(db.Model):
    __tablename__ = 'detail_transaksi'
    id = db.Column(db.Integer, primary_key=True)
    transaksi_id = db.Column(db.Integer, db.ForeignKey('transaksi.id'), nullable=False)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

class Retur(db.Model):
    __tablename__ = 'retur'
    id = db.Column(db.Integer, primary_key=True)
    id_retur = db.Column(db.String(10), unique=True)
    tanggal = db.Column(db.String(20))
    nama_barang = db.Column(db.String(100))
    jumlah = db.Column(db.Integer)
    alasan = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    kasir_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # ← users
    kasir = db.relationship('User', backref='retur')