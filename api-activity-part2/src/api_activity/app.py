import os

from flask import Flask, jsonify, request, g
from flask_restful import Api, Resource, reqparse
from flask_talisman import Talisman

from api_activity._constants import PROJECT_ROOT
from api_activity.db import Database

_EYFILE_PATH = os.path.join(PROJECT_ROOT, "MyKey.pem")
_CERTIFICATE_PATH = os.path.join(PROJECT_ROOT, "MyCertificate.crt")

def authenticate(func):
    def wrapper(*args, **kwargs):
        # Get the username and password from the request headers
        username = request.headers.get('username')
        password = request.headers.get('password')
        db = get_db()
        stored_password = db.get_password(username)
        if stored_password is None or not Bcrypt().check_password_hash(stored_password, password):
            return jsonify({'message': 'Invalid username or password.'}), 401
        
        return func(*args, **kwargs)

    return wrapper

# Create the "hello" resource
class Hello(Resource):
    """A simple resource that for returning a hello message."""

    # Get is a special method for a resource.
    def get(self):
        return jsonify({"message": "Hello World!"})


class Square(Resource):
    """A simple resource that calculates the area of a square."""

    def get(self, num):
        return jsonify({"Shape": __class__.__name__, "Area": num * num})


class Echo(Resource):
    """A simple resource that echoes the arguments passed to it."""

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("arg1", type=str, location="args")
        parser.add_argument("arg2", type=str, location="args")

        arguments = parser.parse_args()

        # Return the arguments as JSON
        return jsonify(arguments)

def get_db():
    if "db" not in g:
        g.db = Database()
    return g.db

class Register(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username cannot be blank")
        parser.add_argument("password", type=str, required=True, help="Password cannot be blank")
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        # Hash the password before storing it
        hashed_pwd = Bcrypt().generate_password_hash(password).decode('utf-8')
        db = get_db()
        if db.add_user(username, hashed_pwd):
            return jsonify({"message": f"User {username} registered successfully"})
        else:
            return jsonify({"message": f"User {username} already exists"}), 409

class SensitiveResource(Resource):
    @authenticate
    def get(self):
        return jsonify({"message": "You are authenticated!"})


def instantiate_app() -> Flask:
    """Instantiate a new flask app"""
    # Create the flask app
    app = Flask(__name__)
    app.config["PREFERED_URL_SCHEME"] = "https"
    Talisman(app, force_https=True)

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.con.close()
    
    return app


def initialize_api(app: Flask) -> Api:
    """Initialize the api for the app and add resources to it"""

    # Create the API object
    api = Api(app)

    # Add the resources we want
    api.add_resource(Hello, "/")
    api.add_resource(Square, "/square/<int:num>")
    api.add_resource(Echo, "/echo")
    api.add_resource(Register, "/register")
    api.add_resource(SensitiveResource, "/sensitive")
    return api


def create_and_serve(debug: bool = True, with_ssl: bool = True):
    """Construct the app together with its api and then serves it"""
    app = instantiate_app()
    initialize_api(app)
    ssl_context = None if not with_ssl else (_CERTFILE_PATH, _KEYFILE_PATH)
    app.run(debug=debug)


def run(app, debug=True):
    app.run(debug=debug, ssl_context=ssl_context)
    """Run the app"""


if __name__ == "__main__":
    run(create_and_serve())




