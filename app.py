#flask learing
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo 
import cloudinary
import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send, socketio


app = Flask(__name__)
app.secret_key = "Cookies"
socketio = SocketIO(app, cors_allowed_origins="*")
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
        curr_site = "index.html"
        return logout(curr_site)
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

def logout():
    if 'email' in session:
        session.pop('email', None)
        return render_template("dashboard.html", auth="Logged out")
    else:
        return render_template('index.html', auth="Error: Not logged in")

@socketio.on('message')
def handle_post(msg):
    action = msg.get('action')
    if action == 'post':
        title = msg.get('title')
        content = msg.get('content')
        mongo.db.posts.insert_one({
            "title": title,
            "content": content
        })
        print("Received post:", msg)
        if msg:
            send(msg, broadcast=True)
    elif action == 'get_posts':
        posts = mongo.db.posts.find()
        post_a = []
        for post in posts:
            post_a.append({
                "title": post['title'],
                "content": post['content']
            })
        send({ 'action': 'get_posts', 'posts': post_a })

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

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    action = request.form.get("action")
    if request.method == "POST" and action == "logout":
        return logout()
    elif request.method == "GET":
        if 'email' in session:
            return render_template("dashboard.html", auth="Logged in")
        else:
            return redirect("/auth")
    return render_template("dashboard.html")
    



if __name__ == "__main__":
    app.run(debug=True)