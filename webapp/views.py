from flask import render_template
from webapp import app
import human_eval

@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
	return render_template("main.html")
