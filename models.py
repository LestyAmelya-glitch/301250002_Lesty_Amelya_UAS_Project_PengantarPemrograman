from db import get_db


def status_stok(stok):
    if stok <= 0:
        return "Habis"
    elif stok <= 5:
        return "Menipis"
    return "Tersedia"


# ---------- ADMIN ----------

def get_admin_by_username(username):
    db = get_db()
    return db.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()


def create_admin(username, password_hash):
    db = get_db()
    db.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    db.commit()


def count_admin():
    db = get_db()
    return db.execute("SELECT COUNT(*) AS total FROM admin").fetchone()["total"]


# ---------- PRODUK ----------

def get_all_produk(kategori=None, keyword=None):
    db = get_db()
    query = "SELECT * FROM produk WHERE 1=1"
    params = []
    if kategori:
        query += " AND kategori = ?"
        params.append(kategori)
    if keyword:
        query += " AND nama_produk LIKE ?"
        params.append(f"%{keyword}%")
    query += " ORDER BY created_at DESC"
    return db.execute(query, params).fetchall()


def get_all_kategori():
    db = get_db()
    rows = db.execute("SELECT DISTINCT kategori FROM produk ORDER BY kategori").fetchall()
    return [row["kategori"] for row in rows]


def get_produk_by_id(produk_id):
    db = get_db()
    return db.execute("SELECT * FROM produk WHERE id = ?", (produk_id,)).fetchone()


def create_produk(data):
    db = get_db()
    db.execute(
        """
        INSERT INTO produk (nama_produk, kategori, nama_petani, harga, stok, satuan, deskripsi, foto_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["nama_produk"], data["kategori"], data["nama_petani"], data["harga"],
            data["stok"], data["satuan"], data["deskripsi"], data["foto_url"],
        ),
    )
    db.commit()


def update_produk(produk_id, data):
    db = get_db()
    db.execute(
        """
        UPDATE produk
        SET nama_produk = ?, kategori = ?, nama_petani = ?, harga = ?, stok = ?,
            satuan = ?, deskripsi = ?, foto_url = ?
        WHERE id = ?
        """,
        (
            data["nama_produk"], data["kategori"], data["nama_petani"], data["harga"],
            data["stok"], data["satuan"], data["deskripsi"], data["foto_url"], produk_id,
        ),
    )
    db.commit()


def update_stok(produk_id, stok_baru):
    db = get_db()
    db.execute("UPDATE produk SET stok = ? WHERE id = ?", (stok_baru, produk_id))
    db.commit()


def delete_produk(produk_id):
    db = get_db()
    db.execute("DELETE FROM produk WHERE id = ?", (produk_id,))
    db.commit()


def count_produk():
    db = get_db()
    return db.execute("SELECT COUNT(*) AS total FROM produk").fetchone()["total"]


def rekap_produk_per_kategori():
    db = get_db()
    return db.execute(
        "SELECT kategori, COUNT(*) AS jumlah FROM produk GROUP BY kategori"
    ).fetchall()


# ---------- PESANAN ----------

def create_pesanan(produk_id, nama_pembeli, kontak_pembeli, alamat_pembeli, jumlah, total_harga):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO pesanan (produk_id, nama_pembeli, kontak_pembeli, alamat_pembeli, jumlah, total_harga)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (produk_id, nama_pembeli, kontak_pembeli, alamat_pembeli, jumlah, total_harga),
    )
    db.commit()
    return cursor.lastrowid


def get_pesanan_by_id(pesanan_id):
    db = get_db()
    return db.execute(
        """
        SELECT pesanan.*, produk.nama_produk, produk.satuan
        FROM pesanan JOIN produk ON pesanan.produk_id = produk.id
        WHERE pesanan.id = ?
        """,
        (pesanan_id,),
    ).fetchone()


def get_all_pesanan(status=None):
    db = get_db()
    query = """
        SELECT pesanan.*, produk.nama_produk, produk.satuan
        FROM pesanan JOIN produk ON pesanan.produk_id = produk.id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND pesanan.status = ?"
        params.append(status)
    query += " ORDER BY pesanan.tanggal_pesan DESC"
    return db.execute(query, params).fetchall()


def get_recent_pesanan(limit=5):
    db = get_db()
    return db.execute(
        """
        SELECT pesanan.*, produk.nama_produk, produk.satuan
        FROM pesanan JOIN produk ON pesanan.produk_id = produk.id
        ORDER BY pesanan.tanggal_pesan DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def update_status_pesanan(pesanan_id, status_baru):
    db = get_db()
    db.execute("UPDATE pesanan SET status = ? WHERE id = ?", (status_baru, pesanan_id))
    db.commit()


def count_pesanan():
    db = get_db()
    return db.execute("SELECT COUNT(*) AS total FROM pesanan").fetchone()["total"]


def count_pesanan_by_status(status):
    db = get_db()
    return db.execute(
        "SELECT COUNT(*) AS total FROM pesanan WHERE status = ?", (status,)
    ).fetchone()["total"]


def total_pendapatan_selesai():
    db = get_db()
    row = db.execute(
        "SELECT SUM(total_harga) AS total FROM pesanan WHERE status = 'Selesai'"
    ).fetchone()
    return row["total"] or 0
