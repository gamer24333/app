from flask import Flask, request, redirect, session
import sqlite3
import os



app = Flask(__name__)
app.secret_key = "mein_geheimes_passwort"

DB_PATH =  "/opt/render/project/src/daten.db"
print("DB existiert:", os.path.exists(DB_PATH))
print("DB Größe:", os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0)
# 🧱 DB erstellen
def init_db():
    conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            conn.commit()
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
        else:
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
            
            return f"""
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <body style="background-color:black; color:white; text-align:center;">
                <h1>Willkommen {email.split("@")[0].capitalize()}</h1>
                <a href="/login" style="color:white;">Logout</a>
            </body>
            """
        else:
            return """
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
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



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# 📋 LISTE (nur für dich)
@app.route("/liste")
def liste():
    conn = sqlite3.connect(DB_PATH)
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

    html += f"""
        <br>
        <h3>Anzahl Accounts: {len(daten)}</h3>
        <a href="/" style="color:white;">Zurück</a>
    </body>
    """
    return html


@app.route("/account")
def account():

    if "email" not in session:
        return redirect("/login")

    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">
        <h1>Willkommen {session["email"]}</h1>

        <a href="/logout" style="color:white;">Logout</a>
    </body>
    
    """
    
@app.route("/shop")
def shop():

    if "email" not in session:
        return redirect("/login")

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">

        <h1>Bill Drinks Shop</h1>

        <a href="/produkt/apfel_kirsche">
            <img src="/static/bill_drinks_apfel_kirsche.jpeg" width="200">
        </a>

        <a href="/produkt/duran_orange">
            <img src="/static/bill_drinks_duran_orange.jpeg" width="200">
        </a>

        <a href="/produkt/melone_mango">
            <img src="/static/bill_drinks_melone_mango.jpeg" width="200">
        </a>

        <br><br>

        <a href="/logout" style="color:white;">Logout</a>

    </body>
    """
    
@app.route("/produkt/<name>")
def produkt(name):

    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <body style="background-color:black; color:white; text-align:center;">

        <h1>{" ".join(name.split("_")).title()} Bill Drink</h1>

        <p>Preis: 1,99 €</p>

        <button onclick= "alert('Die kaufen Funktion kommt bald!')">Kaufen</button>

        <br><br>

        <a href="/shop" style="color:white;">Zurück</a>

    </body>
    """   
    
# ❌ DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if "email" in session:
        c.execute("SELECT * FROM users WHERE id = ?", (id,))
        result = cursor.fetchone()
        gelöschte_email = result[1]
        if session["email"] == gelöschte_email:
            session.clear()
    c.execute("DELETE FROM users WHERE rowid = ?", (id,))
   
            
    conn.commit()
    conn.close()

    return """
    <body style="background-color:black; color:white; text-align:center;">
        Gelöscht! <a href='/liste' style="color:white;">Zurück</a>


        
    </body>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
