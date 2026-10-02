from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-secret")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, "messages.txt")


def load_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []

    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_messages(messages):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)


@app.route("/")
def home():
    photo_folder = os.path.join(app.static_folder, "photos")

    photos = []

    if os.path.exists(photo_folder):
        for filename in os.listdir(photo_folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                photos.append(filename)

    photos.sort()

    messages = load_messages()

    return render_template(
        "maam.html",
        photos=photos,
        messages=messages
    )


@app.route("/add-message", methods=["POST"])
def add_message():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if name and message:
        messages = load_messages()

        messages.append({
            "name": name,
            "message": message
        })

        save_messages(messages)

    return redirect(url_for("home"))


@app.route("/admin-login", methods=["POST"])
def admin_login():
    password = request.form.get("password", "")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_password:
        return "ADMIN_PASSWORD is not set.", 500

    if password == admin_password:
        session["admin"] = True
        return redirect(url_for("home"))

    return "Wrong admin password.", 401


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/delete-message/<int:index>", methods=["POST"])
def delete_message(index):

    if not session.get("admin"):
        return "Unauthorized", 403

    messages = load_messages()

    if 0 <= index < len(messages):
        messages.pop(index)
        save_messages(messages)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)