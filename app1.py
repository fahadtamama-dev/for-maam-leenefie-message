from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)