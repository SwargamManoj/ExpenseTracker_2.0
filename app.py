from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ExpenseForm, LoginForm, ProfileUpdateForm, RegisterForm
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    expenses = db.relationship('Expense', backref='user', lazy=True)
    profile_picture = db.Column(db.String(200), default='default_profile.jpg')
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    total_expenses = sum(expense.amount for expense in expenses)
    user_details = {
    'username': current_user.username,
    'profile_picture': current_user.profile_picture if hasattr(current_user, 'profile_picture') and current_user.profile_picture else 'default_profile.jpg'
}
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses,user=user_details)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        new_expense = Expense(
            amount=form.amount.data, 
            category=form.category.data, 
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_expense.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

from werkzeug.utils import secure_filename
import os

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        profile_picture = request.files['profile_picture']
        filename = 'default_profile.jpg'  # Default profile picture
        if profile_picture:
            from werkzeug.utils import secure_filename
            filename = secure_filename(profile_picture.filename)
            # Configure the upload folder for profile pictures
            UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profiles')  # Relative path
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file to the configured upload folder
            profile_picture.save(upload_path)

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            profile_picture=filename
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reports')
@login_required
def reports():
    # Get expenses grouped by category
    category_expenses = db.session.query(
        Expense.category, 
        db.func.sum(Expense.amount).label('total_amount')
    ).filter(Expense.user_id == current_user.id) \
     .group_by(Expense.category) \
     .all()

    # Convert to list of dictionaries for easier template rendering
    category_totals = [
        {
            'category': category, 
            'total_amount': float(total)
        } 
        for category, total in category_expenses
    ]
    
    # Calculate total expenses
    total_expenses = sum(item['total_amount'] for item in category_totals)

    # Debugging print statements
    print("Category Totals:", category_totals)
    print("Total Expenses:", total_expenses)
    
    return render_template(
        'reports.html', 
        category_totals=category_totals, 
        total_expenses=total_expenses
    )
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Update user details
        if form.full_name.data:
            current_user.full_name = form.full_name.data
        
        if form.email.data:
            current_user.email = form.email.data
        
        if form.bio.data:
            current_user.bio = form.bio.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            current_user.set_profile_picture(form.profile_picture.data)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)