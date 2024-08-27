from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, emit
from sqlalchemy.orm import joinedload
from profilePicture import generate_avatar
from datetime import datetime, timedelta, timezone
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
import os, uuid, base64, pytz, psutil, time, random, ssl, string, pyotp, logging

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')
app.config['UPLOAD_FOLDER'] = r'flaskr/static/uploads'
with open('config_secrets.txt', 'r') as f:
    secret_key = f.read().strip()
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compte.db'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")
# Charger le certificat SSL/TLS
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('cert.pem', 'key.pem')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'society.realese@gmail.com'
with open('config_secret2.txt', 'r') as f:
    secret_key2 = f.read().strip()
app.config['MAIL_PASSWORD'] = secret_key2
app.config['MAIL_DEFAULT_SENDER'] = 'society.realese@gmail.com'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
bcrypt = Bcrypt(app)
online_users = {}
limiter = Limiter(get_remote_address, app=app, default_limits=["25 per minute"])
csrf = CSRFProtect(app)
logging.basicConfig(filename='access.log', level=logging.WARNING)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    solde = db.Column(db.Float, default=0)

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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friends_with')

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    origine_created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'Messages({self.id}, {self.sender_id}, {self.receiver_id}, {self.text})'

    def format_created_at(self):
        tz = pytz.timezone('Europe/Paris')
        return self.created_at.astimezone(tz).strftime('%H:%M')

    def frmat_origine_created_at(self):
        tz = pytz.timezone('Europe/Paris')
        return self.created_at.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rarity = db.Column(db.Float, nullable=True)

class UserQuest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey('quest.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed, accepted, rejected
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    assigned_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())

    user = db.relationship('User', backref='user_quests')
    quest = db.relationship('Quest', backref='user_quests')

    def __repr__(self):
        return f'<UserQuest {self.id} {self.status}>'

    def frmat_origine_created_at(self):
        tz = pytz.timezone('Europe/Paris')
        return self.assigned_at.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vous devez être connecté pour accéder à cette page.", 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            log_action(f"Accès non autorisé tenté par l'utilisateur", current_user)
            abort(403)  # Forbidden access

        return f(*args, **kwargs)
    return decorated_function

def profile_picture():
    avatar_image = generate_avatar(current_user.username)
    avatar_data = base64.b64encode(avatar_image.getvalue()).decode('utf-8')
    first_letter = current_user.username[0].upper()
    return {'avatar': avatar_data, 'first_letter': first_letter}

def friend_profile_picture(username):
    avatar_image = generate_avatar(username)
    return base64.b64encode(avatar_image.getvalue()).decode('utf-8')

def find_friends():
    friendships = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | 
        (Friendship.friend_id == current_user.id)
    ).all()
    friends_data = []

    for friendship in friendships:
        friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
        friend = db.session.get(User, friend_id)

        if friend:
            friend_avatar_base64 = friend_profile_picture(friend.username)
            first_letter = friend.username[0].upper()

            friends_data.append({
                'username': friend.username,
                'avatar': friend_avatar_base64,
                'first_letter': first_letter,
                'friend_id': friend_id
            })
    return friends_data

def find_profil_picture_other_user(user):
    if user:
        username = user.username  # Obtenez le nom d'utilisateur
        avatar_buffer = generate_avatar(username)
        avatar_base64 = base64.b64encode(avatar_buffer.getvalue()).decode('utf-8')
        return {'avatar': avatar_base64}
    return {'avatar': None}

