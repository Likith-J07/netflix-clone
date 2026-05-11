from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, get_s3_client
from app.models import User, Video, WatchHistory
from app.recommendation import get_recommendations
from config import Config

import uuid

main = Blueprint('main', __name__)


@main.route('/')
def index():

    videos = Video.query.all()

    return render_template('index.html', videos=videos)


@main.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')

        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for('main.profiles'))

        flash('Invalid email or password!')

    return render_template('login.html')


@main.route('/profiles')
@login_required
def profiles():

    return render_template('profiles.html')


@main.route('/dashboard')
@login_required
def dashboard():

    videos = Video.query.all()

    recommendations = get_recommendations(current_user.id)

    return render_template(
        'dashboard.html',
        videos=videos,
        recommendations=recommendations
    )


@main.route('/watch/<int:video_id>')
@login_required
def watch(video_id):

    video = Video.query.get_or_404(video_id)

    history = WatchHistory(
        user_id=current_user.id,
        video_id=video_id
    )

    db.session.add(history)
    db.session.commit()

    return render_template('watch.html', video=video)


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        genre = request.form['genre']

        video_file = request.files['video']
        thumbnail_file = request.files['thumbnail']

        s3 = get_s3_client()

        # Upload video
        video_key = f"videos/{uuid.uuid4()}.mp4"

        s3.upload_fileobj(
            video_file,
            Config.AWS_BUCKET_NAME,
            video_key,
            ExtraArgs={
                'ContentType': 'video/mp4'
            }
        )

        # Upload thumbnail
        thumbnail_key = f"thumbnails/{uuid.uuid4()}.jpg"

        s3.upload_fileobj(
            thumbnail_file,
            Config.AWS_BUCKET_NAME,
            thumbnail_key,
            ExtraArgs={
                'ContentType': 'image/jpeg'
            }
        )

        video_url = f"https://{Config.AWS_BUCKET_NAME}.s3.{Config.AWS_REGION}.amazonaws.com/{video_key}"

        thumbnail_url = f"https://{Config.AWS_BUCKET_NAME}.s3.{Config.AWS_REGION}.amazonaws.com/{thumbnail_key}"

        video = Video(
            title=title,
            description=description,
            genre=genre,
            video_url=video_url,
            thumbnail_url=thumbnail_url
        )

        db.session.add(video)
        db.session.commit()

        flash('Video uploaded successfully!')

        return redirect(url_for('main.dashboard'))

    return render_template('upload.html')


@main.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('main.index'))