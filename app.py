from flask import Flask, render_template

app = Flask(__name__, template_folder='', static_folder='')

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.errorhandler(404)
def page_not_found(e):
    @app.route("/404")
    def page_404():
        return render_template('404.html')