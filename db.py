import os
import sqlite3

from flask import g

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "marketplace_tani.db")


def get_db():
    if "db" not in g:
        os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_produk TEXT NOT NULL,
            kategori TEXT NOT NULL,
            nama_petani TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER NOT NULL DEFAULT 0,
            satuan TEXT NOT NULL DEFAULT 'kg',
            deskripsi TEXT,
            foto_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produk_id INTEGER NOT NULL,
            nama_pembeli TEXT NOT NULL,
            kontak_pembeli TEXT NOT NULL,
            alamat_pembeli TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            total_harga REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Menunggu Konfirmasi',
            tanggal_pesan TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (produk_id) REFERENCES produk (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
