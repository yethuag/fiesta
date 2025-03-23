from flask import Flask, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm  # Corrected import
import os 

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids warning
app.config['SECRET_KEY'] = 'bambiii'  # Needed for session management

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Initialize login_manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not logged in

# User Model
class User(db.Model, UserMixin):   
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Fixed typo in form name
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode()
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Fixed form name
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed. Check your username and password.", "danger")
    return render_template("login.html", form=form)  # Ensure return is present

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Read PORT from env
    app.run(host="0.0.0.0", port=port)  
