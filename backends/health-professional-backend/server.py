from datetime import datetime, timedelta
from random import randint
from time import sleep
from uuid import uuid4

from flask import Flask, json, make_response, session, redirect, request, url_for, render_template
import requests

FRONT_URL = "http://localhost:8080"
AUTHENTICATION_LAYER_URL = "https://authentication.layer:8080"

app = Flask(__name__)

# from flask_cors import CORS
# cors = CORS(app, resources={r"/login/*": {"origins": "*"}})

app.secret_key = b"very awesomely super secret key that no one knows"

@app.after_request
def after_request(response):
    sleep(0.5)
    # Add CORS.
    header = response.headers
    header["Access-Control-Allow-Origin"] = FRONT_URL
    header["Access-Control-Allow-Credentials"] = "true"
    header["Access-Control-Allow-Headers"] = "content-type"
    return response


@app.route("/")
def home():
    return "Hello world"


@app.route("/user-info/")
def user_info():
    if "username" in session:
        return json.jsonify({"user": "Dr. Nemo"})
    return make_response("", 401)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # request the authentication layer
        data = {'username':request.form.get('login'),'password':request.form.get('password')}
        r = requests.post(AUTHENTICATION_LAYER_URL, data=data)
        print(r.text)

    return render_template('login.html', username=username, password=password)
    # return """
    #     <form method="post">
    #         <input type="submit" value="login">
    #     </form>
    # """

@app.route("/logout/")
def logout():
    session.pop("username", None)
    return redirect(FRONT_URL)


@app.route("/create-code/", methods=["POST"])
def create_code():
    code_type = request.json["type"]
    now = datetime.now()
    code = ""
    ttl = 0

    if code_type == "pincode":
        # A random number of 9 digits.
        code = str(randint(0, 999999999)).rjust(9, "0")
        ttl = 120
    else:
        code = str(uuid4())
        ttl = 3600

    delta = timedelta(seconds=ttl)
    expireAt = (now + delta).isoformat()
    return json.jsonify(
        {"type": "qrcode", "code": code, "expireAt": expireAt, "ttl": ttl,}
    )
