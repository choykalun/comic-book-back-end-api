import quart.flask_patch
import jwt
import datetime
import requests
import time

from quart import Quart
from quart import session, request, jsonify, g
from pathlib import Path
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

API_KEY = "35a08e36179322fd7a35a3286874cbb0773db196"
API_SERVER_URL = "https://comicvine.gamespot.com/api"
app = Quart(__name__)
app.secret_key = 'mysecret'
app.config.update({'DATABASE' : app.root_path/'api_server_comic.db'})

def getDB():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connectDB()
    return g.sqlite_db

def connectDB():
    engine = sqlite3.connect(app.config['DATABASE'])
    engine.row_factory = sqlite3.Row
    return engine

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "token" in request.headers:
            token = request.headers["token"]

        if not token:
            return jsonify({"message" : "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            db = getDB()
            cur = db.execute("""SELECT * FROM Users WHERE username=?""", [data["username"]])
            current_user = cur.fetchone()
        except:
            return jsonify({"message" : "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def checkRelationExists(comic_type, current_user, item):
    db = getDB()
    if comic_type == "issue":
        cur = db.execute("""SELECT * FROM UsersIssues WHERE username=? AND issueid=?""", [current_user["username"], item["id"]])
        exist = cur.fetchone()
        return exist
    elif comic_type == "volume":
        cur = db.execute("""SELECT * FROM UsersVolumes WHERE username=? AND volumeid=?""", [current_user["username"], item["id"]])
        exist = cur.fetchone()
        return exist

def checkIssueInVolume(volume, issue):
    db = getDB()
    cur = db.execute("""SELECT * FROM IssuesInVolumes WHERE issueid=? AND volumeid=?""", [issue["id"], volume["id"]])
    exist = cur.fetchone()
    return exist


def checkIfExist(comic_type, item):
    db = getDB()
    if comic_type == "issue":
        cur = db.execute("""SELECT * FROM Issues WHERE issueid=?""", [item["id"]])
        exist = cur.fetchone()
        return exist
    elif comic_type == "volume":
        cur = db.execute("""SELECT * FROM Volumes WHERE volumeid=?""", [item["id"]])
        exist = cur.fetchone()
        return exist


def addItemToDB(comic_type, item):
    db = getDB()
    if comic_type == "issue":
        cur = db.execute("""INSERT INTO Issues (name, issueid, issuenumber) VALUES (?, ?, ?)""", [item["name"], item["id"], item["issue_number"]])
        db.commit()
    elif comic_type == "volume":
        cur = db.execute("""INSERT INTO Volumes (name, volumeid, count_of_issues) VALUES (?, ?, ?)""", [item["name"], item["id"], item["count_of_issues"]])
        db.commit()

def addRelationToUser(comic_type, current_user, item):
    db = getDB()
    if comic_type == "issue":
        cur = db.execute("""INSERT INTO UsersIssues (username, issueid) VALUES (?, ?)""", [current_user["username"], item["id"]])
        db.commit()
    elif comic_type == "volume":
        cur = db.execute("""INSERT INTO UsersVolumes (username, volumeid) VALUES (?, ?)""", [current_user["username"], item["id"]])
        db.commit()


def addRelationToVolume(volume, issue):
    db = getDB()
    cur = db.execute("""INSERT INTO IssuesInVolumes (volumeid, issueid) VALUES (?, ?)""", [volume["id"], issue["id"]])
    db.commit()



@app.cli.command('init_db')
def init_db():
    db_connect = connectDB()
    with open(Path(__file__).parent/'schema.sql', mode='r') as file_:
        db_connect.cursor().executescript(file_.read())
    db_connect.commit() 


@app.route("/")
async def index():
    return "Hello World!"


@app.route("/user", methods=['POST'])
async def createUser():
    db = getDB()
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

    return jsonify({"message" : "User has been created!"}), 200


@app.route("/login", methods=['POST'])
async def login():
    db = getDB()
    auth = request.authorization
    cur = db.execute("""SELECT * FROM Users WHERE username=?""", [auth.username])
    exist = cur.fetchone()

    if not auth or not auth.username or not auth.password :
        return '{"message" : "error! username or password are empty"}', 404
    elif not exist:
        return jsonify({"message" : "The user does not exist or the username is incorrect"}), 404
    else:
        if check_password_hash(exist["password"], auth.password):
            token = jwt.encode({"username" : exist["username"], "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config["SECRET_KEY"])

            return jsonify({"token" : token.decode("UTF-8")}), 200
        return jsonify({"message" : "password is incorrect"}), 401


@app.route("/user", methods=["DELETE"])
@tokenRequired
async def deleteUser(current_user):
    db = getDB()
    cur = db.execute("""DELETE FROM Users WHERE username=?""", [current_user["username"]])
    db.commit()
    return jsonify({"message" : "User has been deleted."}), 200


@app.route("/comic/issue/<issueid>", methods=["POST"])
@tokenRequired
async def addIssueToCollectionById(current_user, issueid):
    db = getDB()

    headers = {"User-agent" : "My User-agent 1.0"}
    filter_field = "id:" + issueid
    params = {"api_key" : API_KEY, "filter" : filter_field, "field_list" : "name,id,issue_number,volume", "format" : "json"}
    url = API_SERVER_URL + "/issues"

    response = requests.get(url=url, headers=headers, params=params)
    json_response = response.json()
    issues_returned = json_response["results"]

    if len(issues_returned) == 1:
        issue_to_add = issues_returned[0]
        volume = issue_to_add["volume"]
        if not checkIfExist("issue", issue_to_add):
            addItemToDB("issue", issue_to_add)
        if not checkRelationExists("issue", current_user,issue_to_add):
            addRelationToUser("issue", current_user, issue_to_add)

        if checkIfExist("volume", volume):
            addRelationToVolume(volume, issue)

        return jsonify({"result" : "Issue added"}), 200
    else:
        return jsonify({"result" : "Please try again with the correct id"}), 404


@app.route("/comic/issue", methods=["POST"])
@tokenRequired
async def addIssueToCollection(current_user):
    db = getDB()

    #parse the json from the request
    data = await request.get_json()
    issue = data["issue"]
    headers = {"User-agent" : "My User-agent 1.0"}
    filter_field = "name:" + issue["name"]
    params = {'api_key': API_KEY, 'filter':filter_field, 'field_list':'name,id,issue_number', 'format':'json'}
    url = API_SERVER_URL + "/issues"

    response = requests.get(url=url, headers=headers, params=params)
    json_response = response.json()
    list_of_issues = json_response["results"]
    print(list_of_issues)
    result_to_add = []
    
    for i in range(len(list_of_issues)):
        if list_of_issues[i]["name"].lower() == issue["name"].lower() and list_of_issues[i]["issue_number"] == issue["issue_number"]:
            result_to_add.append(list_of_issues[i])

    if len(result_to_add) == 1:
        issue_to_add = result_to_add[0]
        cur = db.execute("""SELECT * FROM Issues WHERE issueid=?""", [issue_to_add["id"]])
        exist = cur.fetchone()
        print("1")
        if not exist:
            addItemToDB("issue", issue_to_add)
            print("2")
        if not checkRelationExists("issue", current_user, issue_to_add):
            print("3")
            addRelationToUser("issue", current_user, issue_to_add)
        return jsonify({"meessage" : "Issue added"}), 200
    else:
        print(len(result_to_add))
        return jsonify({"message" : "something went wrong"}), 401


def addIssuesFromList(current_user, volume, issues_list):
    # function to add issue by list
    # check if they are already in the database
    for each in issues_list:
        if not checkIfExist("issue", each):
            # add the issue into the database if it does not exist
            addItemToDB("issue", each)
        if not checkIssueInVolume(volume, each):
            # then add the relation for the issue to the volume
            addRelationToVolume(volume, each)
        if not checkRelationExists("issue", current_user, each):
            # finally add the issue into the user
            addRelationToUser("issue", current_user, each)


def returnListOfIssuesByVolumeID(volumeid):
    headers = {"User-agent" : "My User-agent 1.0"}
    filter_field = "volume:" + str(volumeid)
    params = {"api_key" : API_KEY, "filter" : filter_field, "field_list" : "name,id,issue_number", "format" : "json"}
    url = API_SERVER_URL + "/issues"
    response = requests.get(url=url, headers=headers, params=params)
    # get the list of issues from the response
    json_response = response.json()
    issues_returned = json_response["results"]

    if json_response["number_of_total_results"] > 100:
        count = 100
        while (len(issues_returned) != json_response["number_of_total_results"]):
            params["offset"] = count
            response = requests.get(url=url, headers=headers, params=params)
            json_response = response.json()
            issues_returned += json_response["results"]
            count += 100

    return issues_returned



@app.route("/comic/volume/<volumeid>", methods=["POST"])
@tokenRequired
async def addVolumeToCollectionById(current_user, volumeid):
    db = getDB()

    headers = {"User-agent" : "My User-agent 1.0"}
    filter_field = "id:" + str(volumeid)
    params = {"api_key" : API_KEY, "filter" : filter_field, "field_list" : "name,id,count_of_issues,image", "format" : "json"}
    url = API_SERVER_URL + "/volumes"

    response = requests.get(url=url, headers=headers, params=params)
    json_response = response.json()
    volume_returned = json_response["results"]

    if len(volume_returned) == 1:
        volume_to_add = volume_returned[0]
        if not checkIfExist("volume", volume_to_add):
            addItemToDB("volume", volume_to_add)
        if not checkRelationExists("volume", current_user, volume_to_add):
            addRelationToUser("volume", current_user, volume_to_add)

        # Fix the adding issues in this part!

        list_of_issues = returnListOfIssuesByVolumeID(volumeid)
        print(len(list_of_issues))
        addIssuesFromList(current_user, volume_to_add, list_of_issues)
        return jsonify({"result" : "Success"})


@app.route("/comic/volume", methods=["POST"])
@tokenRequired
async def addVolumeToCollection(current_user):
    # if the json object is volume, then we add the volume to the database for the user and then we also find 
    # the issues related to the volume and add them to the database 
    db = getDB()

    #parse the json from the request
    data = await request.get_json()
    volume = data["volume"]
    headers = {"User-agent" : "My User-agent 1.0"}
    filter_field = ""
    if "name" in volume:
        filter_field = "name:" + volume["name"]
    params = {"api_key" : API_KEY, "filter" : filter_field, "field_list" : "name,id,count_of_issues,image", "format" : "json"}
    url = API_SERVER_URL + "/volumes"

    response = requests.get(url=url, headers=headers, params=params)
    json_response = response.json()
    list_of_volumes = json_response["results"]
    # in order to fix this code, I will need to do something similar to get the full list of volumes and the iterate through the list 
    # and then add them to the list to insert into the database. 
    if "list_of_volumes" in data["volume"]:
        for each in data["volume"]["list_of_volumes"]:
            exist = checkIfExist("volume", each)
            if not exist:
                addItemToDB("volume", each)
            if not checkRelationExists("volume", current_user, each):
                addRelationToUser("volume", current_user, each)

            list_of_issues = returnListOfIssuesByVolumeID(each["id"])
            addIssuesFromList(current_user, each, list_of_issues)
        return jsonify({"message":"Done"}), 200


    if len(list_of_volumes) > 1:
        start_time = time.time()
        if json_response["number_of_total_results"] > 100:
            count = 100
            while (len(list_of_volumes) != json_response["number_of_total_results"]):
                params["offset"] = count
                response = requests.get(url=url, headers=headers, params=params)
                json_response = response.json()
                list_of_volumes += json_response["results"]
                count += 100
        for each in list_of_volumes:
            # make sure the response only returns the original image url of the item
            each["image"] = each["image"]["original_url"]
        end_time = time.time()
        print("Program ended in %s seconds" %(end_time - start_time))

        return jsonify({"message" : "please return a list of volumes to add from the list.", "list_of_volumes" : list_of_volumes}), 200


@app.route("/comics/volumes", methods=["GET"])
@tokenRequired
async def list_volumes(current_user):
    query_params = request.args
    list_of_volumes = []
    db = getDB()
    cur = db.execute("""SELECT volumeid FROM UsersVolumes WHERE username=?""", [current_user["username"]])
    volume_ids = cur.fetchall()
    if "filter" in query_params:
        field, value = query_params["filter"].split(":", 1)
        search_name = "%" + value + "%"
    for each in volume_ids:
        if "filter" in query_params:
            print(search_name)
            cur = db.execute("""SELECT * FROM Volumes WHERE volumeid=? AND name LIKE ?""", [each["volumeid"], search_name])
        else:
            cur = db.execute("""SELECT * FROM Volumes WHERE volumeid=?""", [each["volumeid"]])
        item = cur.fetchone()
        if item:
            list_of_volumes.append({"volumeid" : item["volumeid"], "name" : item["name"], "count_of_issues" : item["count_of_issues"]})
    if "sort" in query_params:
        sort_param = query_params["sort"].split("_")
        sort_field = sort_param[0]
        if sort_field == "name":
            newlist = sorted(list_of_volumes, key=lambda k: k[sort_field], reverse=(True if len(sort_param) > 1 and "desc" == sort_param[1] else False))
        else:
            newlist = sorted(list_of_volumes, key=lambda k: int(k[sort_field]), reverse=(True if len(sort_param) > 1 and "desc" == sort_param[1] else False))
        return jsonify({"list_of_issues" : newlist}), 200
    return jsonify({"list_of_volumes" : list_of_volumes}), 200


@app.route("/comics/issues", methods=["GET"])
@tokenRequired
async def list_issues(current_user):
    query_params = request.args
    list_of_issues = []
    db = getDB()
    cur = db.execute("""SELECT issueid FROM UsersIssues WHERE username=?""", [current_user["username"]])
    issue_ids = cur.fetchall()
    if "filter" in query_params:
        field, value = query_params["filter"].split(":", 1)
        search_name = "%" + value + "%"
    for each in issue_ids:
        if "filter" in query_params:
            if field == "volume":
                cur = db.execute("""SELECT * FROM IssuesInVolumes WHERE issueid=? AND volumeid=?""", [each["issueid"], value])
                if cur.fetchone():
                    cur = db.execute("""SELECT * FROM Issues WHERE issueid=?""", [each["issueid"]])
            else:
                cur = db.execute("""SELECT * FROM Issues WHERE issueid=? AND name LIKE ?""", [each["issueid"], search_name])
        else:
            cur = db.execute("""SELECT * FROM Issues WHERE issueid=?""", [each["issueid"]])
        item = cur.fetchone()
        if item:
            list_of_issues.append({"issueid" : item["issueid"], "name" : item["name"], "issuenumber" : item["issuenumber"]})
    if "sort" in query_params:
        sort_param = query_params["sort"].split("_")
        sort_field = sort_param[0]
        if sort_field == "name":
            newlist = sorted(list_of_issues, key=lambda k: k[sort_field], reverse=(True if len(sort_param) > 1 and "desc" == sort_param[1] else False))
        else:
            newlist = sorted(list_of_issues, key=lambda k: int(k[sort_field]), reverse=(True if len(sort_param) > 1 and "desc" == sort_param[1] else False))
        return jsonify({"list_of_issues" : newlist}), 200
    return jsonify({"list_of_issues" : list_of_issues}), 200


@app.route("/comic/issue/<issueid>", methods=["GET"])
@tokenRequired
async def get_issue(current_user, issueid):
    db = getDB()
    cur = db.execute("""SELECT issueid FROM UsersIssues WHERE username=?""", [current_user["username"]])
    issue_ids = cur.fetchall()
    for each in issue_ids:
        if issueid == each["issueid"]:
            cur = db.execute("""SELECT * FROM Issues WHERE issueid=?""", [issueid])
            item = cur.fetchone()
            if item:
                return jsonify({"issue" : {"issueid" : item["issueid"], "name" : item["name"], "issuenumber" : item["issuenumber"]}}), 200
    return jsonify({"result" : "no such issue belongs to the user"}), 404


@app.route("/comic/volume/<volumeid>", methods=["GET"])
@tokenRequired
async def get_volume(current_user, volumeid):
    db = getDB()
    cur = db.execute("""SELECT volumeid FROM UsersVolumes WHERE username=?""", [current_user["username"]])
    volume_ids = cur.fetchall()
    for each in volume_ids:
        if volumeid == each["volumeid"]:
            cur = db.execute("""SELECT * FROM Volumes WHERE volumeid=?""", [volumeid])
            item = cur.fetchone()
            if item:
                return jsonify({"volume" : {"volumeid" : item["volumeid"], "name" : item["name"], "count_of_issues" : item["count_of_issues"]}}), 200
    return jsonify({"result" : "no such volume belongs to the user"}), 404


@app.route("/comic/volume/<volumeid>", methods=["DELETE"])
@tokenRequired
async def delete_volume(current_user, volumeid):
    db = getDB()
    cur = db.execute("""SELECT * FROM UsersVolumes WHERE username=? AND volumeid=?""", [current_user["username"], volumeid])
    exist = cur.fetchone()
    if exist:
        cur = db.execute("""DELETE FROM UsersVolumes WHERE username=? AND volumeid=?""", [current_user["username"], volumeid])
        db.commit()
        cur = db.execute("""SELECT * FROM IssuesInVolumes WHERE volumeid=?""", [volumeid])
        issues_list = cur.fetchall()
        for each in issues_list:
            cur = db.execute("""DELETE FROM UsersIssues WHERE username=? AND issueid=?""", [current_user["username"], each["issueid"]])
            db.commit()
        return jsonify({"result" : "Volume has been deleted from user"}), 200
    return jsonify({"result" : "Volume not found under username"}), 404


@app.route("/comic/issue/<issueid>", methods=["DELETE"])
@tokenRequired
async def delete_issue(current_user, issueid):
    db = getDB()
    cur = db.execute("""SELECT * FROM UsersIssues WHERE username=? AND issueid=?""", [current_user["username"], issueid])
    exist = cur.fetchone()
    if exist:
        cur = db.execute("""DELETE FROM UsersIssues WHERE username=? AND issueid=?""", [current_user["username"], issueid])
        db.commit()
        return jsonify({"result" : "Issue has been deleted from user"}), 200
    return jsonify({"result" : "Issue not found under username"}), 404

