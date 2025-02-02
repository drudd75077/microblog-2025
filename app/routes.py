from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os
from PIL import Image
import secrets
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, UploadForm
from app.models import User

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    posts = [
        {'author':user, 'body':'Test post #1'},
        {'author':user, 'body':'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts, image_file=image_file)

def save_picture(form_picture):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        filename = secure_filename(form.file.data.filename)
        if filename:
            image_name = current_user.image_file
            picture_file = save_picture(form.file.data)
            current_user.image_file = picture_file
            db.session.commit()
            os.remove(os.path.join(app.root_path, 'static/profile_pics', image_name))
            image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        current_user.about_me = form.about_me.data
        current_user.username = form.username.data
        db.session.commit()
        flash(f"Your changes have been saved.")
        return render_template('upload.html', form=form, filename=filename, current_user=current_user, title='Edit Profile', image_file=image_file)
    else:
        try:
            image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        except:
            image_file = url_for('static', filename='profile_pics/default.jpg')
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        return render_template('upload.html', form=form, title='Edit Profile', image_file=image_file)
     



