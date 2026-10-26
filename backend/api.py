"""API du morpion : enregistre les parties terminées et expose l'historique.

Uniquement la bibliothèque standard Python (http.server + sqlite3) :
aucune dépendance pip à installer dans l'image.
"""
import json
import os
import signal
import sqlite3
import threading
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from game import InvalidGame, replay

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8081"))
DB_PATH = os.environ.get("DB_PATH", "/data/games.db")
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "20"))
REQUEST_QUEUE_SIZE = int(os.environ.get("REQUEST_QUEUE_SIZE", "64"))
MAX_BODY_BYTES = 4096


def db():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(db()) as conn, conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS games (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                player_x   TEXT NOT NULL,
                player_o   TEXT NOT NULL,
                moves      TEXT NOT NULL,
                result     TEXT NOT NULL CHECK (result IN ('X', 'O', 'draw')),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )"""
        )


def clean_name(value, default):
    name = str(value or "").strip()[:20]
    return name or default


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "TicTacToeAPI/1.0"

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/health":
            self._send_json({"status": "ok"})
        elif url.path == "/api/games":
            self._list_games(parse_qs(url.query))
        elif url.path == "/api/stats":
            self._stats()
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/games":
            self._send_json({"error": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_BODY_BYTES:
            self._send_json({"error": "corps de requête invalide"}, status=400)
            return
        try:
            payload = json.loads(self.rfile.read(length))
            moves = payload["moves"]
            _, result = replay(moves)
        except (InvalidGame, ValueError, KeyError, TypeError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        player_x = clean_name(payload.get("player_x"), "Joueur X")
        player_o = clean_name(payload.get("player_o"), "Joueur O")
        with closing(db()) as conn, conn:
            cur = conn.execute(
                "INSERT INTO games (player_x, player_o, moves, result) VALUES (?, ?, ?, ?)",
                (player_x, player_o, json.dumps(moves), result),
            )
            row = conn.execute("SELECT * FROM games WHERE id = ?", (cur.lastrowid,)).fetchone()
        self._send_json(serialize(row), status=201)

    def _list_games(self, query):
        try:
            limit = min(int(query.get("limit", [HISTORY_LIMIT])[0]), HISTORY_LIMIT)
        except ValueError:
            limit = HISTORY_LIMIT
        with closing(db()) as conn:
            rows = conn.execute(
                "SELECT * FROM games ORDER BY id DESC LIMIT ?", (max(limit, 1),)
            ).fetchall()
        self._send_json([serialize(r) for r in rows])

    def _stats(self):
        with closing(db()) as conn:
            rows = conn.execute("SELECT result, COUNT(*) AS n FROM games GROUP BY result").fetchall()
        stats = {"X": 0, "O": 0, "draw": 0}
        stats.update({r["result"]: r["n"] for r in rows})
        stats["total"] = sum(stats.values())
        self._send_json(stats)

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}", flush=True)


def serialize(row):
    return {
        "id": row["id"],
        "player_x": row["player_x"],
        "player_o": row["player_o"],
        "moves": json.loads(row["moves"]),
        "result": row["result"],
        "created_at": row["created_at"],
    }


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = REQUEST_QUEUE_SIZE


def main():
    init_db()
    server = Server((HOST, PORT), ApiHandler)

    # SIGTERM (docker stop) : on arrête la boucle serve_forever() depuis un autre
    # thread (shutdown() bloque jusqu'à la fin de la boucle), on laisse finir la
    # requête en cours puis on ferme le socket proprement.
    def on_signal(signum, _frame):
        print(f"Signal {signal.Signals(signum).name} reçu, arrêt propre...", flush=True)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    print(f"API à l'écoute sur http://{HOST}:{PORT} (db={DB_PATH})", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        print("API arrêtée.", flush=True)


if __name__ == "__main__":
    main()
