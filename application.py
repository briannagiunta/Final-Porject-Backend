from flask_socketio import SocketIO,send, join_room, leave_room
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
import cloudinary 
import cloudinary.uploader

bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')


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
        password=hashed_pw,
        zip=request.json['zip']
        )
        models.db.session.add(user)
        models.db.session.commit()
        encrypted_id = jwt.encode({"id": user.id}, os.environ.get('JWT_SECRET'), algorithm="HS256")
        u = user.to_json(dogs=True)
        u['id'] = encrypted_id
        return{"message": "success", "user": u}
app.route('/users/signup', methods=["POST"])(create_user)

def login():
    user = models.User.query.filter_by(email=request.json["email"]).first()
    if not user:
        return { "message": "User not found" }, 404
    elif bcrypt.check_password_hash(user.password, request.json["password"]):
        encrypted_id = jwt.encode({"id": user.id}, os.environ.get('JWT_SECRET'), algorithm="HS256")
        u = user.to_json(dogs=True)
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
        u = user.to_json(dogs=True)
        u['id'] = request.headers["Authorization"]
        return{"message": "user verified","user": u}
app.route('/users/verify', methods=["GET"])(verify_user)

def get_nearby():
    # #look up user
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    #look up all users
    all_users = models.User.query.all()
    #find all zip codes within a 30 mile radius of user
    res = requests.get(f"https://api.zip-codes.com/ZipCodesAPI.svc/1.0/FindZipCodesInRadius?zipcode={user.zip}&minimumradius=0&maximumradius=30&country=ALL&key={os.environ.get('ZIP_KEY')}")
    users = []
    #compare zips .. if user is within 30 miles of logged in user, check to see if they are a match or a potential match, if they are not, append to users list
    for u in all_users:
        for r in res.json()['DataList']:
            if r['Code'] == u.zip and u.id != user.id:
                connected = False
                for p in user.potential_matches:
                    if p.user2_id == u.id:
                        connected = True
                        break
                    else:
                        for m in user.matches:
                            if m.user1_id == u.id or m.user2_id == u.id:
                                connected = True
                                break
                if connected == False:           
                    users.append(u.to_json(dogs=True))
                                
    #send back all users within 30 mile radius
    # users=[]
    # all_users = models.User.query.all()
    # for user in all_users:
    #     users.append(user.to_json(dogs=True))

    return{"users": "nearby users", "users": users}

app.route('/users/nearby', methods=['GET'])(get_nearby)


def create_potential():
    #look up user logged in
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user1 = models.User.query.filter_by(id=decryted_id).first()
    #look up the user that the logged in user wants to match with
    user2 = models.User.query.filter_by(id=request.json["user2_id"]).first()
    #create placeholder false  match
    is_match  = False
    # look through all of the people that want to match with the logged in user
    potential_matches = models.Potential_match.query.filter_by(user2_id=user1.id).all()
    for m in potential_matches:
        #if any of them are the user that the logged in user wants to match with, then they both want to match.
        # update placeholder to show that they both want to match, delete potential match from database, break out of loop.
        if m.user1_id == user2.id:
            is_match = True
            models.db.session.delete(m)
            break
    # check placeholder, if they both want to match, create match in database and associate it with both users
    if is_match == True:
        new_match = models.Match(
            user1_id = user1.id,
            user2_id = user2.id
        )
        new_chat = models.Chat(
            user1_id = user1.id,
            user2_id = user2.id
        )
        models.db.session.add(new_match)
        models.db.session.add(new_chat)
        user1.matches.append(new_match)
        user2.matches.append(new_match)
        user1.chats.append(new_chat)
        user2.chats.append(new_chat)
        models.db.session.commit()
        return{"message":"users matched", "user": user1.to_json(matches=True)}
    # if only one wants to match, create potential match && associate it with logged in user
    else:
        new_potential_match = models.Potential_match(
            user1_id = user1.id,
            user2_id = user2.id
        )
        models.db.session.add(new_potential_match)
        user1.potential_matches.append(new_potential_match)
        models.db.session.commit()
        return{"message": "potential match created", "user": user1.to_json()}
app.route('/users/potential', methods=['POST'])(create_potential)

