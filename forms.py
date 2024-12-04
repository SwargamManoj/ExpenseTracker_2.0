from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Food', 'Food'), 
        ('Transportation', 'Transportation'), 
        ('Utilities', 'Utilities'), 
        ('Entertainment', 'Entertainment'), 
        ('Other', 'Other')
    ], validators=[DataRequired()])
    description = StringField('Description', validators=[Length(max=200)])
    submit = SubmitField('Add Expense')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message="Passwords must match")
    ])
    profile_picture = FileField('Profile Picture')  # New field
    submit = SubmitField('Register')
    
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ProfileUpdateForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        Optional(), 
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Email', validators=[
        Optional(), 
        Email(message='Invalid email address')
    ])
    bio = TextAreaField('Bio', validators=[
        Optional(), 
        Length(max=500, message='Bio must be less than 500 characters')
    ])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')