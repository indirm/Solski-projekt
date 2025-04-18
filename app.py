from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from tinydb import TinyDB, Query

app = Flask(__name__)

app.secret_key = "your_secret_key"


COOK_USERNAME = "cook"
COOK_PASSWORD = "1234"

db = TinyDB("tables.json")
Table = Query()

if len(db) == 0:
    for num in range(1, 31):
        db.insert({"id": num, "is_taken": False})


@app.route('/')
def domov():
    return render_template('stranka.html')

@app.route("/get_number", methods=["POST"])
def get_number():
    free_table = db.get(Table.is_taken == False)

    if free_table:
        db.update({"is_taken": True}, Table.id == free_table["id"])
        return jsonify({"number": free_table["id"]})
    else:
        return jsonify({"error": "Vse stevilke so zasedene"}), 400

@app.route("/release_table/<int:table_id>", methods=["POST"])
def release_table(table_id):
    if db.contains(Table.id == table_id):
        db.update({"is_taken": False}, Table.id == table_id)
        return jsonify({"message": f"Miza {table_id} je zdaj sproščena."})
    else:
        return jsonify({"error": "Miza s tem ID-jem ne obstaja!"}), 404

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == COOK_USERNAME and password == COOK_PASSWORD:
            session["cook_logged_in"] = True
            return redirect(url_for("cook_dashboard"))
        else:
            return render_template("login.html", error="Napačno uporabniško ime ali geslo!")

    return render_template("login.html")

# Protected cook dashboard
@app.route("/cook")
def cook_dashboard():
    if not session.get("cook_logged_in"):
        return redirect(url_for("login"))
    return "Dobrodošel kuhar! Tukaj bo seznam naročil."

# Logout route
@app.route("/logout")
def logout():
    session.pop("cook_logged_in", None)
    return redirect(url_for("login"))

app.run(debug=True)