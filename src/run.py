import quart.flask_patch
import flask_login
import flask_sqlalchemy

from quart import Quart
from quart import session, request
from pathlib import Path
from sqlite3 import dbapi2 as sqlite3


app = Quart(__name__)
app.secret_key = 'mysecret'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.config.update({'DATABASE' : app.root_path/'api_server_comic.db'})
app.config['SQLALCHEMY_DATABASE_URI'] = app.root_path/'api_server_comic.db'
db = flask_sqlalchemy.SQLAlchemy(app)


class User(flask_login.UserMixin):
	__tablename__ = 'Users'
	userid = db.Column('userid', db.Integer, primary_key=True, unique=True)
	first_name = db.Column('firstname', db.String(20))
	last_name = db.Column('lastname', db.String(20))
	email = db.Column('email', db.String(50), unique=True)
	password = db.Column('password', db.String(80))

	def __init__(self, userid, firstname, lastname, email, password):
		self.first_name = firstname
		self.last_name = lastname
		self.email = email
		self.password = password
		self.userid = userid

def connect_db():
	engine = sqlite3.connect(app.config['DATABASE'])
	engine.row_factory = sqlite3.Row
	return engine

@app.cli.command('init_db')
def init_db():
	db = connect_db()
	with open(Path(__file__).parent/'schema.sql', mode='r') as file_:
		db.cursor().executescript(file_.read())
	db.commit() 

@app.route("/")
async def index():
    return "Hello World!"


@app.route("/login", methods=['GET', 'POST'])
async def login():
	args = request.headers
	# print(args["Username"])
	# print(args["Password"])
	if args["Username"] == "" or args["Password"] == "" :
		return '{"message" : "error! username or password are incorrect"}', 404
	# else: 
	# 	if args["Username"] != 

	return args
