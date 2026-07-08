import unittest

from app import app, db, Barang
from models.pengiriman import Pengiriman
from models.user import User


class AppFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite://")
        self.client = self.app.test_client()

    def test_admin_barang_page_shows_items_and_delete_works(self):
        with self.app.app_context():
            Barang.query.delete()
            db.session.commit()

            barang = Barang(
                nama_barang="Test Snack",
                harga=12000,
                stok=10,
                satuan="Pcs",
                tanggal_masuk="2026-07-01",
                tanggal_kadaluarsa="2026-12-31",
                id_admin_fk="admin",
            )
            db.session.add(barang)
            db.session.commit()
            item_id = barang.id

        response = self.client.get("/admin/barang")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Snack", response.data)

        delete_response = self.client.get(f"/admin/barang/hapus/{item_id}", follow_redirects=True)
        self.assertEqual(delete_response.status_code, 200)

        with self.app.app_context():
            self.assertIsNone(Barang.query.get(item_id))

    def test_admin_can_edit_existing_barang(self):
        with self.app.app_context():
            Barang.query.delete()
            db.session.commit()

            barang = Barang(
                nama_barang="Old Snack",
                harga=10000,
                stok=5,
                satuan="Pcs",
                tanggal_masuk="2026-07-01",
                tanggal_kadaluarsa="2026-12-31",
                id_admin_fk="admin",
            )
            db.session.add(barang)
            db.session.commit()
            item_id = barang.id

        response = self.client.post(
            f"/admin/barang/edit/{item_id}",
            data={
                "nama_barang": "Updated Snack",
                "harga": "15000",
                "stok": "8",
                "satuan": "Pack",
                "tanggal_masuk": "2026-07-02",
                "tanggal_kadaluarsa": "2026-12-30",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            updated = Barang.query.get(item_id)
            self.assertEqual(updated.nama_barang, "Updated Snack")
            self.assertEqual(updated.harga, 15000)
            self.assertEqual(updated.stok, 8)
            self.assertEqual(updated.satuan, "Pack")

    def test_admin_dashboard_shows_real_summary(self):
        with self.app.app_context():
            Barang.query.delete()
            User.query.delete()
            db.session.commit()

            db.session.add(User(username="admin", password="admin", role="admin"))
            db.session.add(Barang(nama_barang="Keripik", harga=12000, stok=2, satuan="Pcs", tanggal_masuk="2026-07-01", tanggal_kadaluarsa="2026-08-01", id_admin_fk="admin"))
            db.session.add(Barang(nama_barang="Kacang", harga=8000, stok=8, satuan="Pack", tanggal_masuk="2026-07-02", tanggal_kadaluarsa="2026-09-01", id_admin_fk="admin"))
            db.session.commit()

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "admin"
            sess["role"] = "admin"

        response = self.client.get("/admin/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Total Barang", response.data)
        self.assertIn(b"Stok Menipis", response.data)
        self.assertIn(b"Keripik", response.data)

    def test_kasir_can_add_pengiriman(self):
        with self.app.app_context():
            Pengiriman.query.delete()
            db.session.commit()

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "kasir"
            sess["role"] = "kasir"

        response = self.client.post(
            "/kasir/pengiriman",
            data={
                "no_pengiriman": "PG004",
                "tanggal_input": "2026-07-01",
                "nama_penerima": "Pak Damar",
                "barang": "Kacang",
                "jumlah": "15",
                "status": "Diproses",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            saved = Pengiriman.query.filter_by(no_pengiriman="PG004").first()
            self.assertIsNotNone(saved)
            self.assertEqual(saved.nama_penerima, "Pak Damar")
            self.assertEqual(saved.jumlah, 15)

    def test_kasir_can_edit_and_delete_pengiriman(self):
        with self.app.app_context():
            Pengiriman.query.delete()
            db.session.commit()
            pengiriman = Pengiriman(
                no_pengiriman="PG005",
                tanggal_input="01-07-2026",
                nama_penerima="Pak Rudi",
                barang="Kacang",
                jumlah=8,
                status="Diproses",
            )
            db.session.add(pengiriman)
            db.session.commit()
            item_id = pengiriman.id

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "kasir"
            sess["role"] = "kasir"

        edit_response = self.client.post(
            f"/kasir/pengiriman/edit/{item_id}",
            data={
                "no_pengiriman": "PG005",
                "tanggal_input": "2026-07-02",
                "nama_penerima": "Pak Rudi Baru",
                "barang": "Kacang Salted",
                "jumlah": "10",
                "status": "Dikirim",
            },
            follow_redirects=True,
        )
        self.assertEqual(edit_response.status_code, 200)

        with self.app.app_context():
            updated = Pengiriman.query.get(item_id)
            self.assertEqual(updated.nama_penerima, "Pak Rudi Baru")
            self.assertEqual(updated.barang, "Kacang Salted")
            self.assertEqual(updated.status, "Dikirim")

        delete_response = self.client.get(f"/kasir/pengiriman/hapus/{item_id}", follow_redirects=True)
        self.assertEqual(delete_response.status_code, 200)

        with self.app.app_context():
            self.assertIsNone(Pengiriman.query.get(item_id))

    def test_gudang_dashboard_is_accessible_for_staff(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 2
            sess["username"] = "gudang"
            sess["role"] = "staf gudang"

        response = self.client.get("/gudang/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard Staff Gudang", response.data)

    def test_kasir_retur_page_is_accessible(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 3
            sess["username"] = "kasir"
            sess["role"] = "kasir"

        response = self.client.get("/kasir/retur")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Retur Barang", response.data)


if __name__ == "__main__":
    unittest.main()