def find_quests_user():
    user_quests = UserQuest.query.filter(
        (UserQuest.user_id == current_user.id)
    ).all()
    quests_data = []
    for user_quest in user_quests:
        quest = user_quest.quest
        quests_data.append({
            'id': quest.id,
            'title': quest.title,
            'description': quest.description,
            'reward': quest.reward,
            'completed': user_quest.status == 'completed',
            'pending': user_quest.status == 'pending',
            'failed': user_quest.status == 'failed',
            'accepted': user_quest.status == 'accepted',
            'rejected': user_quest.status == 'rejected',
            'assigned_at': user_quest.assigned_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return quests_data

def get_system_info():
    time.sleep(3)
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    info = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent
    }
    
    return info

def random_quests():
    # Récupération de toutes les quêtes
    resultats = Quest.query.all()

    elements = [resultat.title for resultat in resultats]
    poids = [resultat.rarity if resultat.rarity is not None else 1 for resultat in resultats]  # Assurez-vous que les poids ne sont pas None

    if not elements:
        return None  # Retourner None ou une autre valeur si aucune quête n'est disponible

    # Sélection d'un titre de quête basé sur les poids
    valeur_choisie = random.choices(elements, weights=poids, k=1)[0]

    # Récupération de l'objet Quest correspondant pour obtenir son ID
    quest_obj = Quest.query.filter_by(title=valeur_choisie).first()

    if quest_obj:
        return quest_obj.id, quest_obj.title
    else:
        return None  # Retourne None si la quête choisie n'existe pas (cas improbable)

def reset_quests(user):
    UserQuest.query.filter_by(user_id=user.id).delete()
    db.session.commit()

def reset_daily_quests():
    with app.app_context():
        all_users = User.query.all()
        for user in all_users:
            # Supprimer toutes les quêtes actuelles de l'utilisateur
            reset_quests(user)

            # Vérifier si l'utilisateur a moins de 3 quêtes (après suppression)
            if len(user.user_quests) < 3:
                available_quests = Quest.query.all()
                assigned_quest_ids = [uq.quest_id for uq in user.user_quests]
                available_quests = [q for q in available_quests if q.id not in assigned_quest_ids]

            if available_quests:
                for _ in range(3 - len(user.user_quests)):
                    quest_id, quest_title = random_quests()  # Unpack the returned tuple
                    user_quest = UserQuest(user_id=user.id, quest_id=quest_id, status='accepted')
                    db.session.add(user_quest)
                    available_quests = [q for q in available_quests if q.id != quest_id]  # Remove the quest by id

                    db.session.commit()

    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(reset_daily_quests, 'cron', hour=00, minute=00)  # Exécuter tous les jours à minuit

def verify_otp(otp):
    otp_secret = session.get('otp_secret')

    if not otp_secret:
        return "Clé secrète non trouvée dans la session"

    totp = pyotp.TOTP(otp_secret)

    # Vérifiez le code OTP
    if totp.verify(otp):
        session['authenticated'] = True
        return True
    else:
        return False

def log_action(action, user):
    logging.info(f"Action: {action}, User: {user.username}, Time: {datetime.now()}")

@app.route('/')
@app.route('/home')
@app.route('/acceuil')
@login_required
def home():
    avatar_data = profile_picture()
    friends_data = find_friends()
    return render_template("chat.html", avatar_data=avatar_data, friends=friends_data)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.query(User).get(int(user_id))

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        online_users[user_id] = request.sid
        emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits nécessaires pour accéder à cette section.", 'danger')
        log_action("Essaie de ce connecter sans etre autoriser au /admin", current_user)
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'add' in request.form:
            # Ajout d'un utilisateur par un administrateur
            if not current_user.is_admin:
                log_action("Tentative d'ajout d'utilisateur non autorisé dans /admin", current_user)
                flash("Action non autorisée.", 'danger')
                return redirect(url_for('admin_dashboard'))
            
            hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user = User(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                phone=request.form['phone'],
                username=request.form['username'],
                email=request.form['email'],
                password=hashed_password,
                is_admin='is_admin' in request.form,
                solde=0
            )
            db.session.add(user)
            db.session.commit()
            flash("Utilisateur ajouté avec succès", "success")

        elif 'update' in request.form:            
            # Mise à jour d'un utilisateur par un administrateur
            user = User.query.get(request.form['id'])
            if user and current_user.is_admin:
                user.first_name = request.form['first_name']
                user.last_name = request.form['last_name']
                user.phone = request.form['phone']
                user.username = request.form['username']
                user.email = request.form['email']

                if request.form['password']:
                    user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

                if request.form['solde']:
                    user.solde = float(request.form['solde'])

                user.is_admin = 'is_admin' in request.form
                db.session.commit()
                flash("Utilisateur mis à jour avec succès", "success")
            else:
                if user is None:
                    log_action("Tentative de misa a jour sans présence d'un user", current_user)
                    flash("user inexsitant", 'danger')
                    return redirect(url_for('admin_dashboard'))
                if not current_user.is_admin:
                    log_action("Tentative de mise à jour non autorisée par", current_user)
                    flash("Action non autorisée.", "danger")
                    return redirect(url_for('home'))
            
        elif 'delete' in request.form:
            # Suppression d'un utilisateur par un administrateur
            user = User.query.get(request.form['id'])
            if user and current_user.is_admin:
                db.session.delete(user)
                db.session.commit()
                flash("Utilisateur supprimé avec succès", "success")
            else:
                if user is None:
                    log_action("Tentative de suppression sans séance d'un user", current_user)
                    flash("user inexsitant", 'danger')
                    return redirect(url_for('admin_dashboard'))
                if not current_user.is_admin:
                    log_action(f"Tentative de suppression non autorisée", current_user)
                    flash("Action non autorisée.", "danger")
                    return redirect(url_for('home'))

        return redirect(url_for('admin_dashboard'))

    users = User.query.all()
    return render_template('admin/admin_dashboard.html', users=users)

@app.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update(id):
    compte = User.query.get_or_404(id)
    compte.nom = request.form.get('nom')
    compte.solde = float(request.form.get('solde'))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/data')
@login_required
@admin_required
def data():
    if current_user.is_admin:
        info = get_system_info()
        if info is not None:
            return jsonify(info)
        else:
            return jsonify({})
    else:
        log_action("Tentative de récupération de données serveur.", current_user)
        return  redirect(url_for('home'))

@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in online_users.items():
        if sid == request.sid:
            user_id = uid
            break
    if user_id:
        del online_users[user_id]
        emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)

