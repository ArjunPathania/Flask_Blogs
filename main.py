import os
import smtplib
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, ContactForm, RegisterForm, LoginForm, CommentForm
from dotenv import load_dotenv, find_dotenv
from bleach import clean

# Load environment variables
load_dotenv(find_dotenv())

# Email configuration from environment variables
FROM_EMAIL = os.environ["FROM_EMAIL"]
PASSWORD = os.environ["PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'

# Flask extensions setup
ckeditor = CKEditor(app)
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
Bootstrap5(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Database models
class User(UserMixin, db.Model):
    """Model representing a user."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    """Model representing a blog post."""
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

class Comment(db.Model):
    """Model representing a comment on a blog post."""
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)

with app.app_context():
    db.create_all()

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Reload user from session."""
    return db.get_or_404(User, user_id)

# Decorators

def admin_only(f):
    """Decorator to restrict access to admin-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes

@app.route('/')
def get_all_posts():
    """Display all blog posts."""
    posts = db.session.scalars(db.select(BlogPost)).all()
    return render_template("index.html", all_posts=posts, current_user=current_user)

@app.route('/register', methods=["GET", "POST"])
def register():
    """Handle user registration."""
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form['email']
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user:
            flash("You've already signed up with that email, log in instead!", "info")
            return redirect(url_for('login'))

        if not request.form['password']:
            flash("Password cannot be empty.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(request.form['password'], method="pbkdf2:sha256", salt_length=8)
        new_user = User(email=email, name=request.form['name'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form, current_user=current_user)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']
        user = db.session.scalar(db.select(User).where(User.email == email))
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    """Log the user out."""
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/post/<int:post_id>', methods=["GET", "POST"])
@login_required
def show_post(post_id):
    """Display a specific post and handle comments."""
    post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    comments = db.session.scalars(db.select(Comment)).all()
    if form.validate_on_submit():
        sanitized_text = clean(
            form.comment.data,
            tags=['p', 'b', 'i', 'strong', 'ul', 'li', 'ol', 'a'],
            attributes={'a': ['href']}
        )
        new_comment = Comment(text=sanitized_text, comment_author=current_user, parent_post=post)
        db.session.add(new_comment)
        db.session.commit()
        return render_template("post.html", post=post, form=form, current_user=current_user, comments=comments)
    return render_template("post.html", post=post, form=form, current_user=current_user,comments = comments)

@app.route('/new-post', methods=["GET", "POST"])
@admin_only
def add_new_post():
    """Create a new blog post."""
    form = CreatePostForm()
    if form.validate_on_submit():
        sanitized_body = clean(
            form.body.data,
            tags=['p', 'b', 'i', 'strong', 'ul', 'li', 'ol', 'a'],
            attributes={'a': ['href']}
        )
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=sanitized_body,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, current_user=current_user)

@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    """Edit an existing blog post."""
    post = db.get_or_404(BlogPost, post_id)
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.body = clean(
            form.body.data,
            tags=['p', 'b', 'i', 'strong', 'ul', 'li', 'ol', 'a'],
            attributes={'a': ['href']}
        )
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template("make-post.html", form=form, is_edit=True, current_user=current_user)

@app.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    """Delete a blog post."""
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route('/about')
def about():
    """Render the about page."""
    return render_template("about.html", current_user=current_user)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    """Handle contact form submissions."""
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        flash("Message sent successfully!", "success")
        return render_template("contact.html", form=form, current_user=current_user, msg_sent=True)

    return render_template("contact.html", form=form, current_user=current_user, msg_sent=False)


def send_email(name, email, phone, message):
    """Send an email with contact form details."""
    email_message = f"Subject: New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(FROM_EMAIL, PASSWORD)
        connection.sendmail(FROM_EMAIL, TO_EMAIL, email_message)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    app.run(debug=True, port=port)
