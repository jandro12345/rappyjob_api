from flask import Flask, jsonify, redirect, template_rendered, url_for, render_template

app = Flask(__name__)
app.secret_key = "y2k"

@app.route("/home", methods=["GET","POST"])
def home():
    return render_template('home.html',data=[{"name":"alejandro","sur":"valdivia","url":"https://www.google.com/"},{"name":"alej","sur":"valdivia","url":"https://www.google.com/"},{"name":"alej","sur":"valdivia","url":"https://www.google.com/"}])
if __name__ == "__main__":
	app.run(debug=True)