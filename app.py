from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import inspect
from datetime import datetime
import random
from models import db, Admin, Menu, Orders  # Impor model dari models.py

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi koneksi ke MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://nuranisa:NURANISATOKOAPP07@viaduct.proxy.rlwy.net:3306/restaurant_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database dan migrasi
db.init_app(app)
migrate = Migrate(app, db)

# Fungsi untuk menambahkan data ke tabel
def seed_data():
    with app.app_context():
        if Admin.query.first() is None:
            # Tambahkan 10 data ke tabel admin
            for i in range(1, 11):
                admin = Admin(username=f"admin{i}", password=f"password{i}")
                db.session.add(admin)

            # Tambahkan 10 data ke tabel menu
            categories = ['Food', 'Drink', 'Dessert']
            for i in range(1, 11):
                menu = Menu(
                    name=f"Menu Item {i}",
                    category=random.choice(categories),
                    description=f"Description for Menu Item {i}",
                    price=random.randint(10000, 50000)
                )
                db.session.add(menu)

            # Tambahkan 10 data ke tabel orders
            for i in range(1, 11):
                order = Orders(
                    menu_id=random.randint(1, 10),
                    quantity=random.randint(1, 5)
                )
                db.session.add(order)

            db.session.commit()
            print("Data berhasil ditambahkan.")

            for menu in menus:
                if menu.image is None:
                    menu.image = 'default.jpg'

# Buat tabel dan tambahkan data jika tabel belum ada
@app.before_request
def setup():
    if not inspect(db.engine).has_table('admin'):
        db.create_all()
        seed_data()

@app.cli.command('setup_db')
def setup_db():
    """Setup database dan tambahkan seed data."""
    db.create_all()
    seed_data()
    print("Database dan seed data berhasil dibuat.")

# Route Halaman Login Admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['loggedin'] = True
            session['id'] = admin.id
            session['username'] = admin.username
            return redirect(url_for('dashboard'))
        else:
            msg = 'Username atau password salah!'
    return render_template('admin/login.html', msg=msg)

# Route Dashboard Admin
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('admin/dashboard.html', username=session['username'])
    return redirect(url_for('login'))

# CRUD Menu
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if 'loggedin' in session:  # Hanya bisa diakses jika sudah login sebagai admin
        menus = Menu.query.all()
        return render_template('menu/data_menu.html', menus=menus)
    return redirect(url_for('login'))  # Redirect ke login jika belum login


@app.route('/menu_user', methods=['GET'])
def menu_user():
    menus = Menu.query.all()  # Mengambil semua menu dari database
    return render_template('menu/data_menu_user.html', menus=menus)


@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            category = request.form['category']
            description = request.form['description']
            price = request.form['price']
            menu = Menu(name=name, category=category, description=description, price=price)
            db.session.add(menu)
            db.session.commit()
            flash('Menu berhasil ditambahkan!')
            return redirect(url_for('menu'))
        return render_template('menu/data_menu_tambah.html')
    return redirect(url_for('login'))

@app.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    if 'loggedin' in session:
        menu = Menu.query.get_or_404(id)
        if request.method == 'POST':
            menu.name = request.form['name']
            menu.category = request.form['category']
            menu.description = request.form['description']
            menu.price = request.form['price']
            db.session.commit()
            flash('Menu berhasil diperbarui!')
            return redirect(url_for('menu'))
        return render_template('menu/data_menu_edit.html', menu=menu)
    return redirect(url_for('login'))

@app.route('/menu/delete/<int:id>', methods=['GET', 'POST'])
def delete_menu(id):
    if 'loggedin' in session:
        menu = Menu.query.get_or_404(id)
        db.session.delete(menu)
        db.session.commit()
        flash('Menu berhasil dihapus!')
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

# Halaman Beranda User
@app.route('/')
def index():
    menus = Menu.query.all()
    return render_template('index_user.html')

# Halaman Tentang
@app.route('/about')
def about():
    menus = Menu.query.all()
    return render_template('about.html', menus=menus)

# Halaman Keranjang dan Transaksi
@app.route('/cart')
def cart():
    # Ambil data keranjang dari session
    cart_items = session.get('orders', [])
    
    # Kirimkan data cart ke template
    return render_template('cart.html', cart_items=cart_items)

@app.route('/remove_from_cart/<menu_id>', methods=['POST'])
def remove_from_cart(menu_id):
    cart_items = session.get('cart', [])
    
    # Filter untuk menghapus item yang sesuai dengan menu_id
    session['cart'] = [item for item in cart_items if item['menu_id'] != menu_id]
    
    session.modified = True  # Memastikan perubahan disimpan
    return redirect(url_for('cart'))

@app.route('/transaksi', methods=['GET','POST'])
def transaksi():
    if request.method == 'POST':
        pass
    # Ambil cart dari session
    cart_items = session.get('orders', [])
    
    # Hitung total harga semua item dalam keranjang
    total = sum(item['total_price'] for item in cart_items)
    
    # Kirimkan total harga ke halaman checkout
    return render_template('transaksi.html', cart_items=cart_items, total=total)

# Proses Pemesanan
@app.route('/order', methods=['POST'])
def order():
    if request.method == 'POST':
        menu_id = request.form['menu_id']
        quantity = request.form['quantity']
        order = Orders(menu_id=menu_id, quantity=quantity)
        db.session.add(order)
        db.session.commit()
        flash('Pesanan berhasil dibuat!')
        return redirect(url_for('about'))

# Fungsi Keranjang Belanja
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    menu_id = request.form['menu_id']
    menu_name = request.form['menu_name']
    menu_price = int(request.form['menu_price'])
    quantity = int(request.form['quantity'])

    # Membuat pesanan baru
    total_price = menu_price * quantity
    order = {
        'id': menu_id,
        'menu_name': menu_name,
        'quantity': quantity,
        'total_price': total_price
    }

    # Jika keranjang sudah ada di session, tambahkan pesanan
    if 'orders' not in session:
        session['orders'] = []

    session['orders'].append(order)

    # Menyimpan session
    session.modified = True

    return redirect(url_for('cart_session'))

@app.route('/cart_session')
def cart_session():
    orders = session.get('orders', [])
    return render_template('cart.html', orders=orders)

@app.route('/clear_cart')
def clear_cart():
    # Menghapus semua pesanan dari keranjang di session
    session.pop('orders', None)  # Menghapus key 'orders' jika ada
    session.modified = True
    return redirect(url_for('cart_session'))  # Mengarahkan kembali ke halaman keranjang


# Buat tabel dan tambahkan data jika tabel belum ada
@app.before_request
def setup():
    # Cek apakah tabel 'admin' ada
    if not inspect(db.engine).has_table('admin'):
        # Proses jika tabel 'admin' tidak ada
        db.create_all()
        seed_data()

@app.cli.command('setup_db')
def setup_db():
    """Setup database dan tambahkan seed data."""
    db.create_all()
    seed_data()
    print("Database dan seed data berhasil dibuat.")

if __name__ == '__main__':
    app.run(debug=True)
