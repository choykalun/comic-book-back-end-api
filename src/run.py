import quart.flask_patch

from quart import Quart
from quart import session, request, jsonify, g
from pathlib import Path
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


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

	print(data["firstname"])


	return jsonify({"message" : "User has been created!"})


@app.route("/login", methods=['POST'])
async def login():
	db = get_db()
	data = await request.get_json()
	# print(args["Username"])
	# print(args["Password"])
	if args["Username"] == "" or args["Password"] == "" :
		return '{"message" : "error! username or password are incorrect"}', 404
	# else: 
	# 	if args["Username"] != 

	return '{"message" : "Log in successful"}', 200
