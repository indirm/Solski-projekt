from flask import Flask, jsonify,  render_template


app = Flask(__name__)

assigned_ids = set()

@app.route('/')
def domov():
    return render_template('stranka.html')

@app.route("/get_number", methods=["POST"])
def get_number():
    for num in range(1, 31):
        if num not in assigned_ids:
            assigned_ids.add(num)
            return jsonify({"number": num})
    return jsonify({"error": "Vse stevilke so zasedene"}), 400

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