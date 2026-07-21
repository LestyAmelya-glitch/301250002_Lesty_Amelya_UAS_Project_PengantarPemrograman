from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'tani_toko_secret_key_bebas_diisi'

# Fungsi Koneksi Database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inisialisasi Tabel Database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabel 1: Kelompok Tani
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kelompok_tani (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelompok TEXT NOT NULL,
            nama_ketua TEXT NOT NULL,
            lokasi TEXT NOT NULL,
            no_hp TEXT NOT NULL
        )
    ''')
    # Tabel 2: Produk Hasil Tani
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tani_id INTEGER NOT NULL,
            nama_produk TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL,
            FOREIGN KEY (tani_id) REFERENCES kelompok_tani (id)
        )
    ''')
    conn.commit()
    conn.close()

# Jalankan inisialisasi DB saat app start
init_db()

# --- HALAMAN PUBLIK ---
@app.route('/')
def index():
    conn = get_db_connection()
    # Ambil data produk beserta nama kelompok taninya
    query = '''
        SELECT produk.*, kelompok_tani.nama_kelompok, kelompok_tani.lokasi, kelompok_tani.no_hp 
        FROM produk 
        JOIN kelompok_tani ON produk.tani_id = kelompok_tani.id
    '''
    produk_list = conn.execute(query).fetchall()
    conn.close()
    return render_template('index.html', produk_list=produk_list)

# --- AUTHENTIKASI ADMIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Kredensial Login Admin Sederhana
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            flash('Login berhasil! Selamat datang Admin.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD ADMIN ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # Data Petani & Produk
    petani_list = conn.execute('SELECT * FROM kelompok_tani').fetchall()
    query_produk = '''
        SELECT produk.*, kelompok_tani.nama_kelompok 
        FROM produk 
        JOIN kelompok_tani ON produk.tani_id = kelompok_tani.id
    '''
    produk_list = conn.execute(query_produk).fetchall()
    
    # Statistik untuk Dashboard Admin
    total_petani = conn.execute('SELECT COUNT(*) FROM kelompok_tani').fetchone()[0]
    total_produk = conn.execute('SELECT COUNT(*) FROM produk').fetchone()[0]
    total_stok = conn.execute('SELECT SUM(stok) FROM produk').fetchone()[0] or 0
    
    conn.close()
    return render_template('dashboard.html', 
                           petani_list=petani_list, 
                           produk_list=produk_list, 
                           total_petani=total_petani, 
                           total_produk=total_produk, 
                           total_stok=total_stok)

# --- CRUD KELOMPOK TANI ---
@app.route('/tambah_tani', methods=['POST'])
def tambah_tani():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    nama_kelompok = request.form['nama_kelompok']
    nama_ketua = request.form['nama_ketua']
    lokasi = request.form['lokasi']
    no_hp = request.form['no_hp']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO kelompok_tani (nama_kelompok, nama_ketua, lokasi, no_hp) VALUES (?, ?, ?, ?)',
                 (nama_kelompok, nama_ketua, lokasi, no_hp))
    conn.commit()
    conn.close()
    flash('Data Kelompok Tani berhasil ditambahkan!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/hapus_tani/<int:id>')
def hapus_tani(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM kelompok_tani WHERE id = ?', (id,))
    conn.execute('DELETE FROM produk WHERE tani_id = ?', (id,)) # Hapus juga produk terkait
    conn.commit()
    conn.close()
    flash('Data Kelompok Tani dan produk terkait berhasil dihapus!', 'warning')
    return redirect(url_for('dashboard'))

# --- CRUD PRODUK ---
@app.route('/tambah_produk', methods=['POST'])
def tambah_produk():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    tani_id = request.form['tani_id']
    nama_produk = request.form['nama_produk']
    kategori = request.form['kategori']
    harga = request.form['harga']
    stok = request.form['stok']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO produk (tani_id, nama_produk, kategori, harga, stok) VALUES (?, ?, ?, ?, ?)',
                 (tani_id, nama_produk, kategori, harga, stok))
    conn.commit()
    conn.close()
    flash('Produk Hasil Tani berhasil ditambahkan!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/hapus_produk/<int:id>')
def hapus_produk(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM produk WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Produk berhasil dihapus!', 'warning')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)