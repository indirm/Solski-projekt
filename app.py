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



app.run(debug=True)