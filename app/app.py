from flask import Flask, render_template

app = Flask(__name__, template_folder='./flaskr/templates', static_folder='./flaskr/static')

@app.route('/')
@app.route('/home')
def home():
    return render_template("1erpage.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
    
app.run(debug=True, host='0.0.0.0', port=5000)