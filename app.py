from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        return f"Gespeichert: {name}"

    return """
    <form method="post">
        <input name="name" placeholder="Name">
        <button>Senden</button>
    </form>
    """

# KEIN app.run()
