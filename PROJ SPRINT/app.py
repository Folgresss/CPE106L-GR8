from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime

app = Flask(__name__)

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)  # Needed for flash messages & sessions

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)  # New field

    def __repr__(self):
        return f"<Deadline {self.title} - {'Completed' if self.completed else 'Pending'}>"

    user = db.relationship("User", backref=db.backref("deadlines", lazy=True))

@app.route("/", methods=["GET", "POST"])
def signup():
    if "user_id" in session:  # If already logged in, redirect to dashboard
        flash("You are already signed in!", "info")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))  # Redirect to login instead of error

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        # Hash password and save user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Sign-up successful! 🎉 Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# Route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id  # Store user ID in session
            session["user_name"] = user.name  # Store user name in session
            flash(f"Welcome back, {user.name}! 🎉", "success")
            return redirect(url_for("dashboard"))  # Redirect to dashboard
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_deadlines = Deadline.query.filter_by(user_id=user_id).all()

    # Calculate progress
    total_deadlines = len(user_deadlines)
    completed_deadlines = sum(1 for deadline in user_deadlines if deadline.completed)
    progress = (completed_deadlines / total_deadlines) * 100 if total_deadlines > 0 else 0

    return render_template("dashboard.html", name=session["user_name"], progress=progress)

# Route for logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Route to add a deadline
@app.route("/add_deadline", methods=["GET", "POST"])
def add_deadline():
    if "user_id" not in session:
        flash("Please log in to add deadlines.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        due_date = request.form.get("due_date")

        # Convert input string to date format
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("add_deadline"))

        new_deadline = Deadline(title=title, due_date=due_date, user_id=session["user_id"])
        db.session.add(new_deadline)
        db.session.commit()

        flash("Deadline added successfully!", "success")
        return redirect(url_for("calendar"))

    return render_template("add_deadline.html")

# Route to view deadlines (Calendar)
@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        flash("Please log in to view your deadlines.", "warning")
        return redirect(url_for("login"))

    user_deadlines = Deadline.query.filter_by(user_id=session["user_id"]).order_by(Deadline.due_date).all()

    # Calculate progress
    total_deadlines = len(user_deadlines)
    completed_deadlines = sum(1 for deadline in user_deadlines if deadline.completed)
    progress = (completed_deadlines / total_deadlines) * 100 if total_deadlines > 0 else 0

    return render_template("calendar.html", deadlines=user_deadlines, progress=progress)

@app.route("/mark_completed/<int:deadline_id>", methods=["POST"])
def mark_completed(deadline_id):
    if "user_id" not in session:
        flash("Please log in to update deadlines.", "warning")
        return redirect(url_for("login"))

    deadline = Deadline.query.filter_by(id=deadline_id, user_id=session["user_id"]).first()

    if not deadline:
        flash("Deadline not found!", "danger")
        return redirect(url_for("calendar"))

    # Toggle the completion status
    deadline.completed = not deadline.completed
    db.session.commit()

    flash(f"'{deadline.title}' marked as {'completed' if deadline.completed else 'pending'}!", "success")
    return redirect(url_for("calendar"))

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5001)  # Keep only one app.run()

