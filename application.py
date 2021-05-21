import models
from dotenv import load_dotenv
import os
from flask import Flask, request
app = Flask(__name__)
from flask_cors import CORS
CORS(app)
import sqlalchemy
from flask_bcrypt import Bcrypt
import jwt
import requests

bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

models.db.init_app(app)

def root():
  return 'ok'
app.route('/', methods=["GET"])(root)

def create_user():
    existing_user = models.User.query.filter_by(email=request.json["email"]).first()
    if existing_user:
        return { "message": "Email must be present and unique" }, 400
    else:
        hashed_pw = bcrypt.generate_password_hash(request.json["password"]).decode('utf-8')
        user = models.User(
        name=request.json["name"],
        email=request.json["email"],
        password=hashed_pw
        )
        models.db.session.add(user)
        models.db.session.commit()
        encrypted_id = jwt.encode({"id": user.id}, os.environ.get('JWT_SECRET'), algorithm="HS256")
        u = user.to_json()
        u['id'] = encrypted_id
        return{"message": "success", "user": u}
app.route('/users/signup', methods=["POST"])(create_user)

def login():
    user = models.User.query.filter_by(email=request.json["email"]).first()
    if not user:
        return { "message": "User not found" }, 404
    elif bcrypt.check_password_hash(user.password, request.json["password"]):
        encrypted_id = jwt.encode({"id": user.id}, os.environ.get('JWT_SECRET'), algorithm="HS256")
        u = user.to_json()
        u['id'] = encrypted_id
        return{"message": "success", "user": u}
    else:
        return { "message": "Password incorrect" }, 401
app.route('/users/login', methods=["POST"])(login)


def verify_user():
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    if not user:
        return { "message": "user not found" }, 404
    else:
        u = user.to_json()
        u['id'] = request.headers["Authorization"]
        return{"message": "user verified","user": u}
app.route('/users/verify', methods=["GET"])(verify_user)

from flask_socketio import SocketIO,send

socket_io = SocketIO(app, cors_allowed_origins="*")
app.debug=True
app.host = 'localhost'

@socket_io.on("message")
def handleMessage(msg):
    print(msg)
    send(msg, broadcast=True)
    return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    socket_io.run(app)