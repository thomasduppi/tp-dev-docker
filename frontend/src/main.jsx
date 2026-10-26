import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

function boardFromMoves(moves) {
  const board = Array(9).fill(null);
  moves.forEach((cell, turn) => { board[cell] = turn % 2 === 0 ? 'X' : 'O'; });
  return board;
}

function winningLine(board) {
  return LINES.find(([a, b, c]) => board[a] && board[a] === board[b] && board[a] === board[c]) || null;
}

function resultLabel(game) {
  if (game.result === 'draw') return 'Match nul';
  return `${game.result === 'X' ? game.player_x : game.player_o} (${game.result}) gagne`;
}

function Board({ board, line, onPlay, small = false }) {
  return (
    <div className={small ? 'board small' : 'board'}>
      {board.map((value, i) => (
        <button
          key={i}
          type="button"
          className={`cell ${value || ''} ${line && line.includes(i) ? 'win' : ''}`}
          onClick={onPlay ? () => onPlay(i) : undefined}
          disabled={!onPlay || value !== null}
          aria-label={`Case ${i + 1}${value ? ` : ${value}` : ''}`}
        >
          {value}
        </button>
      ))}
    </div>
  );
}

function App() {
  const [players, setPlayers] = useState({ x: 'Alice', o: 'Bob' });
  const [moves, setMoves] = useState([]);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);

  const board = boardFromMoves(moves);
  const line = winningLine(board);
  const finished = line !== null || moves.length === 9;
  const current = moves.length % 2 === 0 ? 'X' : 'O';

  const refresh = useCallback(async () => {
    try {
      const [games, totals] = await Promise.all([
        fetch('/api/games').then((r) => r.json()),
        fetch('/api/stats').then((r) => r.json()),
      ]);
      setHistory(games);
      setStats(totals);
      setError(null);
    } catch {
      setError("Impossible de joindre l'API");
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    if (!finished) return;
    fetch('/api/games', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_x: players.x, player_o: players.o, moves }),
    })
      .then((r) => { if (!r.ok) throw new Error(); })
      .then(refresh)
      .catch(() => setError("La partie n'a pas pu être enregistrée"));
    // On enregistre une seule fois, au moment où la partie se termine.
  }, [finished]);

  const play = (cell) => {
    if (!finished && board[cell] === null) setMoves([...moves, cell]);
  };

  let status;
  if (line) status = `${board[line[0]] === 'X' ? players.x : players.o} a gagné !`;
  else if (finished) status = 'Match nul !';
  else status = `Au tour de ${current === 'X' ? players.x : players.o} (${current})`;

  return (
    <main>
      <header>
        <h1>Morpion</h1>
        <p className="subtitle">React · Python · nginx — 100 % images maison</p>
      </header>

      <section className="game">
        <div className="players">
          <label>
            Joueur X
            <input
              value={players.x}
              maxLength={20}
              disabled={moves.length > 0}
              onChange={(e) => setPlayers({ ...players, x: e.target.value })}
            />
          </label>
          <label>
            Joueur O
            <input
              value={players.o}
              maxLength={20}
              disabled={moves.length > 0}
              onChange={(e) => setPlayers({ ...players, o: e.target.value })}
            />
          </label>
        </div>

        <p className="status">{status}</p>
        <Board board={board} line={line} onPlay={finished ? null : play} />
        <button type="button" className="primary" onClick={() => setMoves([])}>
          {finished ? 'Nouvelle partie' : 'Recommencer'}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="history">
        <h2>Historique</h2>
        {stats && (
          <ul className="stats">
            <li><strong>{stats.total}</strong> parties</li>
            <li><strong>{stats.X}</strong> victoires X</li>
            <li><strong>{stats.O}</strong> victoires O</li>
            <li><strong>{stats.draw}</strong> nuls</li>
          </ul>
        )}
        {history.length === 0 ? (
          <p className="empty">Aucune partie jouée pour l'instant.</p>
        ) : (
          <ol className="games">
            {history.map((game) => (
              <li key={game.id}>
                <button
                  type="button"
                  className={selected === game.id ? 'game-row open' : 'game-row'}
                  onClick={() => setSelected(selected === game.id ? null : game.id)}
                >
                  <span>#{game.id} — {game.player_x} vs {game.player_o}</span>
                  <span className="result">{resultLabel(game)}</span>
                  <span className="date">{game.created_at}</span>
                </button>
                {selected === game.id && (
                  <Board
                    small
                    board={boardFromMoves(game.moves)}
                    line={winningLine(boardFromMoves(game.moves))}
                  />
                )}
              </li>
            ))}
          </ol>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
