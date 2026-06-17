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
    
    """

# 📋 alle Daten anzeigen
@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT rowid, name FROM daten")
    daten = c.fetchall()
    conn.close()

    html = "<h2>Gespeicherte Daten</h2>"

    for d in daten:
        html += f"""
        <p>
            {d[1]}
            <a href="/delete/{d[0]}">❌ löschen</a>
        </p>
        """

    return html

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("DELETE FROM daten WHERE rowid = ?", (id,))
    conn.commit()
    conn.close()

    return "Gelöscht! <a href='/liste'>Zurück</a>"
# ❗ wichtig für Render: KEIN app.run()
