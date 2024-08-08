from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from profilePicture import generate_avatar
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

def profile_picture():
    # Générer l'avatar
    avatar_image = generate_avatar(current_user.username)
    # Convertir l'image en base64 pour l'afficher dans le template
    avatar_data = base64.b64encode(avatar_image.getvalue()).decode('utf-8')
    
    # Récupérer la première lettre du pseudo de l'utilisateur
    first_letter = current_user.username[0].upper()
    
    return {'avatar': avatar_data, 'first_letter': first_letter}

@app.route('/')
@app.route('/home')
@app.route('/acceuil')
@login_required
def home():
    avatar_data = profile_picture()
    return render_template("chat.html", avatar_data=avatar_data)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

def get_user_info():
    user = User.query.first()
    if user:
        return {
            "nom": current_user.last_name,
            "prenom": current_user.first_name,
            "username" : current_user.username,
        }
    return {}

@app.route('/get_user_info', methods=['GET'])
@login_required
def user_info():
    user_info = {
        "nom": current_user.last_name,
        "prenom": current_user.first_name,
        "username": current_user.username,
    }
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
    avatar_data = profile_picture()
    return render_template("amis.html", avatar_data=avatar_data)

@app.route('/album')
@login_required
def album():
    avatar_data = profile_picture()
    return render_template("album.html", avatar_data=avatar_data)

@app.route('/chat')
@login_required
def discussion():
    avatar_data = profile_picture()
    return render_template("discussion.html", avatar_data=avatar_data)

@app.route('/discussion/parametre')
@login_required
def parametre():
    avatar_data = profile_picture()
    return render_template("parametres.html", avatar_data=avatar_data)

@app.route('/parametre')
@login_required
def reglage():
    avatar_data = profile_picture()
    return render_template("parametres.html", avatar_data=avatar_data)

@app.route('/album-photo')
@login_required
def album_photo():
    avatar_data = profile_picture()
    return render_template("pagealbumex.html", avatar_data=avatar_data)

@app.route('/recherche-amis')
def rechercheamis():
    avatar_data = profile_picture()
    return render_template("searchfriends.html", avatar_data=avatar_data)

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
