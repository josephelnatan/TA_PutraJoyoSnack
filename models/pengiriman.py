from flask_sqlalchemy import SQLAlchemy

from models.user import db


class Pengiriman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_pengiriman = db.Column(db.String(20), unique=True, nullable=False)
    tanggal_input = db.Column(db.String(20), nullable=False)
    nama_penerima = db.Column(db.String(100), nullable=False)
    barang = db.Column(db.String(100), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Diproses")
