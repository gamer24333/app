from flask import Flask, request
import sqlite3

app = Flask(__name__)

# 🔧 Datenbank erstellen (falls noch nicht da)
def init_db():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS daten (name TEXT)")
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")

        # 💾 speichern in Datenbank
        conn = sqlite3.connect("daten.db")
        c = conn.cursor()
        c.execute("INSERT INTO daten VALUES (?)", (name,))
        conn.commit()
        conn.close()

        return f"Gespeichert: {name}"

    return """
    <h2>SQLite Test</h2>
    <form method="post">
        <input name="name" placeholder="Name">
        <button>Senden</button>
    </form>
    <a href="/liste">Alle Einträge anzeigen</a>
    """

# 📋 alle Daten anzeigen
@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT * FROM daten")
    daten = c.fetchall()
    conn.close()

    ausgabe = "<h2>Gespeicherte Daten</h2>"
    for d in daten:
        ausgabe += f"<p>{d[0]}</p>"

    return ausgabe

# ❗ wichtig für Render: KEIN app.run()
