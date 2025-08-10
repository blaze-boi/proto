from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send
from flask_pymongo import PyMongo 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# async_mode='eventlet' optional, socketio auto-detects
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app) 


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

@app.route('/')
def index():
    return render_template('sock.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost')