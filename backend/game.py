"""Règles du morpion : le serveur rejoue les coups pour valider une partie."""

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


class InvalidGame(ValueError):
    pass


def winner(board):
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def replay(moves):
    """Rejoue une liste d'index (0-8), X commence. Retourne (board, résultat).

    Le résultat vaut "X", "O" ou "draw". Lève InvalidGame si la partie est
    incohérente (case occupée, coup après la fin, partie non terminée...).
    """
    if not isinstance(moves, list) or not 5 <= len(moves) <= 9:
        raise InvalidGame("une partie terminée contient entre 5 et 9 coups")

    board = [None] * 9
    for turn, cell in enumerate(moves):
        if not isinstance(cell, int) or isinstance(cell, bool) or not 0 <= cell <= 8:
            raise InvalidGame(f"coup invalide : {cell!r}")
        if board[cell] is not None:
            raise InvalidGame(f"case {cell} déjà occupée")
        if winner(board):
            raise InvalidGame("coup joué après la fin de la partie")
        board[cell] = "X" if turn % 2 == 0 else "O"

    result = winner(board)
    if result:
        return board, result
    if len(moves) == 9:
        return board, "draw"
    raise InvalidGame("la partie n'est pas terminée")
