from flask import Flask, request
import sqlite3
import hashlib

app = Flask(__name__)

# DB erstellen
def init_db():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS daten (
        email TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# 🔐 Passwort hashen
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        hashed = hash_pw(password)

        conn = sqlite3.connect("daten.db")
        c = conn.cursor()
        c.execute("INSERT INTO daten VALUES (?, ?)", (email, hashed))
        conn.commit()
        conn.close()

        return "Gespeichert!"

    return """
    <h2>Register</h2>
    <form method="post">
        <input name="email" placeholder="Email">
        <input name="password" type="password" placeholder="Passwort">
        <button>Senden</button>
    </form>

    <a href="/liste">Liste</a>
    """

@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT rowid, email, password FROM daten")
    daten = c.fetchall()
    conn.close()

    html = "<h2>Accounts</h2>"

    for d in daten:
        html += f"<p>Email: {d[1]} | Passwort: {d[2]} <a href='/delete/{d[0]}'>löschen</a></p>"

    return html

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("DELETE FROM daten WHERE rowid = ?", (id,))
    conn.commit()
    conn.close()

    return "Gelöscht <a href='/liste'>zurück</a>"
