from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)
@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

users = []

reminders = []

@app.route("/")
# ✅ REGISTER
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    hashed_password = generate_password_hash(password)

    users.append({
        "username": username,
        "password": hashed_password
    })

    return jsonify({"message": "User Registered Successfully"})
# ✅ LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    for user in users:
        if user["username"] == username and check_password_hash(user["password"], password):
            access_token = create_access_token(identity=username)
            return jsonify({"token": access_token})

    return jsonify({"error": "Invalid credentials"}), 401

def home():
    return jsonify({"message": "Backend Connected Successfully!"})


# ✅ ADD REMINDER
@app.route("/add", methods=["POST"])
@jwt_required()
def add_reminder():
    data = request.json

    reminder = {
        "title": data.get("title"),
        "dueDate": data.get("dueDate"),
        "category": data.get("category"),
        "priority": data.get("priority", "Medium"),
        "repeatType": data.get("repeatType", "none"),
        "status": "Pending",
        "notified": False
    }

    reminders.append(reminder)
    return jsonify({"message": "Reminder Added Successfully!"})


# ✅ LIST REMINDERS
@app.route("/list", methods=["GET"])
@jwt_required()
def list_reminders():
    update_recurring()
    return jsonify(reminders)


# ✅ TOGGLE STATUS
@app.route("/toggle", methods=["POST"])
@jwt_required()
def toggle_status():
    data = request.json
    index = data.get("index")

    if index < len(reminders):
        if reminders[index]["status"] == "Pending":
            reminders[index]["status"] = "Completed"
        else:
            reminders[index]["status"] = "Pending"

        return jsonify({"message": "Status Updated"})
    
    return jsonify({"error": "Invalid Index"}), 400


# ✅ DELETE REMINDER
@app.route("/delete", methods=["POST"])
@jwt_required()
def delete_reminder():
    data = request.json
    index = data.get("index")

    if index < len(reminders):
        reminders.pop(index)
        return jsonify({"message": "Deleted Successfully"})
    
    return jsonify({"error": "Invalid Index"}), 400


# ✅ RECURRING LOGIC
def update_recurring():
    now = datetime.now()

    for reminder in reminders:
        if reminder["status"] == "Pending":
            due = datetime.fromisoformat(reminder["dueDate"])

            if due <= now and reminder["repeatType"] != "none":

                if reminder["repeatType"] == "daily":
                    new_due = due + timedelta(days=1)

                elif reminder["repeatType"] == "weekly":
                    new_due = due + timedelta(weeks=1)

                elif reminder["repeatType"] == "monthly":
                    new_due = due + timedelta(days=30)

                reminder["dueDate"] = new_due.isoformat()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)





