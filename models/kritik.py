from flask_sqlalchemy import SQLAlchemy

from models.user import db


class Kritik(db.Model):
    __tablename__ = "kritik"

    id = db.Column(db.Integer, primary_key=True)

    tanggal = db.Column(db.String(20), nullable=False)  # format: dd-mm-YYYY
    nama_pelanggan = db.Column(db.String(120), nullable=False)
    feedback = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Belum Diproses",
    )