@app.route('/online_users')
@login_required
@admin_required
def get_online_users():
    if current_user.is_admin:
        user_ids = list(online_users.keys())
        users = User.query.filter(User.id.in_(user_ids)).all()
        online_user_data = [
            {
                'id': user.id,
                'username': user.username,
                'admin': user.is_admin if user.is_admin is not None else False
            }
            for user in users
        ]
        return jsonify(online_user_data)
    else:
        log_action("Tentative de récupération des utilisateurs connectés.", current_user)
        return redirect(url_for('home'))

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Connexion réussie !", "success")
                return redirect(url_for('home'))
            elif user is not None:
                user = User.query.filter_by(email=form.email.data).first()
                if user and check_password_hash(user.password, form.password.data):
                    login_user(user)
                    flash("Connexion réussie !", "success")
                    return redirect(url_for('home'))
        return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        form = RegistrationForm()
        if form.validate_on_submit() and request.method == "POST":
            username_exists = User.query.filter_by(username=form.username.data).first()
            email_exists = User.query.filter_by(email=form.email.data).first()

            if username_exists:
                flash('Le nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.', 'danger')
            elif email_exists:
                flash('L\'adresse e-mail est déjà utilisée. Veuillez en choisir une autre.', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                new_user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone=form.phone.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    is_admin=False
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('login'))
    
        return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie !", "success")
    return redirect(url_for('login'))

@app.route('/appareil-photo')
@login_required
def appareil_photo():
    return render_template("photo.html")

