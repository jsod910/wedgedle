from flask import Flask, render_template
from flask_cors import CORS
# import backend functions
from games.wedgedle.routes import wedgedle_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(wedgedle_bp, url_prefix="/wedgedle")

@app.route("/")
def landing():
    return render_template("wedgedle_index.html")

# @app.route("/games/wedgedle")
# def wedgedle():
#     return render_template("wedgedle_index.html")

if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run()