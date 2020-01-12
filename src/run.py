from flask import Flask

app = Flask(__name__)

@app.route("/")
async def index():
    return "Hello World!"


