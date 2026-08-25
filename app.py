from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room
import random
import string

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"
socketio = SocketIO(app)

QUESTIONS = [
    "Who would survive longest in prison?",
    "Who would be the best spy?",
    "Who would survive a zombie apocalypse?",
    "Who would become famous first?",
    "Who would crack under pressure first?",
    "Who would be the best liar?",
    "Who would make the worst road trip partner?",
    "Who would win a cooking contest?",
    "Who would get arrested first?",
    "Who would survive a desert island?",
    "Who would be most likely to start a cult?",
    "Who would be the best captain?",
    "Who would become a millionaire fastest?",
    "Who would be the funniest in a crisis?",
    "Who would most likely get lost in their own city?",
    "Who would absolutely win hide and seek?",
    "Who would be the best criminal mastermind?",
    "Who would ruin a party fastest?",
    "Who would win an argument with a police officer?",
    "Who would be the scariest in a horror movie?",
    "Who would survive a week without their phone?"
]

AVATARS = ["🦊", "🐼", "🐸", "🦁", "🐵", "🦄", "🐯", "🦉", "🐲", "🐻", "🐧", "🐺"]

rooms = {}
sid_map = {}


def code():
    while True:
        c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if c not in rooms:
            return c


def build_question_options(question_pool, correct_question=None):
    if correct_question is None:
        correct_question = question_pool
        question_pool = QUESTIONS
    other_questions = [q for q in question_pool if q != correct_question]
    options = random.sample(other_questions, 9) if len(other_questions) >= 9 else other_questions[:]
    options.append(correct_question)
    random.shuffle(options)
    return options


def score_board(room):
    r = rooms[room]
    return [
        {"name": name, "score": data["score"], "avatar": data.get("avatar", "🎮")}
        for name, data in sorted(r["players"].items(), key=lambda item: item[1]["score"], reverse=True)
    ]


def broadcast(room):
    r = rooms[room]
    socketio.emit("lobby_update", {
        "host": r["host"],
        "ranker": r["ranker"],
        "players": r["players"],
        "state": r["state"],
        "round": r["round"],
        "scoreboard": score_board(room),
    }, to=room)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/create")
def create():
    name = request.form["name"]
    c = code()
    rooms[c] = {
        "host": name,
        "state": "lobby",
        "round": 1,
        "question": None,
        "players": {name: {"ready": False, "score": 0, "avatar": random.choice(AVATARS)}},
        "ranking": [],
        "ranker": name,
        "guesses": {},
        "current_result": None,
    }
    session["room"] = c
    session["name"] = name
    return redirect(url_for("lobby", room=c))


@app.post("/join")
def join():
    c = request.form["code"].upper()
    if c not in rooms:
        return "Room not found", 404
    name = request.form["name"]
    if name in rooms[c]["players"]:
        rooms[c]["players"][name]["avatar"] = rooms[c]["players"][name].get("avatar", random.choice(AVATARS))
    else:
        rooms[c]["players"].setdefault(name, {"ready": False, "score": 0, "avatar": random.choice(AVATARS)})
    session["room"] = c
    session["name"] = name
    return redirect(url_for("lobby", room=c))


@app.get("/lobby/<room>")
def lobby(room):
    return render_template("lobby.html", room=room, name=session.get("name"), questions=QUESTIONS)


@socketio.on("join_room")
def on_join(data):
    room = data["room"]
    name = data["name"]
    join_room(room)
    sid_map[request.sid] = (room, name)
    broadcast(room)


@socketio.on("toggle_ready")
def ready():
    room, name = sid_map[request.sid]
    p = rooms[room]["players"][name]
    p["ready"] = not p["ready"]
    broadcast(room)


