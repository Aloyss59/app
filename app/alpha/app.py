from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm  # Ensure these are defined correctly
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import base64

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')
app.config['UPLOAD_FOLDER'] = r'flaskr\static\uploads'
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compte.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/')
@app.route('/home')
@app.route('/acceuil')
@login_required
def home():
    return render_template("chat.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_user_info():
    user = User.query.first()
    if user:
        return {
            "nom": user.last_name,
            "prenom": user.first_name,
            "email": user.email,
            "telephone": user.phone
        }
    return {}

@app.route('/get_user_info', methods=['GET'])
@login_required
def user_info():
    user_info = get_user_info()
    return jsonify(user_info)   

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('./auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('./auth/signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Welcome {current_user.username}!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/appareil-photo')
@login_required
def appareil_photo():
    return render_template("photo.html")

@app.route('/amis')
@login_required
def amis():
    return render_template("amis.html")

@app.route('/album')
@login_required
def album():
    return render_template("album.html")

@app.route('/chat')
@login_required
def discussion():
    return render_template("discussion.html")

@app.route('/discussion/parametre')
@login_required
def parametre():
    return render_template("parametres.html")

@app.route('/parametre')
@login_required
def reglage():
    return render_template("parametres.html")

@app.route('/album-photo')
@login_required
def album_photo():
    return render_template("pagealbumex.html")

@app.route('/recherche-amis')
def rechercheamis():
    return render_template("searchfriends.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'No image part in the request'}), 400

    image_data = data['image'].split(",")[1]
    file_data = base64.b64decode(image_data)
    filename = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, "wb") as f:
        f.write(file_data)
    
    return jsonify({'url': f"../static/uploads/{filename}"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)
