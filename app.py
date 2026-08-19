import os
from contextlib import contextmanager
from functools import wraps
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from db_setup import Base, Book, Author, User
from custom_exception import WikiParseError

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = 'login'

db = SQLAlchemy(app)
api = Api(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv('DB_PATH', 'books.db')
engine = create_engine(f'sqlite:///{DB_PATH}?check_same_thread=False')
Base.metadata.bind = engine
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db() as session:
            return func(session, *args, **kwargs)
    return wrapper


@login.user_loader
@with_session
def load_user(db, user_id):
    return db.query(User).get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        with get_db() as db:
            user = db.query(User).filter_by(name=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        with get_db() as db:
            user = db.query(User).filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')


def redirect_to_index_if_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/sign_in', methods=['GET', 'POST'])
@with_session
def login(db):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.query(User).filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('sign_in.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@redirect_to_index_if_authenticated
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


from views import *
from api import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
