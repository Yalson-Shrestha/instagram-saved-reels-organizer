from flask import Flask, render_template, request, redirect
from models import db, Reel, Category
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    reels = Reel.query.order_by(Reel.date_added.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('index.html', reels=reels, categories=categories)

@app.route('/add', methods=['GET', 'POST'])
def add_reel():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        url = request.form['url']
        title = request.form['title']
        category_id = request.form['category_id']
        tags = request.form['tags']

        new_reel = Reel(
            url=url,
            title=title,
            category_id=category_id,
            tags=tags,
            date_added=datetime.now()
        )
        db.session.add(new_reel)
        db.session.commit()
        return redirect('/')
    return render_template('add_reel.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        if not Category.query.filter_by(name=name).first():
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
        return redirect('/')
    return render_template('add_category.html')

@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Delete associated reels first
    Reel.query.filter_by(category_id=category.id).delete()
    db.session.delete(category)
    db.session.commit()
    return redirect('/')

@app.route('/category/<int:category_id>')
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    reels = category.reels
    return render_template('category.html', reels=reels, category=category.name)

@app.route('/delete/<int:reel_id>', methods=['POST'])
def delete_reel(reel_id):
    reel = Reel.query.get_or_404(reel_id)
    db.session.delete(reel)
    db.session.commit()
    return redirect(request.referrer or '/')

if __name__ == '__main__':
    app.run(debug=True)
