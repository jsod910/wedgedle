print("STEP 1: Starting app import", flush=True)

from flask import Flask, render_template
print("STEP 1: Starting app import", flush=True)

from flask_cors import CORS
print("STEP 2: Flask imported", flush=True)

# import backend functions
from games.wedgedle.routes import wedgedle_bp
print("STEP 3: CORS imported", flush=True)
from games.shipdle.routes import shipdle_bp
print("STEP 4: Wedgedle blueprint imported", flush=True)

app = Flask(__name__)
print("STEP 5: Shipdle blueprint imported", flush=True)
CORS(app)
print("STEP 7: CORS applied", flush=True)

app.register_blueprint(wedgedle_bp, url_prefix="/wedgedle")
print("STEP 7: CORS applied", flush=True)
app.register_blueprint(shipdle_bp, url_prefix="/shipdle")
print("STEP 8: Wedgedle blueprint registered", flush=True)

@app.route("/")
def landing():
    return render_template("landing.html", game_name="wedgedle")

@app.route("/games/wedgedle")
def wedgedle():
    return render_template("wedgedle.html")

@app.route("/games/shipdle")
def shipdle():
    return render_template(
        "shipdle.html", 
        game_title="Y-Wingdle",
        game_name="shipdle"
    )


if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run()