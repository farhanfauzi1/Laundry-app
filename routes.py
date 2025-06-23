from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db
from app.forms import RegistrationForm, LoginForm, PlaceOrderForm, UpdateOrderForm, AddServiceForm, PaymentForm
from app.models import User, Order, Service, Payment
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from functools import wraps

# Dekorator untuk memeriksa peran pengguna (admin)
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rute Umum ---
@app.route('/')
@app.route('/home')
def home():
    services = Service.query.all()
    return render_template('index.html', title='Beranda', services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='customer') # Default role customer
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Anda sekarang dapat masuk.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Daftar', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login berhasil!', 'success')
            if user.role == 'admin':
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('customer_dashboard'))
        else:
            flash('Login gagal. Periksa email dan kata sandi Anda.', 'danger')
    return render_template('login.html', title='Masuk', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('home'))

# --- Rute Admin ---
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    # Mengambil 10 pesanan terbaru, diurutkan berdasarkan order_date
    latest_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           title='Dashboard Admin',
                           total_users=total_users,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           latest_orders=latest_orders)

@app.route('/admin/manage_services', methods=['GET', 'POST'])
@admin_required
def manage_services():
    form = AddServiceForm()
    if form.validate_on_submit():
        service = Service(name=form.name.data, price_per_kg=form.price_per_kg.data, description=form.description.data)
        db.session.add(service)
        db.session.commit()
        flash(f'Layanan "{service.name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('manage_services'))
    
    services = Service.query.all()
    return render_template('admin/manage_services.html', title='Kelola Layanan', services=services, form=form)

@app.route('/admin/add_service', methods=['GET', 'POST'])
@admin_required
def add_service():
    form = AddServiceForm()
    if form.validate_on_submit():
        service = Service(name=form.name.data, price_per_kg=form.price_per_kg.data, description=form.description.data)
        db.session.add(service)
        db.session.commit()
        flash(f'Layanan "{service.name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('manage_services'))
    return render_template('admin/add_service.html', title='Tambah Layanan Baru', form=form)

@app.route('/admin/edit_service/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = AddServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.price_per_kg = form.price_per_kg.data
        service.description = form.description.data
        db.session.commit()
        flash(f'Layanan "{service.name}" berhasil diperbarui.', 'success')
        return redirect(url_for('manage_services'))
    return render_template('admin/edit_service.html', title='Edit Layanan', form=form, service=service)

@app.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash(f'Layanan "{service.name}" berhasil dihapus.', 'info')
    return redirect(url_for('manage_services'))

@app.route('/admin/manage_users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', title='Kelola Pengguna', users=users)

@app.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Anda tidak bisa mengubah peran Anda sendiri.', 'warning')
        return redirect(url_for('manage_users'))

    if user.role == 'admin':
        user.role = 'customer'
        flash(f'Peran {user.username} diubah menjadi pelanggan.', 'info')
    else:
        user.role = 'admin'
        flash(f'Peran {user.username} diubah menjadi admin.', 'success')
    db.session.commit()
    return redirect(url_for('manage_users'))

@app.route('/admin/add_admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='admin')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Admin {user.username} berhasil ditambahkan.', 'success')
        return redirect(url_for('manage_users'))
    return render_template('admin/add_admin.html', title='Tambah Admin Baru', form=form)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Anda tidak bisa menghapus akun Anda sendiri.', 'warning')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Pengguna {user.username} berhasil dihapus.', 'info')
    return redirect(url_for('manage_users'))

@app.route('/admin/manage_orders')
@admin_required
def manage_orders():
    status_filter = request.args.get('status')
    orders_query = Order.query

    if status_filter and status_filter.lower() not in ['all', 'semua']:
        orders_query = orders_query.filter_by(status=status_filter)

    orders = orders_query.order_by(Order.order_date.desc()).all()

    return render_template('admin/manage_orders.html', 
                           title='Kelola Pesanan', 
                           orders=orders, 
                           status_filter=status_filter)

@app.route('/admin/update_order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = UpdateOrderForm(obj=order)
    
    if form.validate_on_submit():
        # Update field-field dari form
        order.status = form.status.data
        order.weight = form.weight.data
        order.pickup_datetime = form.pickup_datetime.data
        order.address = form.address.data
        
        # Hitung total harga berdasarkan berat × harga per kg
        if order.weight and order.service:
            order.total_price = order.weight * order.service.price_per_kg
        else:
            order.total_price = None
        
        db.session.commit()
        flash('Pesanan berhasil diperbarui!', 'success')
        return redirect(url_for('manage_orders'))
    
    return render_template('admin/update_order.html', title='Perbarui Pesanan', form=form, order=order)

@app.route('/admin/delete_order/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Pesanan berhasil dihapus.', 'info')
    return redirect(url_for('manage_orders'))

# --- Rute Pelanggan ---
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('home'))
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('customer/dashboard.html', title='Dashboard Pelanggan', orders=orders)

@app.route('/customer/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    if current_user.role != 'customer':
        flash('Anda tidak memiliki izin untuk membuat pesanan.', 'danger')
        return redirect(url_for('home'))
    form = PlaceOrderForm()
    # Mengisi pilihan layanan dari database
    form.service.choices = [(s.id, s.name) for s in Service.query.all()]
    if form.validate_on_submit():
        selected_service = Service.query.get(form.service.data)
        
        # Gabungkan pickup_date dan pickup_time
        pickup_datetime = datetime.combine(form.pickup_date.data, form.pickup_time.data)
        
        order = Order(
            user_id=current_user.id,
            service_id=selected_service.id,
            pickup_datetime=pickup_datetime,
            address=form.delivery_address.data,
            status='Pending',
            weight=None,
            total_price=None
        )
        db.session.add(order)
        db.session.commit()
        flash('Pesanan Anda berhasil dibuat dan menunggu konfirmasi!', 'success')
        return redirect(url_for('customer_dashboard'))
    return render_template('customer/place_order.html', title='Buat Pesanan', form=form)

@app.route('/customer/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    # Pastikan hanya pengguna yang bersangkutan atau admin yang bisa melihat detail
    if order.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    return render_template('customer/order_detail.html', title=f'Detail Pesanan #{order.id}', order=order)

@app.route('/customer/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)

    if order.status == 'Pending':
        order.status = 'Cancelled'
        db.session.commit()
        flash('Pesanan Anda telah dibatalkan.', 'info')
    else:
        flash('Pesanan tidak dapat dibatalkan pada status ini.', 'warning')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer/order/<int:order_id>/checkout', methods=['GET', 'POST'])
@login_required
def checkout(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    
    # Pastikan pesanan memiliki total_price dan status memungkinkan pembayaran
    if not order.total_price or order.status not in ['Pending', 'Processing', 'Completed']:
        flash('Pesanan tidak siap untuk pembayaran.', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))

    form = PaymentForm()
    if form.validate_on_submit():
        # Cek apakah sudah ada pembayaran untuk order ini
        existing_payment = Payment.query.filter_by(order_id=order.id).first()
        if existing_payment:
            flash('Pesanan ini sudah memiliki pembayaran.', 'warning')
            return redirect(url_for('order_detail', order_id=order.id))
        
        payment = Payment(
            order_id=order.id,
            amount=order.total_price,
            method=form.payment_method.data,
            status='Paid'
        )
        db.session.add(payment)
        order.status = 'Processing'
        db.session.commit()
        flash('Pembayaran berhasil diproses!', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    # PERBAIKAN: Ubah path template menjadi customer/checkout.html
    return render_template('customer/checkout.html', title=f'Checkout Pesanan #{order.id}', form=form, order=order)

# Rute untuk order history (jika diperlukan)
@app.route('/order/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    # Pastikan hanya pengguna yang bersangkutan atau admin yang bisa melihat detail
    if order.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    return render_template('order_history.html', title=f'Detail Pesanan #{order.id}', order=order)