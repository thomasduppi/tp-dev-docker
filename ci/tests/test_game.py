"""Tests unitaires des règles du morpion (backend/game.py monté en lecture seule)."""
import os
import sys
import unittest

sys.path.insert(0, os.environ.get("BACKEND_SRC", "/backend"))

from game import InvalidGame, replay  # noqa: E402


class ReplayTest(unittest.TestCase):
    def test_x_wins_on_first_row(self):
        _, result = replay([0, 3, 1, 4, 2])
        self.assertEqual(result, "X")

    def test_o_wins_on_diagonal(self):
        _, result = replay([1, 0, 2, 4, 3, 8])
        self.assertEqual(result, "O")

    def test_draw(self):
        _, result = replay([0, 1, 2, 4, 3, 5, 7, 6, 8])
        self.assertEqual(result, "draw")

    def test_rejects_occupied_cell(self):
        with self.assertRaises(InvalidGame):
            replay([0, 0, 1, 2, 3])

    def test_rejects_unfinished_game(self):
        with self.assertRaises(InvalidGame):
            replay([0, 1, 2, 3, 5])

    def test_rejects_move_after_win(self):
        with self.assertRaises(InvalidGame):
            replay([0, 3, 1, 4, 2, 5])

    def test_rejects_out_of_range_cell(self):
        with self.assertRaises(InvalidGame):
            replay([0, 3, 1, 4, 9])


if __name__ == "__main__":
    unittest.main()