def get_matches():
    #look up user
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    # look through user chats and find info for everyone user has a chat with 
    chatArr = []
    for chat in user.chats:
        if chat.user1_id == user.id:
            chatArr.append({"chat": chat.to_json(), "user": models.User.query.filter_by(id=chat.user2_id).first().to_json()})
        else:
            chatArr.append({"chat": chat.to_json(), "user": models.User.query.filter_by(id=chat.user1_id).first().to_json()})
    
    return{"matches": chatArr}
app.route('/users/matches', methods=['GET'])(get_matches)

def get_messages():
    chat = models.Chat.query.filter_by(id=request.json['chat_id']).first()
    return{"chat": chat.to_json()}
app.route('/chat/messages', methods=['POST'])(get_messages)

def send_message():
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    chat = models.Chat.query.filter_by(id=request.json['chat_id']).first()
    message = models.Message(
        user_id = user.id,
        content = request.json['content']
    )
    models.db.session.add(message)
    chat.messages.append(message)
    models.db.session.commit()
    return{"message": "message sent", "chat": chat.to_json()}
app.route('/chat/send/message', methods=['POST'])(send_message)


def upload_profile_pic():
    #look up user
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    #upload pic to cloudinary
    cloudinary.config(cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'), api_secret=os.getenv('CLOUDINARY_API_SECRET'))
    res = cloudinary.uploader.upload(request.files['file'])
    # set user image to url from cloudinary
    user.image = res['url']
    models.db.session.add(user)
    models.db.session.commit()
    return {"message":"image uploaded", "user": user.to_json()}
app.route('/users/upload', methods=['POST'])(upload_profile_pic)

def about_me():
    #look up user
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    #set about column to whatever was sent 
    user.about = request.json['about']
    models.db.session.add(user)
    models.db.session.commit()
    return{"message":"SUCCESS! about me updated", "user": user.to_json()}
app.route('/users/about', methods=['POST'])(about_me)


def add_dog():
    # look up user
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    # create dog w info from user
    dog = models.Dog(
        name = request.json["name"],
        breed = request.json["breed"],
        age = request.json["age"],
        size = request.json["size"],
        description = request.json["description"]
    )
    # add dog to database and assciate dog w user
    models.db.session.add(dog)
    user.dogs.append(dog)
    models.db.session.commit()
    return{"message": "dog added", "dog": dog.to_json()}
app.route('/users/add-dog', methods=['POST'])(add_dog)


def upload_dog_pic():
    #upload pic to cloudinary
    cloudinary.config(cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'), api_secret=os.getenv('CLOUDINARY_API_SECRET'))
    res = cloudinary.uploader.upload(request.files['file'])
    #look up doggo
    dog = models.Dog.query.filter_by(id=request.headers['dogId']).first()
    # set image to url from cloudinary
    dog.image = res['url']
    models.db.session.add(dog)
    models.db.session.commit()
    return {"message":"image uploaded", "user": dog.user.to_json(dogs=True)}
app.route('/users/dog/upload', methods=['POST'])(upload_dog_pic)

def edit_dog():
    dog = models.Dog.query.filter_by(id=request.json['dogId']).first()
    dog.name = request.json['name']
    dog.breed = request.json['breed']
    dog.age = request.json['age']
    dog.size = request.json['size']
    dog.description = request.json['description']
    models.db.session.add(dog)
    models.db.session.commit()
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    return{"message": "dog updated", "user": user.to_json(dogs=True)}
app.route('/users/dog/edit', methods=['PUT'])(edit_dog)

def remove_dog():
    dog = models.Dog.query.filter_by(id=request.json['dogId']).first()
    models.db.session.delete(dog)
    models.db.session.commit()
    decryted_id = jwt.decode(request.headers["Authorization"], os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    return{"message": "dog removed", "user": user.to_json(dogs=True)}
app.route('/users/dog/remove', methods=['PUT'])(remove_dog)





socket_io = SocketIO(app, cors_allowed_origins="*")
app.debug=True
app.host = 'localhost'

@socket_io.on("message")
def handleMessage(msg, userId, chatId):
    print(msg)
    print(userId)
    print(chatId)
    decryted_id = jwt.decode(userId, os.environ.get('JWT_SECRET'), algorithms=["HS256"])['id']
    user = models.User.query.filter_by(id=decryted_id).first()
    chat = models.Chat.query.filter_by(id=chatId).first()
    message = models.Message(
        user_id = user.id,
        content = msg
    )
    models.db.session.add(message)
    chat.messages.append(message)
    models.db.session.commit()
    send(msg, broadcast=True)
    return None

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    socket_io.run(app)