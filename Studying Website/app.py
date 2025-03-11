from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timedelta

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
    points = db.Column(db.Integer, default=0)  # New column to track points
    rank = db.Column(db.String(20), default="Bronze")  # New column for ranking

class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default="Medium")  # Already added priority
    notified = db.Column(db.Boolean, default=False)  # NEW COLUMN
    user = db.relationship("User", backref=db.backref("deadlines", lazy=True))

    def __repr__(self):
        return f"<Deadline {self.title} - {'Completed' if self.completed else 'Pending'}>"

    user = db.relationship("User", backref=db.backref("deadlines", lazy=True))

def check_deadline_notifications(user_id):
    user_id = session["user_id"]
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    upcoming_deadlines = Deadline.query.filter_by(user_id=user_id, due_date=tomorrow, notified=False).all()

    # Mark them as notified
    for deadline in upcoming_deadlines:
        deadline.notified = True
    db.session.commit()  # ✅ Fixed missing commit

    return upcoming_deadlines

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    completed_on = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("history", lazy=True))

@app.route("/", methods=["GET", "POST"])
def signup():
    if "user_id" in session:  # Redirect logged-in users
        flash("You are already signed in!", "info")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm-password")

            # Ensure all fields are filled
            if not name or not email or not password or not confirm_password:
                flash("All fields are required!", "danger")
                return redirect(url_for("signup"))

            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please log in.", "warning")
                return redirect(url_for("login"))

            # Check if passwords match
            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("signup"))

            # Hash password and create user
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(name=name, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            flash("Sign-up successful! 🎉 Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"An error occurred: {str(e)}", "danger")
            print(f"Signup Error: {e}")  # Print error for debugging

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

def update_user_rank(user):
    if user.points >= 500:
        user.rank = "Platinum Puller"
    elif user.points >= 400:
        user.rank = "Emerald Edger"
    elif user.points >= 200:
        user.rank = "Gold Gooner"
    elif user.points >= 100:
        user.rank = "Silver Stroker"
    elif user.points >= 50:
        user.rank = "Bronze Beater"
    else:
        user.rank = "Unranked"
    session["rank"] = user.rank  # Update session rank
    db.session.commit()

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)  # Fetch user details
    update_user_rank(user)  # Ensure rank is updated before rendering
    user_deadlines = Deadline.query.filter_by(user_id=user_id).all()

    # Calculate progress
    user_deadlines = Deadline.query.filter_by(user_id=user_id).all()
    total_deadlines = len(user_deadlines)
    completed_deadlines = sum(1 for deadline in user_deadlines if deadline.completed)
    progress = (completed_deadlines / total_deadlines) * 100 if total_deadlines > 0 else 0

    # Get upcoming notifications
    upcoming_deadlines = check_deadline_notifications(user_id)  # ✅ Fix: This is the correct variable

    if upcoming_deadlines:
        flash("⚠️ Reminder: You have deadlines due tomorrow! Check your calendar. 📅", "warning")

    return render_template("dashboard.html", name=session["user_name"], progress=progress, notifications=upcoming_deadlines, rank=user.rank)

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

        priority = request.form.get("priority")
        new_deadline = Deadline(title=title, due_date=due_date, user_id=session["user_id"], priority=priority)
        db.session.add(new_deadline)
        db.session.commit()

        flash("Deadline added successfully!", "success")
        return redirect(url_for("calendar"))

    return render_template("add_deadline.html")

@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        flash("Please log in to view your deadlines.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)  # Fetch user details
    selected_priority = request.args.get("priority")  # Get priority from query parameters

    # Filter deadlines based on priority
    if selected_priority and selected_priority in ["High", "Medium", "Low"]:
        deadlines = Deadline.query.filter_by(user_id=user_id, priority=selected_priority).order_by(Deadline.due_date).all()
    else:
        deadlines = Deadline.query.filter_by(user_id=user_id).order_by(Deadline.due_date).all()

    # Calculate progress
    total_deadlines = len(deadlines)
    completed_deadlines = sum(1 for deadline in deadlines if deadline.completed)
    progress = (completed_deadlines / total_deadlines) * 100 if total_deadlines > 0 else 0

    return render_template("calendar.html", deadlines=deadlines, progress=progress, selected_priority=selected_priority, rank=user.rank)

def calculate_progress():
    user_id = session["user_id"]
    user_deadlines = Deadline.query.filter_by(user_id=user_id).all()

    total_deadlines = len(user_deadlines)
    completed_deadlines = sum(1 for deadline in user_deadlines if deadline.completed)

    return (completed_deadlines / total_deadlines) * 100 if total_deadlines > 0 else 0

@app.route("/mark_completed/<int:deadline_id>", methods=["POST"])
def mark_completed(deadline_id):
    if "user_id" not in session:
        flash("Please log in to update deadlines.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    deadline = Deadline.query.filter_by(id=deadline_id, user_id=user_id).first()

    if not deadline:
        flash("Deadline not found!", "danger")
        return redirect(url_for("calendar"))

    deadline.completed = True

    # Award points based on priority
    if deadline.priority == "High":
        user.points += 20
    elif deadline.priority == "Medium":
        user.points += 15
    elif deadline.priority == "Low":
        user.points += 10

    # Check if all deadlines are completed
    user_deadlines = Deadline.query.filter_by(user_id=user_id).all()
    all_completed = all(d.completed for d in user_deadlines) if user_deadlines else False

    if all_completed and user_deadlines:
        for d in user_deadlines:
            completed_deadline = History(
                user_id=d.user_id,
                title=d.title,
                due_date=d.due_date,
                priority=d.priority,
                completed_on=datetime.today().date()
            )
            db.session.add(completed_deadline)
        Deadline.query.filter_by(user_id=user_id).delete()
        flash("All deadlines completed! Moved to history.", "success")

    update_user_rank(user)
    session["rank"] = user.rank  # Update session rank
    db.session.commit()

    flash(f"'{deadline.title}' marked as completed!", "success")
    return redirect(url_for("calendar"))

@app.route("/history")
def history():
    if "user_id" not in session:
        flash("Please log in to view history.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    completed_deadlines = History.query.filter_by(user_id=user_id).order_by(History.completed_on.desc()).all()

    return render_template("history.html", completed_deadlines=completed_deadlines)

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5001)  # Keep only one app.run()
