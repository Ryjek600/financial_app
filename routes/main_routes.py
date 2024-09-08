from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for('main.login'))
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('main.register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}")
            return redirect(url_for('main.register'))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful.")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('main.login'))

    return render_template("login.html")

@main.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect(url_for('main.index'))

@main.route("/results")
def results():
    return render_template("results.html")








