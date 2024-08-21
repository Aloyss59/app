import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from flask_socketio import SocketIO, emit
from profilePicture import generate_avatar
from datetime import date, datetime, timezone
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
import os, uuid, base64, pytz, psutil, time, random

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')
app.config['UPLOAD_FOLDER'] = r'flaskr/static/uploads'
with open('config_secrets.txt', 'r') as f:
    secret_key = f.read().strip()
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compte.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")
online_users = {}

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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    origine_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'Message({self.id}, {self.sender_id}, {self.receiver_id}, {self.text})'

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
        if not current_user.is_admin:
            abort(403)  # Accès refusé
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

def reset_daily_quests():
    with app.app_context():
        all_users = User.query.all()
        for user in all_users:
            # Check if the user has less than 3 quests
            if len(user.user_quests) < 3:
                available_quests = Quest.query.all()
                assigned_quest_ids = [uq.quest_id for uq in user.user_quests]
                available_quests = [q for q in available_quests if q.id not in assigned_quest_ids]

                if available_quests:
                    for _ in range(3 - len(user.user_quests)):
                        quest = random.choice(available_quests)
                        user_quest = UserQuest(user_id=user.id, quest_id=quest.id, status='accepted')
                        db.session.add(user_quest)
                        available_quests.remove(quest)

        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(reset_daily_quests, 'cron', hour=0, minute=0)  # Exécuter tous les jours à minuit
scheduler.start()

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
    return db.session.get(User, int(user_id))

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
    if request.method == 'POST':
        if 'add' in request.form:
            hashed_password = generate_password_hash(request.form['password'])
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
            user = User.query.get(request.form['id'])

            if user:
                user.first_name = request.form['first_name']
                user.last_name = request.form['last_name']
                user.phone = request.form['phone']
                user.username = request.form['username']
                user.email = request.form['email']

                if request.form['password']:
                    user.password = generate_password_hash(request.form['password'])

                if request.form['solde']:
                    user.solde = float(request.form['solde'])

                user.is_admin = 'is_admin' in request.form

                db.session.commit()
                flash("Utilisateur mis à jour avec succès", "success")

            else:
                flash("Utilisateur introuvable", "error")

        elif 'delete' in request.form:
            user = User.query.get(request.form['id'])
            if user:
                db.session.delete(user)
                db.session.commit()
                flash("Utilisateur supprimé avec succès", "success")

            else:
                flash("Utilisateur introuvable", "error")

        return redirect(url_for('admin_dashboard'))
    
    users = User.query.all()
    return render_template('admin/admin_dashboard.html', users=users)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    compte = User.query.get_or_404(id)
    compte.nom = request.form.get('nom')
    compte.solde = float(request.form.get('solde'))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/data')
def data():
    info = get_system_info()
    return jsonify(info)

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
        else:
            flash('Formulaire invalide. Veuillez vérifier vos informations.', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == "POST":
        username_exists = User.query.filter_by(username=form.username.data).first()
        email_exists = User.query.filter_by(email=form.email.data).first()

        if username_exists:
            flash('Le nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.', 'danger')
        elif email_exists:
            flash('L\'adresse e-mail est déjà utilisée. Veuillez en choisir une autre.', 'danger')
        else:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
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

@app.route('/recherche-amis', methods=['GET', 'POST'])
@login_required
def recherche_amis():
    avatar_data = profile_picture()
    users = []

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            users = User.query.filter(User.username.ilike(f'%{username}%')).all() # Rechercher les utilisateurs par nom d'utilisateur

    return render_template("searchfriends.html", avatar_data=avatar_data, users=users)

@app.route('/send-friend-request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
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

    return redirect(url_for('recherche_amis'))

@app.route('/amis')
@login_required
def amis():
    avatar_data = profile_picture()
    friends_data = find_friends()
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
    created_at = new_message.created_at.isoformat()

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
    try:
        avatar_data = profile_picture()
        current_user_id = current_user.id

        # Vérifiez si l'utilisateur cible est le même que l'utilisateur actuel
        if user_id == current_user_id:
            flash('Vous ne pouvez pas discuter avec vous-même.', 'warning')
            return redirect(url_for('home'))

        # Vérifiez si l'utilisateur cible existe
        target_user = User.query.get(user_id)
        if not target_user:
            flash('Utilisateur non trouvé.', 'danger')
            return redirect(url_for('home'))

        # Récupérez les messages avec les utilisateurs associés
        messages = Message.query.options(
            joinedload(Message.sender),
            joinedload(Message.receiver)
        ).filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.created_at.asc()).all()

        return render_template("discussion.html", messages=messages, user_id=user_id, avatar_data=avatar_data)

    except Exception as e:
        flash('Une erreur est survenue : {}'.format(str(e)), 'danger')
        return redirect(url_for('home'))

@app.route('/send_message/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    message_text = request.form.get('message', '')
    if message_text is not None and request.method == "POST":
        new_message = Message(text=message_text, sender_id=current_user.id, receiver_id=user_id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat_with_user', user_id=user_id))
    
    flash('Le message ne peut pas être vide.', 'danger')
    return redirect(url_for('chat_with_user', user_id=user_id))

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

@app.route('/recherche-amis')
def rechercheamis():
    avatar_data = profile_picture()
    return render_template("searchfriends.html", avatar_data=avatar_data)

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
    scheduler.start()
    info = get_system_info()
