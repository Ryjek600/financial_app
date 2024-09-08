from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from models import User

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Please try again.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")



