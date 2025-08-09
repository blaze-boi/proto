#flask learing
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo 
import cloudinary
import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Cookies"
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)    

cloudinary.config(
  cloud_name = "dxqcm0b4y",
  api_key = "515517175212981",
  api_secret = "gUe1L7Ru-eF4o8GAVSbuSThoyrE"
)

@app.route("/auth", methods=["POST", "GET"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    if request.method == "GET":
        return render_template("index.html", auth="")
    if request.form.get("action") == "signup":
        return signup(name, email, password)
    elif request.form.get("action") == "login":
        return login(name, email, password)
    elif request.form.get("action") == "logout":
        return logout()
    return redirect("/")

def signup(name, email, password):
    if(mongo.db.users.find_one({"email": email})==None):
        mongo.db.users.insert_one({
            "name": name,
            "email": email,
            "password": password
        })
        session['email'] = email
        return render_template('dashboard.html', auth="Signed up")
    else:
        return render_template('index.html', auth="Error")


def login(name, email, password):
    user = mongo.db.users.find_one({"email": email})
    if user and user['password'] == password:
        session['email'] = email
        return render_template('dashboard.html', auth="Logged in")
    else:
        return render_template('index.html', auth="Error")    

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if 'email' in session:
        session.pop('email', None)
        return render_template('index.html', auth="Logged out")
    else:
        return render_template('index.html', auth="Error: Not logged in")


@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)
            url = result["secure_url"]

            # Save URL to MongoDB
            mongo.db.images.insert_one({"url": url})
            return render_template("upload.html", img_url=url)

    return render_template("upload.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html") 

@app.route("/posting", methods=["POST", "GET"])
def posting():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)
            url = result["secure_url"]

            # Save URL to MongoDB
            mongo.db.images.insert_one({"url": url})
            return render_template("posting.html", img_url=url)
    return render_template("posting.html")


if __name__ == "__main__":
    app.run(debug=True)