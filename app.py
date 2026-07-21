from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'tani_toko_secret_key_bebas_diisi'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kelompok_tani (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelompok TEXT NOT NULL,
            nama_ketua TEXT NOT NULL,
            lokasi TEXT NOT NULL,
            no_hp TEXT NOT NULL
        )
    ''')
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

init_db()

# --- KATALOG PUBLIK ---
@app.route('/')
def index():
    conn = get_db_connection()
    query = '''
        SELECT produk.*, kelompok_tani.nama_kelompok, kelompok_tani.lokasi, kelompok_tani.no_hp 
        FROM produk 
        JOIN kelompok_tani ON produk.tani_id = kelompok_tani.id
    '''
    produk_list = conn.execute(query).fetchall()
    conn.close()
    return render_template('index.html', produk_list=produk_list)

# --- LOGIN & LOGOUT ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['logged_in'] = True
            flash('Selamat datang kembali, Admin!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password tidak valid!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Berhasil keluar dari sistem.', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD ADMIN (TANPA CRUD - HANYA STATISTIK & GRAFIK) ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    total_petani = conn.execute('SELECT COUNT(*) FROM kelompok_tani').fetchone()[0]
    total_produk = conn.execute('SELECT COUNT(*) FROM produk').fetchone()[0]
    total_stok = conn.execute('SELECT SUM(stok) FROM produk').fetchone()[0] or 0
    
    # Ambil data statistik per kategori untuk Grafik Chart.js
    kat_data = conn.execute('SELECT kategori, COUNT(*) as jumlah FROM produk GROUP BY kategori').fetchall()
    categories = [row['kategori'] for row in kat_data]
    counts = [row['jumlah'] for row in kat_data]

    # Produk dengan stok terendah (peringatan stok)
    stok_rendah = conn.execute('SELECT nama_produk, stok FROM produk ORDER BY stok ASC LIMIT 5').fetchall()
    
    conn.close()
    return render_template('dashboard.html', 
                           total_petani=total_petani, 
                           total_produk=total_produk, 
                           total_stok=total_stok,
                           categories=categories,
                           counts=counts,
                           stok_rendah=stok_rendah)

# --- HALAMAN KHUSUS KELOLA DATA (CRUD) ---
@app.route('/kelola_data')
def kelola_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    petani_list = conn.execute('SELECT * FROM kelompok_tani').fetchall()
    query_produk = '''
        SELECT produk.*, kelompok_tani.nama_kelompok 
        FROM produk 
        JOIN kelompok_tani ON produk.tani_id = kelompok_tani.id
    '''
    produk_list = conn.execute(query_produk).fetchall()
    conn.close()
    return render_template('kelola_data.html', petani_list=petani_list, produk_list=produk_list)

# --- PROSES CRUD ---
@app.route('/tambah_tani', methods=['POST'])
def tambah_tani():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('INSERT INTO kelompok_tani (nama_kelompok, nama_ketua, lokasi, no_hp) VALUES (?, ?, ?, ?)',
                 (request.form['nama_kelompok'], request.form['nama_ketua'], request.form['lokasi'], request.form['no_hp']))
    conn.commit()
    conn.close()
    flash('Kelompok Tani berhasil ditambahkan!', 'success')
    return redirect(url_for('kelola_data'))

@app.route('/hapus_tani/<int:id>')
def hapus_tani(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM kelompok_tani WHERE id = ?', (id,))
    conn.execute('DELETE FROM produk WHERE tani_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Data Kelompok Tani dihapus!', 'warning')
    return redirect(url_for('kelola_data'))

@app.route('/tambah_produk', methods=['POST'])
def tambah_produk():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('INSERT INTO produk (tani_id, nama_produk, kategori, harga, stok) VALUES (?, ?, ?, ?, ?)',
                 (request.form['tani_id'], request.form['nama_produk'], request.form['kategori'], request.form['harga'], request.form['stok']))
    conn.commit()
    conn.close()
    flash('Produk hasil tani berhasil ditambahkan!', 'success')
    return redirect(url_for('kelola_data'))

@app.route('/hapus_produk/<int:id>')
def hapus_produk(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM produk WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Produk berhasil dihapus!', 'warning')
    return redirect(url_for('kelola_data'))

if __name__ == '__main__':
    app.run(debug=True)