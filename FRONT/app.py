"""
Rappyjob
"""
from datetime import datetime,timedelta
from psycopg2 import connect,extras
from flask import Flask, redirect, request, flash, url_for, render_template, session
import requests
import json
from configfront import URL_API, DSN


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
    if session:
        return redirect(url_for('panel'))
    else:
        if request.method == 'POST':
            if 'usernamelogin' in request.form and 'passwordlogin' in request.form:
                data_request = {
                    "usernamelogin": request.form['usernamelogin'],
                    "passwordlogin": request.form['passwordlogin']
                }
                response_login = requests.post('{}/api/login'.format(URL_API),data=json.dumps(data_request))
                response_login = response_login.json()
                if response_login['message']:
                    session['token'] = response_login['data'][0]['token']
                    session['id'] = response_login['data'][0]['id']
                    #return render_template('panel.html',data=session['id'])
                    return redirect(url_for('panel'))
                elif response_login['error']:
                    flash(response_login['error'],'danger')
                    return render_template('login.html',status="login")
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

@app.route("/verification", methods=["GET"])
def verification():
    email = request.args.get('e')
    id = request.args.get('i')
    response = requests.get('{}/api/email-register?e={}&i={}'.format(URL_API,email,id))
    temp_response = response.json()
    if temp_response["message"]:
        return render_template('successfulmsg.html')
    elif temp_response["error"]:
        return render_template('badmsg.html',data = temp_response["error"])

@app.route("/panel", methods=["GET","POST"])
def panel():
    if request.method =='POST' and session:
        status = request.form.get('checkstatus', False)
        parameter = request.form.get('parameter', None)
        id = request.form.get('id', 0)
        data_request = {
            "parameter": parameter,
            "status": status,
            "id": id,
            "id_user": session['id']
        }
        response = requests.post('{}/api/update-parameter'.format(URL_API),data=json.dumps(data_request))
        # print(response.json())
        return redirect(url_for('panel'))
    if session:
        conn = connect(dsn=DSN)
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute('select id from login where token_session=%s',(session['token'],))
        if cursor.fetchall():
            cursor.execute('select * from parameter_user where id_user=%s and status = true order by parameter',(session['id'],))
            data_parameter = cursor.fetchall()
            return render_template('panel.html',session_id=session['id'],data_parameter=data_parameter)
        else:
            return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.pop('token')
    session.pop('id')
    return redirect(url_for('login'))

# @app.route("/change-parameter", methods=["POST"])
# def change_parameter():
#     if request.method =='POST':
#         user = request.form
#         print(user)
#         return redirect(url_for('panel'))

if __name__ == "__main__":
	app.run(debug=True)