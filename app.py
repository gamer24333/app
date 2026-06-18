from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

# 🧱 DB erstellen
def init_db():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()



# 🟢 REGISTER + LOGIN STARTSEITE
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # 💾 User speichern
        conn = sqlite3.connect("daten.db")
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        return f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="background-color:black; color:white; text-align:center;">
            <h1>Account erstellt!</h1>
            <a href="/login">Zum Login</a>
        </body>
        """

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="background-color:black; color:white; text-align:center;">

        <img src="/static/bill_drink.jpeg" width="250">

        <h1>Register</h1>

        <form method="post">

            <input name="email"
                   placeholder="Email"><br><br>

            <input type="password"
                   name="password"
                   placeholder="Passwort"><br><br>

            <button>Registrieren</button>
        </form>

        <br>
        <a href="/login" style="color:white;">Zum Login</a>

    </body>
    """

# 🔵 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("daten.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            return f"""
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <body style="background-color:black; color:white; text-align:center;">
                <h1>Willkommen {email.split("@")[0].capitalize()}</h1>
                <a href="/login" style="color:white;">Logout</a>
            </body>
            """
        else:
            return """
            <body style="background-color:black; color:white; text-align:center;">
                <h1>Falsche Daten</h1>
                <a href="/login" style="color:white;">Zurück</a>
            </body>
            """

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="background-color:black; color:white; text-align:center;">

        <h1>Login</h1>

        <form method="post">

            <input name="email" placeholder="Email"><br><br>

            <input type="password"
                   name="password"
                   placeholder="Passwort"><br><br>

            <button>Login</button>
        </form>

        <br>
        <a href="/" style="color:white;">Registrieren</a>

    </body>
    """

# 📋 LISTE (nur für dich)
@app.route("/liste")
def liste():
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("SELECT rowid, email, password FROM users")
    daten = c.fetchall()
    conn.close()

    html = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">
        <h2>Alle Accounts (DEBUG)</h2>
    """

    for d in daten:
        html += f"""
        <p>
            {d[1]} | {d[2]}
            <a href="/delete/{d[0]}" style="color:white;">❌ löschen</a>
        </p>
        """

    html += """
        <br>
        <a href="/" style="color:white;">Zurück</a>
    </body>
    """
    return html

# ❌ DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("daten.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE rowid = ?", (id,))
    conn.commit()
    conn.close()

    return """
    <body style="background-color:black; color:white; text-align:center;">
        Gelöscht! <a href='/liste' style="color:white;">Zurück</a>
    </body>
    """

# ❗ kein app.run() wegen Render
