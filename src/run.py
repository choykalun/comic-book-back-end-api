import quart.flask_patch
import flask_login

from quart import Quart
from quart import session, request



app = Quart(__name__)
app.secret_key = 'mysecret'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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

	return args
