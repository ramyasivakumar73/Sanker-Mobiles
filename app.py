from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from models import db, User, Admin, Product
from config import Config
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import string

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    if session.get('is_admin'):
        return Admin.query.get(int(user_id))
    return User.query.get(int(user_id))

# Create DB and Admin if not exists
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@sankermobiles.com', phone='9876543210')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# --- CONTEXT PROCESSOR ---
@app.context_processor
def inject_globals():
    return dict(is_admin=session.get('is_admin', False))

# --- USER ROUTES ---

@app.route('/')
@login_required
def index():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    categories = [
        "Mobiles", "AirPods", "Back Covers", "Chargers", "Wires",
        "Bluetooth Adapters", "Power Banks", "Smart Watches", "Speakers",
        "Memory Cards", "Pen Drives", "Tripods", "Selfie Sticks"
    ]
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('user/index.html', products=products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == identifier) | 
            (User.email == identifier) | 
            (User.phone == identifier)
        ).first()
        
        if user and user.check_password(password):
            session['is_admin'] = False
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('user/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            new_user = User(username=username, email=email, phone=phone)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
    return render_template('user/register.html')

@app.route('/logout')
@login_required
def logout():
    redirect_to = url_for('admin_login') if session.get('is_admin') else url_for('login')
    session.pop('is_admin', None)
    logout_user()
    return redirect(redirect_to)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        user = User.query.filter(
            (db.func.lower(User.email) == identifier.lower()) | 
            (User.phone == identifier)
        ).first()
        
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.session.commit()
            session['reset_user_id'] = user.id
            session['is_admin_reset'] = False
            
            if app.config.get('DEMO_MODE'):
                flash(f'DEBUG: Your Reset OTP is {otp}', 'info')
            
            try:
                msg = Message('Sanker Mobiles Account - Your Reset OTP',
                             recipients=[user.email])
                msg.body = f'Hello {user.username},\n\nYour OTP for password reset is: {otp}\n\nThanks,\nSanker Mobiles Team'
                mail.send(msg)
                flash(f'OTP sent to your email: {user.email}', 'success')
            except Exception as e:
                print(f"SMTP Error: {e}")
                flash('Could not send email, but you can continue if in demo mode.', 'warning')
            
            return redirect(url_for('verify_otp'))
        flash('Account not found.', 'error')
    return render_template('user/forgot.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    is_admin_reset = session.get('is_admin_reset', False)
    user_id = session.get('admin_reset_id' if is_admin_reset else 'reset_user_id')
    
    if not user_id:
        return redirect(url_for('admin_forgot_password' if is_admin_reset else 'forgot_password'))
        
    if request.method == 'POST':
        otp = request.form.get('otp')
        user = Admin.query.get(user_id) if is_admin_reset else User.query.get(user_id)
        
        if user and user.otp == otp and user.otp_expiry > datetime.utcnow():
            flash('OTP Verified! Create your new password.', 'success')
            return redirect(url_for('reset_password'))
        flash('Invalid/Expired OTP', 'error')
            
    return render_template('admin/verify_otp.html' if is_admin_reset else 'user/verify_otp.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    is_admin_reset = session.get('is_admin_reset', False)
    user_id = session.get('admin_reset_id' if is_admin_reset else 'reset_user_id')
    
    if not user_id:
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        user = Admin.query.get(user_id) if is_admin_reset else User.query.get(user_id)
        
        if user:
            user.set_password(password)
            user.otp = None
            user.otp_expiry = None
            db.session.commit()
            session.pop('admin_reset_id', None)
            session.pop('reset_user_id', None)
            flash('Password reset successful!', 'success')
            return redirect(url_for('admin_login' if is_admin_reset else 'login'))
            
    return render_template('user/reset.html')

# --- ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['is_admin'] = True
            login_user(admin)
            flash('Admin Login Successful', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials', 'error')
    return render_template('admin/login.html')

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        admin = Admin.query.filter((Admin.username == identifier) | (Admin.email == identifier)).first()
        if admin:
            otp = ''.join(random.choices(string.digits, k=6))
            admin.otp = otp
            admin.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.session.commit()
            session['admin_reset_id'] = admin.id
            session['is_admin_reset'] = True
            
            if app.config.get('DEMO_MODE'):
                flash(f'DEBUG: Admin OTP is {otp}', 'info')
            
            try:
                msg = Message('Admin Reset OTP', recipients=[admin.email])
                msg.body = f'Your Admin OTP is: {otp}'
                mail.send(msg)
                flash('OTP sent to admin email.', 'success')
            except:
                flash('Demo Mode: OTP generated.', 'warning')
            return redirect(url_for('verify_otp'))
    return render_template('admin/forgot.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/dashboard.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not session.get('is_admin'): return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        price = float(request.form.get('price'))
        discount = float(request.form.get('discount', 0))
        fixed_discount = float(request.form.get('fixed_discount', 0))
        category = request.form.get('category')
        description = request.form.get('description')
        stock = int(request.form.get('stock', 0))
        
        image_url = request.form.get('image_url')
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('static', filename='images/' + filename)

        new_product = Product(
            name=name, brand=brand, price=price, discount=discount,
            fixed_discount=fixed_discount, category=category,
            description=description, stock=stock, image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    categories = ["Mobiles", "AirPods", "Back Covers", "Chargers", "Wires", "Power Banks", "Smart Watches", "Speakers"]
    return render_template('admin/product_form.html', categories=categories, action="Add")

@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not session.get('is_admin'): return redirect(url_for('login'))
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.brand = request.form.get('brand')
        product.price = float(request.form.get('price'))
        product.discount = float(request.form.get('discount', 0))
        product.category = request.form.get('category')
        product.stock = int(request.form.get('stock', 0))
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    categories = ["Mobiles", "AirPods", "Back Covers", "Chargers", "Wires", "Power Banks", "Smart Watches", "Speakers"]
    return render_template('admin/product_form.html', product=product, categories=categories, action="Edit")

@app.route('/admin/product/delete/<int:id>')
@login_required
def delete_product(id):
    if not session.get('is_admin'): return redirect(url_for('login'))
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
