import unittest

from app import app, db, Barang


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


if __name__ == "__main__":
    unittest.main()
