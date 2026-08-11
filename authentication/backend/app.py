import datetime
import os
from functools import wraps

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import jwt

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
    supports_credentials=False,
)

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB = os.environ.get("MONGO_DB", "AuthTesting")
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_EXPIRY_MINUTES = 30

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
# users = db.users
users = db.auth_prototype_testing


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "authentication-api"}), 200


def create_token(user_id):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + datetime.timedelta(minutes=JWT_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        g.user_id = payload["sub"]
        return f(*args, **kwargs)

    return decorated


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    result = users.insert_one({"email": email, "password": hashed})

    return jsonify({"message": "User created", "user_id": str(result.inserted_id)}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_token(user["_id"])
    return jsonify({"token": token}), 200


@app.route("/me", methods=["GET"])
@token_required
def me():
    try:
        user = users.find_one({"_id": ObjectId(g.user_id)})
    except InvalidId:
        return jsonify({"error": "Invalid token subject"}), 401

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"email": user["email"], "user_id": str(user["_id"])}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