@socketio.on("start_game")
def start():
    room, name = sid_map[request.sid]
    r = rooms[room]
    if name != r["host"]:
        return

    other_players = [p for n, p in r["players"].items() if n != r["host"]]
    if not all(p["ready"] for p in other_players):
        return

    r["state"] = "ranking"
    r["question"] = random.choice(QUESTIONS)
    r["ranking"] = []
    if r["round"] == 1:
        r["ranker"] = r["host"]
    r["guesses"] = {}
    r["current_result"] = None
    for p in r["players"].values():
        p["ready"] = False

    socketio.emit("game_started", {
        "round": r["round"],
        "host": r["host"],
        "ranker": r["ranker"],
    }, to=room)
    ranker_sid = next((sid for sid, info in sid_map.items() if info == (room, r["ranker"])), None)
    if ranker_sid:
        socketio.emit("host_question", {
            "question": r["question"],
            "players": list(r["players"].keys())
        }, to=ranker_sid)
    broadcast(room)


@socketio.on("submit_ranking")
def submit_ranking(data):
    room, name = sid_map[request.sid]
    r = rooms[room]
    if name != r["ranker"] or r["state"] != "ranking":
        return

    ranking = data.get("ranking") or []
    if set(ranking) != set(r["players"]) or len(ranking) != len(r["players"]):
        return

    r["ranking"] = ranking
    r["state"] = "guessing"
    options = build_question_options(QUESTIONS, r["question"])
    socketio.emit("ranking_submitted", {
        "host": r["host"],
        "ranking": ranking,
        "question_options": options,
    }, to=room)


@socketio.on("submit_guess")
def submit_guess(data):
    room, name = sid_map[request.sid]
    r = rooms[room]
    if name == r["ranker"] or r["state"] != "guessing":
        return

    guess = data.get("guess")
    if guess is None:
        return

    if name in r["guesses"]:
        return

    player = r["players"][name]
    correct = guess == r["question"]
    if correct:
        player["score"] += 5
    r["guesses"][name] = {"guess": guess, "correct": correct}

    eligible_players = [player_name for player_name in r["players"] if player_name != r["ranker"]]
    socketio.emit("guess_received", {
        "player": name,
        "submitted": len(r["guesses"]),
        "total": len(eligible_players),
    }, to=room)
    if len(r["guesses"]) < len(eligible_players):
        return

    r["state"] = "results"
    result = {
        "correct_question": r["question"],
        "guesses": r["guesses"],
        "scoreboard": score_board(room),
    }
    r["current_result"] = result
    socketio.emit("round_result", result, to=room)
    broadcast(room)


@socketio.on("next_round")
def next_round():
    room, name = sid_map[request.sid]
    r = rooms[room]
    if name != r["host"]:
        return

    r["round"] += 1
    r["state"] = "ranking"
    r["question"] = random.choice(QUESTIONS)
    r["ranking"] = []
    r["guesses"] = {}
    r["current_result"] = None
    player_names = list(r["players"])
    next_ranker_index = (player_names.index(r["ranker"]) + 1) % len(player_names)
    r["ranker"] = player_names[next_ranker_index]
    for p in r["players"].values():
        p["ready"] = False

    socketio.emit("next_round_started", {
        "round": r["round"],
        "host": r["host"],
        "ranker": r["ranker"],
    }, to=room)
    ranker_sid = next((sid for sid, info in sid_map.items() if info == (room, r["ranker"])), None)
    if ranker_sid:
        socketio.emit("host_question", {
            "question": r["question"],
            "players": list(r["players"].keys())
        }, to=ranker_sid)


@socketio.on("disconnect")
def disc():
    info = sid_map.pop(request.sid, None)
    if not info:
        return
    room, name = info
    if room not in rooms:
        return
    rooms[room]["players"].pop(name, None)
    if rooms[room]["players"]:
        if rooms[room]["host"] == name:
            rooms[room]["host"] = next(iter(rooms[room]["players"]))
        broadcast(room)
    else:
        rooms.pop(room, None)


if __name__ == "__main__":
    socketio.run(app, debug=True)
