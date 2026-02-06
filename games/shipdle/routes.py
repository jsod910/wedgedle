from flask import jsonify, request, render_template, Blueprint, url_for
# import backend functions
from utils.reset_time import get_next_reset, get_server_now
from .shipdle import ShipdleGame

shipdle_bp = Blueprint("shipdle", __name__)
game = ShipdleGame()

# @shipdle_bp.route("/")
# def index():
#     return render_template("shipdle.html")

@shipdle_bp.route("api/shipdle/reset_time")
def reset_time():
    return { 
        "server_now": get_server_now().isoformat(),
        "reset_time": get_next_reset().isoformat()
    }

@shipdle_bp.route("api/shipdle/search")
def search():
    query = request.args.get("q", "").lower()
    result = game.search_ships(query)

    for ship in result:
        ship["image"] = url_for("static", filename=ship["image"], _external=False)

    return jsonify(result)

@shipdle_bp.route("api/shipdle/guess", methods=["POST"])
def guess():
    data = request.get_json()

    if "guess" not in data:
        return jsonify({"error": "Missing guess"}), 400
    
    result = game.check_guess(data["guess"])
    img = result["guess_info"]["info"]["image"]
    result["guess_info"]["info"]["image"] = url_for("static", filename=img, _external=False)

    return jsonify(result)

@shipdle_bp.route("api/shipdle/answer")
def answer():
    ship = game.get_daily_ship();

    return jsonify({
        "id": ship["id"],
        "name": ship["name"],
        "alignment": ship["alignment"],
        "image": url_for("static", filename=ship["image"], _external=False)
    })

@shipdle_bp.route("api/shipdle/images")
def images():
    imgs = game.get_images()
    return jsonify([
        url_for("static", filename=img)
        for img in imgs
    ])

if __name__ == "__main__":
    shipdle_bp.run(debug=True)