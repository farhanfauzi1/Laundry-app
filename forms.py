from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FloatField, DateTimeField, DateField, TimeField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User
import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PlaceOrderForm(FlaskForm):
    service = SelectField('Layanan', validators=[DataRequired()], coerce=int)
    pickup_date = DateField('Tanggal Pengambilan', validators=[DataRequired()])
    pickup_time = TimeField('Waktu Pengambilan', validators=[DataRequired()], default=datetime.time(9, 0))
    delivery_address = TextAreaField('Alamat Pengiriman', validators=[DataRequired()])
    submit = SubmitField('Buat Pesanan')

class UpdateOrderForm(FlaskForm):
    weight = FloatField('Berat (kg)', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ])
    pickup_datetime = DateTimeField('Tanggal & Waktu Jemput', validators=[Optional()])
    address = StringField('Alamat', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Update Pesanan')

class AddServiceForm(FlaskForm):
    name = StringField('Nama Layanan', validators=[DataRequired(), Length(min=2, max=100)])
    price_per_kg = DecimalField('Harga per Kg', validators=[DataRequired()], places=2)
    description = TextAreaField('Deskripsi')
    submit = SubmitField('Tambahkan Layanan')

class PaymentForm(FlaskForm):
    payment_method = SelectField('Metode Pembayaran', choices=[
        ('cash', 'Tunai'),
        ('transfer', 'Transfer Bank'),
        ('ewallet', 'E-Wallet')
    ], validators=[DataRequired()])
    submit = SubmitField('Bayar Sekarang')