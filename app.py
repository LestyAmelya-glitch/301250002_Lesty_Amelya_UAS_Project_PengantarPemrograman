from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_bebas_diisi'

# Fungsi koneksi ke SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inisialisasi Database & Tabel
def init_db():
    conn = get_db_connection()
    # Tabel Kelompok Tani
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kelompok_tani (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelompok TEXT NOT NULL,
            nama_ketua TEXT NOT NULL,
            lokasi TEXT NOT NULL,
            no_hp TEXT NOT NULL
        )
    ''')
    # Tabel Produk Hasil Tani
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tani_id INTEGER,
            nama_produk TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL,
            FOREIGN KEY (tani_id) REFERENCES kelompok_tani (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTE PUBLIK ----------------
@app.route('/')
def index():
    conn = get_db_connection()
    produk_list = conn.execute('''
        SELECT p.*, k.nama_kelompok, k.no_hp 
        FROM produk p 
        JOIN kelompok_tani k ON p.tani_id = k.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', produk_list=produk_list)

# ---------------- ROUTE AUTHENTICATION ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Default Admin: admin / admin123
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            flash('Login berhasil! Selamat datang Admin.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau Password salah!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# ---------------- ROUTE DASHBOARD ADMIN ----------------
@app.route('/admin/dashboard')
def dashboard():
    if not session.get('is_admin'):
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    total_petani = conn.execute('SELECT COUNT(*) FROM kelompok_tani').fetchone()[0]
    total_produk = conn.execute('SELECT COUNT(*) FROM produk').fetchone()[0]
    total_stok = conn.execute('SELECT SUM(stok) FROM produk').fetchone()[0] or 0
    
    petani_list = conn.execute('SELECT * FROM kelompok_tani').fetchall()
    produk_list = conn.execute('''
        SELECT p.*, k.nama_kelompok 
        FROM produk p 
        LEFT JOIN kelompok_tani k ON p.tani_id = k.id
    ''').fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                           total_petani=total_petani, 
                           total_produk=total_produk, 
                           total_stok=total_stok,
                           petani_list=petani_list,
                           produk_list=produk_list)

# ---------------- ROUTE CRUD (KELOMPOK TANI) ----------------
@app.route('/admin/tani/tambah', methods=['POST'])
def tambah_tani():
    if not session.get('is_admin'): return redirect(url_for('login'))
    nama = request.form['nama_kelompok']
    ketua = request.form['nama_ketua']
    lokasi = request.form['lokasi']
    no_hp = request.form['no_hp']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO kelompok_tani (nama_kelompok, nama_ketua, lokasi, no_hp) VALUES (?, ?, ?, ?)',
                 (nama, ketua, lokasi, no_hp))
    conn.commit()
    conn.close()
    flash('Data Kelompok Tani Berhasil Ditambahkan!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/tani/hapus/<int:id>')
def hapus_tani(id):
    if not session.get('is_admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM kelompok_tani WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Kelompok Tani Berhasil Dihapus!', 'danger')
    return redirect(url_for('dashboard'))

# ---------------- ROUTE CRUD (PRODUK) ----------------
@app.route('/admin/produk/tambah', methods=['POST'])
def tambah_produk():
    if not session.get('is_admin'): return redirect(url_for('login'))
    tani_id = request.form['tani_id']
    nama = request.form['nama_produk']
    kategori = request.form['kategori']
    harga = request.form['harga']
    stok = request.form['stok']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO produk (tani_id, nama_produk, kategori, harga, stok) VALUES (?, ?, ?, ?, ?)',
                 (tani_id, nama, kategori, harga, stok))
    conn.commit()
    conn.close()
    flash('Produk Berhasil Ditambahkan!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/produk/hapus/<int:id>')
def hapus_produk(id):
    if not session.get('is_admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM produk WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Produk Berhasil Dihapus!', 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)