from flask import Flask, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

DATABASE_URL = os.environ.get("DATABASE_URL")


# 🔌 CONNECTION
def get_conn():
    return psycopg2.connect(DATABASE_URL)


# 👑 ADMIN CHECK (NEU)
def is_admin():
    return session.get("is_admin") == True


# 🔥 SESSION CHECK
def check_user():
    if "email" not in session:
        return False

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=%s", (session["email"],))
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

        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=%s", (email,))
        if c.fetchone():
            conn.close()
            return """
            <body style="background-color:black; color:white;">
                <script>
                    alert("Diese E-Mail existiert bereits!");
                    window.location.href = "/";
                </script>
            </body>
            """

        c.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, password)
        )

        conn.commit()
        conn.close()

        return """
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
            <input name="email" placeholder="Email" minlength="3"><br><br>
            <input type="password" name="password" placeholder="Passwort"><br><br>
            <button>Registrieren</button>
        </form>

        <br>
        <a href="/login" style="color:white;">Zum Login</a>

    </body>
    """


# 🔵 LOGIN (FIXED ADMIN)
@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect("/account")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()

        # 🔥 ADMIN MIT LADEN
        c.execute(
            "SELECT email, is_admin FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session["email"] = user[0]
            session["is_admin"] = user[1]  # 🔥 WICHTIG
            return redirect("/account")

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
            <input type="password" name="password" placeholder="Passwort" minlength="4"><br><br>
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


# 📋 LISTE
@app.route("/liste")
def liste():
    if not check_user():
        return redirect("/login")

    # 🔒 NUR ADMIN DARF LISTE SEHEN
    if not is_admin():
        return """
        <body style="background:black;color:white;text-align:center;">
            <h1>⛔ Nur Admin Zugriff</h1>
            
        </body>
                """

    
    search = request.args.get("q")

    conn = get_conn()
    c = conn.cursor()

    # 🔍 wenn gesucht wird → filter
    if search:
        c.execute(
            "SELECT id, email, password FROM users WHERE email ILIKE %s",
            (f"%{search}%",)
        )
    else:
        c.execute("SELECT id, email, password FROM users")

    daten = c.fetchall()
    conn.close()

    html = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">

        <h2>Alle Accounts (ADMIN)</h2>

        <form method="get">
            <input name="q" placeholder="Email suchen">
            <button type="submit">Suchen</button>
        </form>

        <br>
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
        <a href="/account">Zurück</a>
    </body>
    """

    return html


# 👤 ACCOUNT
@app.route("/account", methods=["GET", "POST"])
def account():
    if not check_user():
        return redirect("/login")

    # 🔥 POST LOGIK
    if request.method == "POST":
        admin_email = request.form.get("admin_email")
        if admin_email:
            return redirect(f"/make_admin/{admin_email}")

        remove_email = request.form.get("admin_lösch_email")
        if remove_email:
            return redirect(f"/remove_admin/{remove_email}")

    # 👤 NORMAL USER VIEW
    if not is_admin():
        return f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <body style="background-color:black; color:white; text-align:center;">

            <h1>Willkommen {session["email"]}</h1>

            <a href="/shop" style="color:white;">Zum Shop</a>
            <br><br>
            <a href="/logout" style="color:white;">Logout</a>

        </body>
        """

    # 👑 ADMIN VIEW
    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">

        <h1>Willkommen ADMIN {session["email"]}</h1>

        <a href="/shop" style="color:white;">Zum Shop</a>
        <br><br>
        <a href="/liste" style="color:white;">Account Liste</a>

        <br><br>

        <form method="post">
            <input name="admin_email" placeholder="Zum Admin machen">
            <button type="submit">Senden</button>

            <br><br>

            <input name="admin_lösch_email" placeholder="Admin entfernen">
            <button type="submit">Senden</button>
        </form>

        <br>
        <a href="/logout" style="color:white;">Logout</a>

    </body>
    """

@app.route("/make_admin/<email>")
def make_admin(email):
    if not is_admin():
        return "Keine Berechtigung"

    conn = get_conn()
    c = conn.cursor()

    # 🔍 CHECK: gibt es die Email überhaupt?
    c.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return "User existiert nicht"

    # 👑 Admin setzen
    c.execute("UPDATE users SET is_admin = TRUE WHERE email=%s", (email,))
    conn.commit()
    conn.close()

    return f"{email} ist jetzt Admin"

@app.route("/remove_admin/<email>")
def remove_admin(email):
    if not is_admin():
        return "Keine Berechtigung"

    conn = get_conn()
    c = conn.cursor()

    # 🔍 CHECK
    c.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return "User existiert nicht"

    c.execute("UPDATE users SET is_admin = FALSE WHERE email=%s", (email,))
    conn.commit()
    conn.close()

    return f"{email} ist kein Admin mehr"
    
# 🛒 SHOP (UNVERÄNDERT)
@app.route("/shop")
def shop():
    if not check_user():
        return redirect("/login")

    products = [
        ("apfel_kirsche", "bill_drinks_apfel_kirsche.jpeg"),
        ("duran_orange", "bill_drinks_duran_orange.jpeg"),
        ("melone_mango", "bill_drinks_melone_mango.jpeg"),
        ("pflaume_kokosnuss", "bill_drinks_pflaume_kokosnuss.jpeg"),
        ("ananas_drachenfrucht", "bill_drinks_ananas_drachenfrucht.jpeg"),
        ("erdbeere_blaubeere", "bill_drinks_erdbeere_blaubeere.jpeg"),
    ]

    html = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="background-color:black; color:white; text-align:center;">

        <h1>Bill Drinks Shop</h1>
        <a href="/spenden" class="donate-btn">
            ❤️ Spenden
        </a>
        <div class="shop">
    """

    for name, img in products:
        html += f"""
        <a href="/produkt/{name}">
            <img src="/static/{img}">
        </a>
        """

    html += """
        </div>

        <br>
        <a href="/logout" style="color:white;">Logout</a>

    </body>

    <style>
    body {
        margin: 0;
        font-family: Arial;
        overflow-x: hidden;
    }

    .shop {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 25px;
        justify-items: center;
        padding: 20px;
    }

    .shop img {
        width: 200px;
        height: 400px;
        object-fit: cover;
        border-radius: 10px;
        transition: transform 0.2s ease;
    }

    .shop img:hover {
        transform: scale(1.05);
    }

    @media (max-width: 1200px) {
        .shop { grid-template-columns: repeat(3, 1fr); }
    }

    @media (max-width: 800px) {
        .shop { grid-template-columns: repeat(2, 1fr); }
        .shop img { width: 160px; height: 320px; }
    }

    @media (max-width: 500px) {
        .shop { grid-template-columns: repeat(1, 1fr); }
        .shop img { width: 220px; height: 350px; }
    }

    .donate-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #0000ff;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """

    return html

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

# 💙 SPENDEN
@app.route("/spenden")
def spenden():
    return """
     <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <body style="
        background-color:black;
        color:white;
        text-align:center;
        font-family:Arial;
    ">

        <h1> ❤️ Bill Drinks unterstützen</h1>

        <p>
            Mit deiner Spende hilfst du uns dabei,
            neue Sorten zu entwickeln, Designs zu erstellen
            und Bill Drinks weiter auszubauen.
        </p>

        <br>

        <h2>Warum spenden?</h2>

        <p>
            Jede Unterstützung hilft uns bei:
        </p>

        <ul style="display:inline-block; text-align:left;">
            <li>🥤 Entwicklung neuer Geschmacksrichtungen</li>
            <li>🎨 Design neuer Dosen</li>
            <li>🌐 Verbesserung der Website</li>
            <li>📢 Werbung für Bill Drinks</li>
        </ul>

        <br><br>

        <!--
            <a href="DEIN_PAYPAL_LINK">
        -->

        <button onclick="alert('Die Spendenfunktion kommt bald')" style="
            padding:15px 30px;
            font-size:18px;
            border-radius:10px;
            cursor:pointer;
        ">
             ❤️ Jetzt spenden
        </button>

        <!--
        </a>
        -->
        
        <br><br>

        <a href="/shop" style="color:white;">
            Zurück zum Shop
        </a>

    </body>
    """


# ❌ DELETE (🔥 NUR ADMIN)
@app.route("/delete/<int:id>")
def delete(id):
    if not check_user():
        return redirect("/login")

    # 🔥 ADMIN CHECK
    if not is_admin():
        return "Keine Berechtigung"

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT email FROM users WHERE id=%s", (id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return "User nicht gefunden"

    c.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    if result[0] == session["email"]:
        session.clear()

    return """
    <body style="background-color:black;color:white;text-align:center;">
        Gelöscht!
        <br><br>
        <a href="/liste">Zurück</a>
    </body>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
