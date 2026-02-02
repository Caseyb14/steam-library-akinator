import os
import requests
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "super_secret_key"

db = SQL("sqlite:///game.db")
RAWG_API_KEY = "5b3343418f5b4625a849e044a378660e"

# --- HELPER: Fetch Image URL ---
def get_game_image(game_name):
    """Fetches the box art URL from RAWG for a specific game."""
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={game_name}"
        response = requests.get(url)
        data = response.json()
        if data["count"] > 0:
            return data["results"][0]["background_image"]
    except:
        return None
    return None

# --- HELPER: Validation ---
def validate_game_exists(game_name):
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={game_name}"
    response = requests.get(url)
    data = response.json()
    if data["count"] > 0:
        return data["results"][0]["name"]
    return None

@app.route("/")
def index():
    # RESET everything for a new game
    session["current_node_id"] = 1
    session["history"] = []       # [NEW] Stores path for Undo
    session["step_count"] = 1     # [NEW] Question Counter
    return redirect("/game")

@app.route("/game", methods=["GET", "POST"])
def game():
    node_id = session.get("current_node_id", 1)
    rows = db.execute("SELECT * FROM nodes WHERE id = ?", node_id)

    if not rows:
        return "Error: Node not found", 404

    current_node = rows[0]

    # 1. IF IT'S A QUESTION
    if current_node["is_question"] == 1:
        return render_template("question.html",
                               node=current_node,
                               step=session.get("step_count", 1))

    # 2. IF IT'S A GUESS (ANSWER)
    else:
        # [NEW] Fetch the image before showing the page
        image_url = get_game_image(current_node["text"])
        return render_template("guess.html", node=current_node, image=image_url)

@app.route("/answer", methods=["POST"])
def answer():
    choice = request.form.get("choice")
    node_id = session.get("current_node_id")

    # [NEW] Save current spot to history BEFORE moving
    if "history" not in session:
        session["history"] = []
    session["history"].append(node_id)

    # [NEW] Increment step counter
    session["step_count"] = session.get("step_count", 1) + 1

    # Logic to move down
    row = db.execute("SELECT * FROM nodes WHERE id = ?", node_id)
    current_node = row[0]

    if choice == "yes":
        session["current_node_id"] = current_node["yes_id"]
    elif choice == "no":
        session["current_node_id"] = current_node["no_id"]

    return redirect("/game")

# --- [NEW] UNDO ROUTE ---
@app.route("/undo")
def undo():
    # If there is history, go back one step
    if session.get("history"):
        last_node_id = session["history"].pop() # Remove last item
        session["current_node_id"] = last_node_id
        session["step_count"] -= 1              # Decrease step count
    return redirect("/game")

# --- EXISTING ROUTES (No changes needed below here) ---
@app.route("/win")
def win():
    return render_template("win.html")

@app.route("/lose")
def lose():
    return render_template("lose.html")

@app.route("/check_game", methods=["POST"])
def check_game():
    user_input = request.form.get("game_name")
    found_name = validate_game_exists(user_input)
    if not found_name:
        return render_template("lose.html", error=f"No matches found for '{user_input}'.")
    return render_template("confirm.html", user_input=user_input, found_game=found_name)

@app.route("/confirm_game", methods=["POST"])
def confirm_game():
    confirmed_name = request.form.get("confirmed_name")
    session["new_game_name"] = confirmed_name
    return redirect("/add_question")

@app.route("/add_question", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("add_question.html", new_game=session.get("new_game_name"))

    question_text = request.form.get("question")
    side = request.form.get("side")
    current_node_id = session.get("current_node_id")
    new_game_name = session.get("new_game_name")

    old_node = db.execute("SELECT * FROM nodes WHERE id = ?", current_node_id)[0]
    old_game_name = old_node["text"]

    new_game_id = db.execute("INSERT INTO nodes (text, is_question) VALUES (?, 0)", new_game_name)
    old_game_moved_id = db.execute("INSERT INTO nodes (text, is_question) VALUES (?, 0)", old_game_name)

    if side == "yes":
        db.execute("UPDATE nodes SET text = ?, is_question = 1, yes_id = ?, no_id = ? WHERE id = ?",
                   question_text, new_game_id, old_game_moved_id, current_node_id)
    else:
        db.execute("UPDATE nodes SET text = ?, is_question = 1, yes_id = ?, no_id = ? WHERE id = ?",
                   question_text, old_game_moved_id, new_game_id, current_node_id)

    return redirect("/")

@app.route("/stats")
def stats():
    # 1. Count total games (Leaf nodes)
    games_count = db.execute("SELECT COUNT(*) as n FROM nodes WHERE is_question = 0")[0]["n"]

    # 2. Count total questions (Internal nodes)
    questions_count = db.execute("SELECT COUNT(*) as n FROM nodes WHERE is_question = 1")[0]["n"]

    # 3. Get the 5 most recently added games (highest IDs)
    recent_games = db.execute("SELECT text FROM nodes WHERE is_question = 0 ORDER BY id DESC LIMIT 5")

    return render_template("stats.html",
                           games_count=games_count,
                           questions_count=questions_count,
                           recent_games=recent_games)
