from flask import Flask, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

DB_PATH = "/opt/render/project/src/daten.db"


# 🧱 DB erstellen
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()


# 🔥 SESSION CHECK (NEU WICHTIG)
def check_user():
    if "email" not in session:
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (session["email"],))
    user = c.fetchone()
    conn.close()

    if not user:
        session.clear()
        return False

    return True


# 🟢 REGISTER
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            conn.close()
            return """
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <body style="background-color:black; color:white;">
                <script>
                    alert("Diese E-Mail existiert bereits!");
                    window.location.href = "/";
                </script>
            </body>
            """

        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        return """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="background-color:black; color:white; text-align:center;">
            <h1>Account erstellt!</h1>
            <a href="/login">Zum Login</a>
        </body>
        """

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="background-color:black; color:white; text-align:center;">

        <img src="/static/bill_drinks.jpeg" width="250">

        <h1>Register</h1>

        <form method="post">
            <input name="email" placeholder="Email"><br><br>
            <input type="password" name="password" placeholder="Passwort"><br><br>
            <button>Registrieren</button>
        </form>

        <br>
        <a href="/login" style="color:white;">Zum Login</a>

    </body>
    """


# 🔵 LOGIN (FIXED)
@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect("/shop")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["email"] = email
            return redirect("/shop")

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
            <input type="password" name="password" placeholder="Passwort"><br><br>
            <button>Login</button>
        </form>

        <br>
        <a href="/" style="color:white;">Registrieren</a>

    </body>
    """


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# 📋 LISTE (FIXED mit Check)
@app.route("/liste")
def liste():
    if not check_user():
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, email, password FROM users")
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


# 👤 ACCOUNT (FIXED)
@app.route("/account")
def account():
    if not check_user():
        return redirect("/login")

    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">
        <h1>Willkommen {session["email"]}</h1>
        <a href="/logout" style="color:white;">Logout</a>
    </body>
    """


# 🛒 SHOP (FIXED Schutz)
@app.route("/shop")
def shop():
    if not check_user():
        return redirect("/login")

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="background-color:black; color:white; text-align:center;">

        <h1>Bill Drinks Shop</h1>

        <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:25px;">

            <a href="/produkt/apfel_kirsche"><img src="/static/bill_drinks_apfel_kirsche.jpeg" width="200" style="height:400px; object-fit:cover;"></a>
            <a href="/produkt/duran_orange"><img src="/static/bill_drinks_duran_orange.jpeg" width="200" style="height:400px; object-fit:cover;"></a>
            <a href="/produkt/melone_mango"><img src="/static/bill_drinks_melone_mango.jpeg" width="200" style="height:400px; object-fit:cover;"></a>
            <a href="/produkt/pflaume_kokosnuss"><img src="/static/bill_drinks_pflaume_kokosnuss.jpeg" width="200" style="height:400px; object-fit:cover;"></a>
            <a href="/produkt/ananas_drachenfrucht"><img src="/static/bill_drinks_ananas_drachenfrucht.jpeg" width="200" style="height:400px; object-fit:cover;"></a>
            <a href="/produkt/erdbeere_blaubeere"><img src="/static/bill_drinks_erdbeere_blaubeere.jpeg" width="200" style="height:400px; object-fit:cover;"></a>

        </div>

        <br>
        <a href="/logout" style="color:white;">Logout</a>

    </body>
    """


# 🧃 PRODUKT
@app.route("/produkt/<name>")
def produkt(name):
    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">

        <h1>{" ".join(name.split("_")).title()}</h1>

        <p>Preis: 1,99 €</p>

        <button onclick="alert('Die kaufen Funktion kommt bald!')">Kaufen</button>

        <br><br>
        <a href="/shop" style="color:white;">Zurück</a>

    </body>
    """


# ❌ DELETE (FIXED + SAFE)
@app.route("/delete/<int:id>")
def delete(id):
    if not check_user():
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT email FROM users WHERE id = ?", (id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return "User nicht gefunden"

    if session["email"] != result[0]:
        conn.close()
        return "Nicht erlaubt"

    c.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    session.clear()

    return """
    <body style="background-color:black; color:white; text-align:center;">
        Gelöscht!
        <br>
        <a href="/login" style="color:white;">Login</a>
    </body>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
