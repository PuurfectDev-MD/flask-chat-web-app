# to enter the access the app - app.app_context().push()
# to access the individual user info : user= User.query.filter_by(username="username").first()  -  user.password / user.username
# to delete all info from database: db.drop_all()
#to create all the database columns : db.create_all()

from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

name = ""
profile_pic = ""
logged = False


class User(db.Model):
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(60), unique=True, nullable=False)
    image = db.Column(db.String(100), default="static/profile_pic/default.jpg")


class Msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    msg = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(50), nullable=True)
    hashtag = db.Column(db.String(20), nullable=True)
    user = db.Column(db.String(30))
    profPic = db.Column(db.String(100), default="static/profile_pic/default.jpg")


@app.route("/")
def index():
    page = ""
    f = open("html/home.html", "r")
    page += f.read()
    return page


@app.route("/signup")
def signup():
    page = ""
    f = open("html/signup.html")
    page += f.read()
    f.close()
    return page


@app.route("/newuser", methods=["POST"])
def new_user():
    data = request.form
    user = User(username=data["username"], password=data["password"])
    db.session.add(user)
    db.session.commit()

    page = ""
    page += f"""{data["username"]} your signup was successful."""
    page += f"""To continue > """
    page += f"""<a href="/">Log in</a>"""
    return page


@app.route("/login", methods=["POST"])
def login():
    global name, profile_pic, logged

    data = request.form
    user = User.query.filter_by(username=data["username"]).first()
    if user:
        password = user.password
        if password == data["password"]:
            profile_pic = user.image
            name = data["username"]
            logged = True

            return redirect("/room")
        else:
            return "Wrong Credentials"
    else:
        return "User doesnt exist."


@app.route("/room")
def room():
    if logged:
        page = ""
        f = open("html/room.html", "r")
        page += f.read()
        f.close()
        page = page.replace("{{ name }}", name)
        page = page.replace("{{ profile_pic }}", profile_pic)
        page += f"{profile_pic}"

        texts = Msg.query.filter(Msg.timestamp > datetime(2024, 5, 4)).order_by(Msg.timestamp.desc()).all()
        for text in texts:
            page += f"""<div class='message'>"""
            page += f"<div class='msgpic'><img src={text.profPic}></div>"
            page += f"<h3 class ='textusernm'>{text.user}</h3>"
            page += f"<p class='textdate'>{text.timestamp}</p>"
            page += f"""</div>"""

            page += f"""<div class="msg-container">"""
            page += f"<img class='arrow' src='static/arrow.png'>"
            page += f"<h2 class='textmsg'>{text.msg}</h2>"
            page += f"""</div>"""

            page+=f"<div class='empty'></div>"

        return page
    else:
        return "You are not logged in. Log in to continue."


@app.route("/sendmsg", methods=["POST"])
def msg():
    data = request.form
    text = Msg(timestamp=datetime.now(), msg=data["msg"], title=data["title"], hashtag=data["hashtag"], user=name)
    db.session.add(text)
    db.session.commit()
    return redirect("/room")


@app.route("/logout")
def logout():
    global name, profile_pic, logged
    name = ""
    profile_pic = ""
    logged = False
    return redirect("/")


@app.route("/home")
def home():
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
