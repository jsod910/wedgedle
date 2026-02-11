from flask import jsonify, request, render_template, Blueprint, url_for
# import backend functions
from utils.reset_time import get_next_reset, get_server_now, get_today_date
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

@shipdle_bp.route("api/start", methods=["POST"])
def start():
    mode = request.json["mode"]

    if mode == "unlimited":
        game_id = game.start_unlimited_game()
        result = {
            "game_id": game_id,
        }
    elif mode == "daily":
        game_id = get_today_date()
        result = {
            "game_id": game_id
        }
    
    return result

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
    
    result = game.check_guess(data["guess"], data["mode"], data["game_id"])
    img = result["guess_info"]["info"]["image"]
    result["guess_info"]["info"]["image"] = url_for("static", filename=img, _external=False)

    return jsonify(result)

@shipdle_bp.route("api/shipdle/answer", methods=["POST"])
def answer():
    data = request.get_json()

    ship = game.get_target(data["mode"], data["game_id"])

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