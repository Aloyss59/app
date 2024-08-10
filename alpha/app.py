from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from profilePicture import generate_avatar
import os, uuid, base64

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')
app.config['UPLOAD_FOLDER'] = r'flaskr\static\uploads'
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compte.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, rejected

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', foreign_keys=[user_id], backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friends_with')

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
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Connexion réussie !", "success")
                return redirect(url_for('home'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Formulaire invalide. Veuillez vérifier vos informations.', 'danger')
            return redirect(url_for('login'))
    else:
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

@app.route('/recherche-amis', methods=['GET', 'POST'])
@login_required
def recherche_amis():
    avatar_data = profile_picture()
    users = []

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # Rechercher les utilisateurs par nom d'utilisateur
            users = User.query.filter(User.username.ilike(f'%{username}%')).all()

    return render_template("searchfriends.html", avatar_data=avatar_data, users=users)

@app.route('/send-friend-request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    # Vérifier si une demande d'ami existe déjà
    existing_request = FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=user_id).first()

    if existing_request:
        flash('Vous avez déjà envoyé une demande à cet utilisateur.', 'warning')
    else:
        # Créer une nouvelle demande d'ami
        friend_request = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
        db.session.add(friend_request)
        db.session.commit()
        flash('Demande d\'ami envoyée avec succès !', 'success')

    return redirect(url_for('recherche_amis'))

@app.route('/amis')
@login_required
def amis():
    # Récupérer toutes les amitiés associées à l'utilisateur connecté
    friendships = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | 
        (Friendship.friend_id == current_user.id)
    ).all()

    # Créer une session SQLAlchemy pour récupérer les amis
    session = db.session

    # Liste pour stocker les informations des amis
    friends_data = []

    avatar_data = profile_picture()
    
    # Parcourir toutes les amitiés et ajouter les informations nécessaires à la liste friends_data
    for friendship in friendships:
        # Identifier l'ID de l'ami
        friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
        
        # Utiliser session.get() pour récupérer l'ami
        friend = session.get(User, friend_id)

        if friend:
            # Générer l'avatar de cet ami
            friend_avatar = generate_avatar(friend.username)
            friend_avatar_base64 = base64.b64encode(friend_avatar.getvalue()).decode('utf-8')
            first_letter = friend.username[0].upper()

            # Ajouter les informations de l'ami à la liste
            friends_data.append({
                'username': friend.username,
                'avatar': friend_avatar_base64,
                'first_letter': first_letter
            })

    # Rendre la page amis.html avec les données appropriées
    return render_template('amis.html', friends=friends_data, avatar_data=avatar_data)

@app.route('/accept-friend-request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.receiver_id == current_user.id:
        # Créer une relation d'amitié
        friendship = Friendship(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id)
        db.session.add(friendship)
        # Mettre à jour le statut de la demande d'ami
        friend_request.status = 'accepted'
        db.session.commit()
        flash('Demande d\'ami acceptée.', 'success')
        return redirect(url_for('amis'))
    else:
        flash('Demande d\'ami invalide.', 'danger')
    return redirect(url_for('demandes_amis'))

@app.route('/reject-friend-request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.receiver_id == current_user.id:
        # Mettre à jour le statut de la demande d'ami
        friend_request.status = 'rejected'
        db.session.commit()
        flash('Demande d\'ami refusée.', 'info')
        return redirect(url_for('chat'))
    else:
        flash('Demande d\'ami invalide.', 'danger')

    return redirect(url_for('demandes_amis'))


@app.route('/demandes-amis')
@login_required
def demandes_amis():
    avatar_data = profile_picture()
    # Récupérer les demandes d'amis en attente reçues par l'utilisateur connecté
    received_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    return render_template('demandes_amis.html', received_requests=received_requests, avatar_data=avatar_data)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    message = data['message']
    emit('receive_message', {'message': message, 'username': current_user.username}, room=room)

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    emit('receive_message', {'message': f"{current_user.username} a rejoint la salle."}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    emit('receive_message', {'message': f"{current_user.username} a quitté la salle."}, room=room)

@app.route('/chat')
@login_required
def chat():
    return render_template("discussion.html")

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
def album():
    avatar_data = profile_picture()
    return render_template("pagealbumex.html", avatar_data=avatar_data)

@app.route('/album')
@login_required
def album_photo():
    avatar_data = profile_picture()
    return render_template("album.html", avatar_data=avatar_data)

@app.route('/albumquests')
@login_required
def album_quests():
    avatar_data = profile_picture()
    return render_template("albumquests.html", avatar_data=avatar_data)

@app.route('/quests')
@login_required
def quests():
    avatar_data = profile_picture()
    return render_template("quests.html", avatar_data=avatar_data)

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
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
