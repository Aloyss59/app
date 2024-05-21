from flask import Flask, render_template

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')

@app.route('/')
@app.route('/home')
def home():
    return render_template("chat.html")

@app.route('/appareil-photo')
def appareil_photo():
    return render_template("photo.html")

@app.route('/amis')
def amis():
    return render_template("amis.html")

@app.route('/album')
def album():
    return render_template("album.html")

@app.route('/discussion')
def discussion():
    return render_template("discussion.html")

@app.route('/discussion/parametre')
def parametre():
    return render_template("parametres.html")

@app.route('/parametre')
def reglage():
    return render_template("reglage.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/login')
def login():
    return render_template('./auth/login.html')

@app.route('/register')
def register():
    return render_template('./auth/register.html')
    
app.run(debug=True, host='0.0.0.0', port=5000)