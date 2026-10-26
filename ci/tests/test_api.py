"""Tests d'intégration : la stack complète, à travers le reverse proxy."""
import json
import os
import unittest
import urllib.error
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://webserver:8080").rstrip("/")
TIMEOUT = float(os.environ.get("TEST_TIMEOUT", "5"))


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE_URL + path, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


class StackTest(unittest.TestCase):
    def test_webserver_health(self):
        status, _ = call("GET", "/healthz")
        self.assertEqual(status, 200)

    def test_frontend_served_through_proxy(self):
        status, body = call("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('<div id="root">', body)

    def test_spa_fallback(self):
        status, body = call("GET", "/une/route/inconnue")
        self.assertEqual(status, 200)
        self.assertIn('<div id="root">', body)

    def test_backend_health_through_proxy(self):
        status, body = call("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"status": "ok"})

    def test_game_is_saved_and_listed(self):
        _, before = call("GET", "/api/stats")
        status, body = call("POST", "/api/games", {
            "player_x": "CI-X", "player_o": "CI-O", "moves": [0, 3, 1, 4, 2],
        })
        self.assertEqual(status, 201)
        game = json.loads(body)
        self.assertEqual(game["result"], "X")

        _, history = call("GET", "/api/games")
        self.assertIn(game["id"], [g["id"] for g in json.loads(history)])

        _, after = call("GET", "/api/stats")
        self.assertEqual(json.loads(after)["X"], json.loads(before)["X"] + 1)

    def test_server_recomputes_result(self):
        status, body = call("POST", "/api/games", {"moves": [0, 1, 2, 4, 3, 5, 7, 6, 8]})
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(body)["result"], "draw")

    def test_invalid_game_rejected(self):
        status, _ = call("POST", "/api/games", {"moves": [0, 0, 1, 2, 3]})
        self.assertEqual(status, 400)

    def test_unknown_route(self):
        status, _ = call("GET", "/api/nope")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
