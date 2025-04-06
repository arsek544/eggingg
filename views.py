from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Game
import os
from werkzeug.utils import secure_filename

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('profile'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        avatar = request.files['avatar']
        if avatar:
            filename = secure_filename(avatar.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar.save(path)
            current_user.avatar = filename
            db.session.commit()
    return render_template('profile.html')

@app.route('/topup', methods=['POST'])
@login_required
def topup():
    amount = float(request.form['amount'])
    current_user.balance += amount
    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/buy/<int:game_id>')
@login_required
def buy(game_id):
    game = Game.query.get(game_id)
    if game and game not in current_user.games and current_user.balance >= game.price:
        current_user.balance -= game.price
        current_user.games.append(game)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/library')
@login_required
def library():
    return render_template('library.html', games=current_user.games)
