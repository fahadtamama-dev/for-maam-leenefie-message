from flask import Flask, render_template, request, redirect, url_for, session
import os
import random
import psycopg

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-secret")

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)


def load_messages():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, message FROM messages"
        ).fetchall()

    messages = [
        {"id": row[0], "name": row[1], "message": row[2]}
        for row in rows
    ]

    random.shuffle(messages)

    return messages






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
        with get_db() as conn:
            conn.execute(
                "INSERT INTO messages (name, message) VALUES (%s, %s)",
                (name, message)
            )

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


@app.route("/delete-message/<int:message_id>", methods=["POST"])
def delete_message(message_id):

    if not session.get("admin"):
        return "Unauthorized", 403

    with get_db() as conn:
        conn.execute(
            "DELETE FROM messages WHERE id = %s",
            (message_id,)
        )

    return redirect(url_for("home"))


if DATABASE_URL:
    init_db()


if __name__ == "__main__":
    app.run(debug=True)