@app.route('/send-friend-request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    if request.method == "POST":
        # Vérifier si une demande d'ami existe déjà dans les deux sens
        existing_request = FriendRequest.query.filter(
            (FriendRequest.sender_id == current_user.id) & 
            (FriendRequest.receiver_id == user_id) |
            (FriendRequest.sender_id == user_id) & 
            (FriendRequest.receiver_id == current_user.id)
        ).first()

        if existing_request:
            if existing_request.sender_id == current_user.id:
                flash('Vous avez déjà envoyé une demande à cet utilisateur.', 'warning')
            else:
                flash('Cet utilisateur vous a déjà envoyé une demande d\'ami.', 'warning')
        else:
            # Créer une nouvelle demande d'ami
            friend_request = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
            db.session.add(friend_request)
            db.session.commit()
            flash('Demande d\'ami envoyée avec succès !', 'success')

        return redirect(url_for('amis'))
    return redirect(url_for('amis'))

@app.route('/amis', methods=['GET', 'POST'])
@login_required
def amis():
    avatar_data = profile_picture()
    friends_data = find_friends()
    users = []

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            users = User.query.filter(User.username.ilike(f'%{username}%')).all()
            for user in users:
                user_picture = find_profil_picture_other_user(user)
                user.avatar = user_picture['avatar']

    received_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()

    return render_template(
        'amis.html',
        friends=friends_data,
        avatar_data=avatar_data,
        users=users,
        received_requests=received_requests
    )

@app.route('/accept-friend-request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    if request.method == "POST":
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
    return redirect(url_for('amis'))

@app.route('/reject-friend-request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    if request.method == "POST":
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == current_user.id:
            # Mettre à jour le statut de la demande d'ami
            friend_request.status = 'rejected'
            db.session.commit()
            flash('Demande d\'ami refusée.', 'info')
            return redirect(url_for('chat'))
        else:
            flash('Demande d\'ami invalide.', 'danger')

    return redirect(url_for('amis'))

@socketio.on('message')
def handle_message(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    message_text = data.get('text')

    # Vérification des données
    if not sender_id or not receiver_id or not message_text:
        return

    # Créer un nouvel objet Message
    new_message = Message(sender_id=sender_id, receiver_id=receiver_id, text=message_text)
    db.session.add(new_message)
    db.session.commit()

    # Convertir l'heure en UTC pour l'envoyer au client
    created_at = new_message.created_at.replace(tzinfo=timezone.utc).astimezone(timezone).isoformat()

    # Envoyer le message à tous les clients
    emit('message', {
        'text': message_text,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'created_at': created_at
    }, broadcast=True)  # broadcast=True permet d'envoyer le message à tous les clients connectés

@app.route('/chat/<int:user_id>', methods=['GET'])
@login_required
def chat_with_user(user_id):
    avatar_data = profile_picture()  # Assurez-vous que cette fonction renvoie un dict avec une clé 'avatar'
    current_user_id = current_user.id

    if user_id == current_user_id:
        flash('Vous ne pouvez pas discuter avec vous-même.', 'warning')
        return redirect(url_for('home'))

    target_user = User.query.get(user_id)
    if not target_user:
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('home'))
    
    messages = db.session.query(Messages).options(
        joinedload(Messages.sender),
        joinedload(Messages.receiver)
    ).filter(
        (Messages.sender_id == current_user_id) & (Messages.receiver_id == user_id) |
        (Messages.sender_id == user_id) & (Messages.receiver_id == current_user_id)
    ).order_by(Messages.created_at.asc()).all()

    return render_template("discussion.html", messages=messages, user_id=user_id, avatar_data=avatar_data)

@app.route('/send_message/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    message_text = request.form.get('message', '')
    if message_text is not None and request.method == "POST":
        new_message = Messages(text=message_text, sender_id=current_user.id, receiver_id=user_id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat_with_user', user_id=user_id))
    
    flash('Le message ne peut pas être vide.', 'danger')
    return redirect(url_for('chat_with_user', user_id=user_id))

# @app.route('/discussion/parametre')
# @login_required
# def parametre():
#     avatar_data = profile_picture()
#     return render_template("parametres.html", avatar_data=avatar_data)

@app.route('/parametre', methods=['GET'])
@login_required
def reglage():
    avatar_data = profile_picture()
    return render_template("parametres.html", avatar_data=avatar_data)

from flask_mail import Mail, Message
mail = Mail(app)
def send_otp(email, otp_code):
    msg = Message(subject='Votre code de vérification', recipients=[email])
    msg.body = f'Votre code OTP est {otp_code}.'
    mail.send(msg)

@app.route('/parametre/update-password', methods=['POST'])
@login_required
def update_password():
    if request.method == 'POST':
        user = current_user
        old_password = request.form['old-password']
        new_password = request.form['new-password']
        new_password_confirm = request.form['new-password-confirm']
        otp = request.form.get('opt-password', '')

        # Vérifiez le mot de passe
        if not user or check_password_hash(user.password, old_password):
            flash("Identifiants invalides. Veuillez réessayer.", 'error')
            return redirect(url_for('login'))

        # Vérifiez si les mots de passe sont identiques
        if new_password != new_password_confirm:
            flash("Les mots de passe ne sont pas identiques.", 'error')
            return redirect(url_for('reglage'))

        # Vérifiez si le nouveau mot de passe est suffisamment fort
        if len(new_password) < 3:
            flash("Le mot de passe doit contenir au moins 8 caractères.", 'error')
            return redirect(url_for('reglage'))

        # Vérification et envoi OTP
        if not otp:
            if 'opt-password' not in session:
                verification_code = ''.join(random.choices(string.digits, k=6))
                session['opt-password'] = verification_code
                email = user.email
                send_otp(email, verification_code)
                flash("Un code de vérification a été envoyé à votre email.", 'info')
            if 'opt-password' in session:
                otp = request.form['opt-password']
                if otp:
                    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    db.session.commit()
                    flash("Mot de passe modifier avec succès", 'success')
                    return redirect(url_for('reglage'))
            
            flash("Veuillez entrer le code de vérification envoyé à votre email.", 'info')
            return redirect(url_for('reglage'))

        # Vérification de l'OTP
        if otp != session.get('opt-password'):
            flash("Code de vérification incorrect.", 'error')
            return redirect(url_for('reglage'))

        # Mise à jour du mot de passe
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        session.pop('opt-password', None)  # Supprimer l'OTP de la session après l'utilisation
        flash("Mot de passe mis à jour avec succès!", 'success')
        return redirect(url_for('reglage'))
    return redirect(url_for('reglage'))

@app.route('/parametre/update-email', methods=['POST'])
@login_required
def update_email():
    if request.method == "POST":
        user = current_user
        old_email = request.form.get('old_email')
        new_email = request.form.get('new_email')
        password = request.form.get('password')
        otp = request.form.get('opt-email', '')

        # Vérifiez si l'ancienne adresse email correspond
        if old_email != user.email:
            flash("L'ancienne adresse email ne correspond pas.", 'error')
            return redirect(url_for('reglage'))

        # Vérifiez le mot de passe
        if not user or not check_password_hash(user.password, password):
            flash("Identifiants invalides. Veuillez réessayer.", 'error')
            return redirect(url_for('login'))
        
        # Vérifiez si le nouvel email est déjà utilisé
        if User.query.filter_by(email=new_email).first():
            flash("Cette adresse email est déjà utilisée.", 'error')
            return redirect(url_for('reglage'))

        # Gestion de l'OTP
        if not otp:
            # Génère un nouveau code OTP et envoie-le par e-mail
            if 'opt-email' not in session:
                verification_code = ''.join(random.choices(string.digits, k=6))
                session['opt-email'] = verification_code
                email = current_user.email
                send_otp(email, verification_code)
                flash("Un code de vérification a été envoyé par mail.", 'info')
                return redirect(url_for('reglage'))
            if 'opt-email' in session:
                otp = request.form['opt-email']
                if otp:
                    user.email = new_email
                    db.session.commit()
                    session.pop('opt-email', None)
                    flash("Adresse email mise à jour avec succès!", 'success')
                    return redirect(url_for('reglage'))
                else:
                    flash("Code de verrification incorrect.", 'error')
                    return redirect(url_for('reglage'))

            # Redirige si le code OTP n'est pas encore saisi
            flash("Veuillez entrer le code de vérification envoyé par mail.", 'info')
            return redirect(url_for('reglage'))
    

        # Vérification de l'OTP
        if otp != session.get('opt-email'):
            flash("Code de vérification incorrect.", 'error')
            return redirect(url_for('reglage'))

        # Met à jour l'email
        user.email = new_email
        db.session.commit()
        session.pop('opt-email', None)
        flash("Adresse email mise à jour avec succès!", 'success')
        return redirect(url_for('reglage'))
    return redirect(url_for('reglage'))

@app.route('/parametre/update-phone', methods=['POST'])
@login_required
def update_phone():
    if request.method == 'POST':
        user = User.query.get(current_user.id)

        old_phone = request.form['old-phone']
        new_phone = request.form['new-phone']
        password = request.form['password-phone']
        otp = request.form.get('opt-phone', '')

        # Vérifiez si l'ancien numéro de téléphone correspond
        if old_phone != user.phone:
            flash("L'ancien numéro de téléphone ne correspond pas.", 'error')
            return redirect(url_for('reglage'))

        # Vérifiez le mot de passe
        if not user or not check_password_hash(user.password, password):
            flash("Identifiants invalides. Veuillez réessayer.", 'error')
            return redirect(url_for('login'))

        # Gestion de l'OTP
        if not otp:
            # Génère un nouveau code OTP et envoie-le par e-mail
            if 'opt-phone' not in session:
                verification_code = ''.join(random.choices(string.digits, k=6))
                session['opt-phone'] = verification_code
                email = current_user.email
                send_otp(email, verification_code)
                flash("Un code de vérification a été envoyé par mail.", 'info')
                return redirect(url_for('reglage'))
            if 'opt-phone' in session:
                otp = request.form['opt-phone']
                if otp:
                    user.phone = new_phone
                    db.session.commit()
                    session.pop('opt-phone', None)
                    flash("Adresse email mise à jour avec succès!", 'success')
                    return redirect(url_for('reglage'))
                else:
                    flash("Code de verrification incorrect.", 'error')
                    return redirect(url_for('reglage'))

        # Met à jour le numéro de téléphone
        user.phone = new_phone
        db.session.commit()
        session.pop('opt-phone', None)
        flash("Numéro de téléphone mis à jour avec succès!", 'success')
        return redirect(url_for('reglage'))
    return redirect(url_for('reglage'))

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

@app.route('/dash-quests', methods=['GET', 'POST'])
@login_required
@admin_required
def quests():
    if request.method == 'POST':
        quest_id = request.form.get('id')
        action = request.form.get('action')

        if not quest_id:
            flash("L'ID de la quête est manquant.", "danger")
            return redirect(url_for('quests'))

        if not action:
            flash("Aucune action spécifiée.", "danger")
            return redirect(url_for('quests'))

        try:
            user_quest = UserQuest.query.filter_by(user_id=current_user.id, quest_id=quest_id).first()

            if user_quest:
                if action == 'accepted':
                    user_quest.status = 'accepted'
                elif action == 'rejected':
                    user_quest.status = 'rejected'
                    db.session.delete(user_quest)
                else:
                    flash("Action non reconnue.", "danger")
                    return redirect(url_for('quests'))
            else:
                existing_quest = UserQuest.query.filter_by(user_id=current_user.id, quest_id=quest_id).first()

                if existing_quest:
                    flash("Cette quête a déjà été acceptée.", "warning")
                    return redirect(url_for('quests'))

                if action == 'accept':
                    new_user_quest = UserQuest(user_id=current_user.id, quest_id=quest_id, status='pending')
                    db.session.add(new_user_quest)
                elif action == 'next':
                    id_futur_quests, futur_quest = random_quests()
                else:
                    flash("Action non reconnue pour une nouvelle quête.", "danger")
                    return redirect(url_for('quests'))

            db.session.commit()
            flash("Quête mise à jour avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            if db.session.is_active:
                db.session.close()
            flash(f"Erreur lors de la mise à jour de la quête: {str(e)}", "danger")

    avatar_data = profile_picture()
    quests = find_quests_user()
    id_futur_quests, futur_quest = random_quests()

    return render_template("dash-quests.html", quests=quests, avatar_data=avatar_data, futur_quest=futur_quest, id_futur_quests=id_futur_quests)

@app.route('/quests')
@login_required
def daily_quests():
    avatar_data = profile_picture()
    quests_data = find_quests_user()  # Récupère les quêtes de l'utilisateur connecté
    return render_template("quests.html", avatar_data=avatar_data, quests=quests_data)

@app.route('/api/usernames')
@login_required
def get_usernames():
    users = User.query.all()
    user_dict = {user.id: user.username for user in users}
    return jsonify(user_dict)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    scheduler.start()
    info = get_system_info()
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur: {str(e)}")
