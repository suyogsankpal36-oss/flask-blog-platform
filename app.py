from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Home Page
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


# Single Post Page
@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


# Create Post
@app.route('/create', methods=['GET', 'POST'])
def create_post():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        # Validation
        if not title or not content:
            flash("Title and Content are required!")
            return redirect(url_for('create_post'))

        new_post = Post(
            title=title,
            content=content
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Post Created Successfully!")
        return redirect(url_for('home'))

    return render_template('create.html')


# Edit Post
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):

    post = Post.query.get_or_404(id)

    if request.method == 'POST':

        post.title = request.form['title']
        post.content = request.form['content']

        if not post.title or not post.content:
            flash("Fields cannot be empty!")
            return redirect(url_for('edit_post', id=id))

        db.session.commit()

        flash("Post Updated Successfully!")
        return redirect(url_for('home'))

    return render_template('edit.html', post=post)


# Delete Post
@app.route('/delete/<int:id>')
def delete_post(id):

    post = Post.query.get_or_404(id)

    db.session.delete(post)
    db.session.commit()

    flash("Post Deleted Successfully!")
    return redirect(url_for('home'))


# Create Database
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)