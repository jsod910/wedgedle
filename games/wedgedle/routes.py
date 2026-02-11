from flask import jsonify, request, render_template, Blueprint, url_for
# import backend functions
from utils.reset_time import get_next_reset, get_server_now, get_today_date
from .wedgedle import WedgedleGame

wedgedle_bp = Blueprint("wedgedle", __name__)
game = WedgedleGame()

# @wedgedle_bp.route("/")
# def index():
#     return render_template("wedgedle.html")

@wedgedle_bp.route("api/wedgedle/reset_time")
def reset_time():
    return { 
        "server_now": get_server_now().isoformat(),
        "reset_time": get_next_reset().isoformat()
    }

@wedgedle_bp.route("api/start", methods=["POST"])
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

@wedgedle_bp.route("api/wedgedle/search")
def search():
    query = request.args.get("q", "").lower()
    result = game.search_characters(query)

    for char in result:
        char["image"] = url_for("static", filename=char["image"], _external=False)

    return jsonify(result)

@wedgedle_bp.route("api/wedgedle/guess", methods=["POST"])
def guess():
    data = request.get_json()

    if "guess" not in data:
        return jsonify({"error": "Missing guess"}), 400
    
    result = game.check_guess(data["guess"], data["mode"], data["game_id"])
    img = result["guess_info"]["info"]["image"]
    result["guess_info"]["info"]["image"] = url_for("static", filename=img, _external=False)

    return jsonify(result)

@wedgedle_bp.route("api/wedgedle/answer", methods=["POST"])
def answer():
    data = request.get_json()

    character = game.get_target(data["mode"], data["game_id"])

    return jsonify({
        "id": character["id"],
        "name": character["name"],
        "alignment": character["alignment"],
        "image": url_for("static", filename=character["image"], _external=False)
    })

@wedgedle_bp.route("api/wedgedle/images")
def images():
    imgs = game.get_images()
    return jsonify([
        url_for("static", filename=img)
        for img in imgs
    ])

# if __name__ == "__main__":
#     wedgedle_bp.run(debug=True)