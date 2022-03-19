"""
Rappyjob
"""
from datetime import datetime,timedelta
from flask import Flask, jsonify, redirect, request, template_rendered, url_for, render_template
import requests
import json
from configfront import URL_API


app = Flask(__name__)
app.secret_key = "y2k"
@app.route("/", methods=["GET"])
def inti():
    return redirect(url_for("home"))
@app.route("/home", methods=["GET","POST"])
def home():
    if request.method == 'POST' and 'parameter' in request.form:
        data = []
        parameter = {'parameter': request.form['parameter'].lower()}
        response = requests.get('{}/api/cpt-get-data'.format(URL_API),params=parameter)
        data.extend(response.json()['data'])
        response = requests.get('{}/api/infoempleo-get-data'.format(URL_API),params=parameter)
        data.extend(response.json()['data'])
        data.sort(key = lambda date: datetime.strptime(date["time_order"], '%Y-%m-%d %H:%M:%S'),reverse=True)
        return render_template('home.html',data=data)
    if request.method == 'GET':
        return render_template('home.html')
if __name__ == "__main__":
	app.run(debug=True)