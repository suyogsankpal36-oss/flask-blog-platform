from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# ==============================
# DATABASE CONFIG (VERCEL FIX)
# ==============================

if os.environ.get("VERCEL"):
    database_path = "/tmp/blog.db"
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(BASE_DIR, "blog.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==============================
# DATABASE MODEL
# ==============================

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)


# ==============================
# SINGLE POST PAGE
# ==============================

@app.route("/post/<int:id>")
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)


# ==============================
# CREATE POST
# ==============================

@app.route("/create", methods=["GET", "POST"])
def create_post():

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content required!")
            return redirect(url_for("create_post"))

        new_post = Post(
            title=title,
            content=content
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!")
        return redirect(url_for("home"))

    return render_template("create.html")


# ==============================
# EDIT POST
# ==============================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):

    post = Post.query.get_or_404(id)

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Fields cannot be empty!")
            return redirect(url_for("edit_post", id=id))

        post.title = title
        post.content = content

        db.session.commit()

        flash("Post updated successfully!")
        return redirect(url_for("home"))

    return render_template("edit.html", post=post)


# ==============================
# DELETE POST
# ==============================

@app.route("/delete/<int:id>")
def delete_post(id):

    post = Post.query.get_or_404(id)

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully!")

    return redirect(url_for("home"))


# ==============================
# CREATE DATABASE
# ==============================

with app.app_context():
    db.create_all()


# VERCEL EXPORT
app = app


if __name__ == "__main__":
    app.run()