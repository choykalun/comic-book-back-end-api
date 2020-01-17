from quart import Quart
from quart import session

app = Quart(__name__)

@app.route("/")
async def index():
    return "Hello World!"


@app.route("/login")
async def login():
	return "success"

@app.route("/comic", method=["GET", "POST"])