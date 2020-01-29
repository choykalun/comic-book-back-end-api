import quart.flask_patch
import jwt
import datetime

from quart import Quart
from quart import session, request, jsonify, g
from pathlib import Path
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Quart(__name__)
app.secret_key = 'mysecret'
app.config.update({'DATABASE' : app.root_path/'api_server_comic.db'})

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def connect_db():
	engine = sqlite3.connect(app.config['DATABASE'])
	engine.row_factory = sqlite3.Row
	return engine

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if "token" in request.headers:
			token = request.headers["token"]

		if not token:
			return jsonify({"message" : "Token is missing!"}), 401

		try:
			data = jwt.decode(token, app.config["SECRET_KEY"])
			db = get_db()
			cur = db.execute("""SELECT * FROM Users WHERE username=?""", [data["username"]])
			current_user = cur.fetchone()
		except:
			return jsonify({"message" : "Token is invalid!"}), 401

		return f(current_user, *args, **kwargs)

	return decorated


@app.cli.command('init_db')
def init_db():
	db_connect = connect_db()
	with open(Path(__file__).parent/'schema.sql', mode='r') as file_:
		db_connect.cursor().executescript(file_.read())
	db_connect.commit() 


@app.route("/")
async def index():
    return "Hello World!"

@app.route("/user", methods=['POST'])
async def create_user():
	db = get_db()
	data = await request.get_json()
	cur = db.execute("""SELECT * FROM Users WHERE email=?""", [data["email"]])
	exist = cur.fetchall()

	if len(exist) > 0:
		return jsonify({"message" : "This email already exists"}), 409
	else:
		hashed_password = generate_password_hash(data["password"], method="sha256")
		cur = db.execute("""INSERT INTO Users (firstname, lastname, email, password, username) VALUES (?, ?, ?, ?, ?)""", [data["firstname"], data["lastname"], 
			data["email"], hashed_password, data["username"]])
		db.commit()


	return jsonify({"message" : "User has been created!"})


@app.route("/login", methods=['POST'])
async def login():
	db = get_db()
	auth = request.authorization
	cur = db.execute("""SELECT * FROM Users WHERE username=?""", [auth.username])
	exist = cur.fetchone()

	if not auth or not auth.username or not auth.password :
		return '{"message" : "error! username or password are empty"}', 404
	elif not exist:
		return jsonify({"message" : "The user does not exist or the username is incorrect"}), 404
	else:
		if check_password_hash(exist["password"], auth.password):
			token = jwt.encode({"username" : exist["username"], "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config["SECRET_KEY"])

			return jsonify({"token" : token.decode("UTF-8")})
		return jsonify({"message" : "password is incorrect"}), 401


@app.route("/user", methods=["DELETE"])
@token_required
async def delete_user(current_user):
	db = get_db()
	print(current_user["username"])
	cur = db.execute("""DELETE FROM Users WHERE username=?""", [current_user["username"]])
	db.commit()
	return jsonify({"message" : "User has been deleted."})
