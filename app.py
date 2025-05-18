from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Reel, Category
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    reels = Reel.query.join(Category).filter(Category.user_id == current_user.id).order_by(Reel.date_added.desc()).all()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('index.html', reels=reels, categories=categories)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_reel():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    if request.method == 'POST':
        url = request.form['url']
        title = request.form['title']
        category_id = request.form['category_id']
        tags = request.form['tags']
        new_reel = Reel(url=url, title=title, category_id=category_id, tags=tags, date_added=datetime.now())
        db.session.add(new_reel)
        db.session.commit()
        return redirect('/')
    return render_template('add_reel.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        if not Category.query.filter_by(name=name, user_id=current_user.id).first():
            new_category = Category(name=name, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
        return redirect('/')
    return render_template('add_category.html')

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        return "Unauthorized", 403
    Reel.query.filter_by(category_id=category.id).delete()
    db.session.delete(category)
    db.session.commit()
    return redirect('/')

@app.route('/category/<int:category_id>')
@login_required
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        return "Unauthorized", 403
    reels = category.reels
    return render_template('category.html', reels=reels, category=category.name)

@app.route('/delete/<int:reel_id>', methods=['POST'])
@login_required
def delete_reel(reel_id):
    reel = Reel.query.get_or_404(reel_id)
    if reel.category.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(reel)
    db.session.commit()
    return redirect(request.referrer or '/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            error = "Invalid username or password."
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

