"""
Rappyjob
"""
from datetime import datetime,timedelta
from flask import Flask, jsonify, redirect, request, flash, url_for, render_template
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

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == 'POST':
        if 'usernamelogin' in request.form and 'passwordlogin' in request.form:
            data_request = {
                "usernamelogin": request.form['usernamelogin'],
                "passwordlogin": request.form['passwordlogin']
            }
        elif 'username' in request.form and 'email' in request.form and 'password' in request.form and 'passwordconfirm' in request.form:
            data = {
                    "username": request.form['username'],
                    "email": request.form['email'],
                    "password": request.form['password'],
                    "passwordconfirm": request.form['passwordconfirm']
                }
            if request.form['password'] == request.form['passwordconfirm']:
                response = requests.post('{}/api/register'.format(URL_API),data=json.dumps(data))
                response = response.json()
                if response['error']:
                    flash(response['error'], 'danger')
                    return render_template('login.html',data=data)
                elif response['message']:
                    ## como hacer
                    name = "Successful"
                    flash(response['message'], 'success')
                    return render_template('login.html',name=name)
            else:
                flash('Las contraseñas no coinciden','danger')
                return render_template('login.html',data=data)
        else:
            flash('Incorrect username/password','danger')
            return render_template('login.html')
    else:
        return render_template('login.html')
if __name__ == "__main__":
	app.run(debug=True)