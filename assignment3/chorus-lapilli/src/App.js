import { useState } from 'react';
import './Board.css'; // Ensure you have appropriate CSS for styling

function Square({ value, onSquareClick, isSelected }) {
    return (
        <button
            className={`square ${isSelected ? 'selected' : ''}`}
            onClick={onSquareClick}
        >
            {value}
        </button>
    );
}

export default function Board() {
    const [squares, setSquares] = useState(Array(9).fill(null));
    const [xIsNext, setXIsNext] = useState(true);
    const [selectedSquare, setSelectedSquare] = useState(null); // For movement phase
    const [placementCounts, setPlacementCounts] = useState({ X: 0, O: 0 });

    // Helper function to check adjacency
    function isAdjacent(from, to) {
        const adjacentIndices = {
            0: [1, 3, 4],
            1: [0, 2, 3, 4, 5],
            2: [1, 4, 5],
            3: [0, 1, 4, 6, 7],
            4: [0, 1, 2, 3, 5, 6, 7, 8],
            5: [1, 2, 4, 7, 8],
            6: [3, 4, 7],
            7: [3, 4, 5, 6, 8],
            8: [4, 5, 7],
        };
        return adjacentIndices[from].includes(to);
    }

    // Helper function to check if player can win in this move
    function canWin(squares, player) {
        const lines = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ];
        for (let line of lines) {
            const [a, b, c] = line;
            const lineValues = [squares[a], squares[b], squares[c]];
            const count = lineValues.filter(val => val === player).length;
            const empty = lineValues.indexOf(null);
            if (count === 2 && empty !== -1) {
                return line[empty];
            }
        }
        return null;
    }

    function handleClick(i) {
        const currentPlayer = xIsNext ? 'X' : 'O';
        const opponent = xIsNext ? 'O' : 'X';
        let winner = calculateWinner(squares); // Changed from const to let

        if (winner) {
            return; // Game already won
        }

        const playerPlacementCount = placementCounts[currentPlayer];

        // Determine if we're in Placement Phase or Movement Phase
        const isPlacementPhase = playerPlacementCount < 3;

        if (isPlacementPhase) {
            // Placement Phase
            if (squares[i]) {
                return; // Square already occupied
            }
            const newSquares = squares.slice();
            newSquares[i] = currentPlayer;
            setSquares(newSquares);
            setPlacementCounts({
                ...placementCounts,
                [currentPlayer]: playerPlacementCount + 1,
            });
            setXIsNext(!xIsNext);
        } else {
            // Movement Phase
            if (selectedSquare === null) {
                // First click: select a piece to move
                if (squares[i] !== currentPlayer) {
                    return; // Not player's own piece
                }

                // Special rule: If player has a piece in the center
                const hasCenter = squares[4] === currentPlayer;
                if (hasCenter) {
                    // Must either win or vacate the center
                    // Check if any winning move is possible
                    const tempSquares = squares.slice();
                    for (let target = 0; target < 9; target++) {
                        if (isAdjacent(i, target) && tempSquares[target] === null) {
                            tempSquares[i] = null;
                            tempSquares[target] = currentPlayer;
                            if (calculateWinner(tempSquares) === currentPlayer) {
                                // Player can win by moving this piece
                                // Allow selection
                                setSelectedSquare(i);
                                return;
                            }
                        }
                    }
                    // If cannot win, must vacate center
                    if (i === 4) {
                        setSelectedSquare(i);
                        return;
                    } else {
                        // Cannot select other pieces
                        return;
                    }
                }

                // No center piece, allow selecting any own piece
                setSelectedSquare(i);
            } else {
                // Second click: select destination square
                if (squares[i]) {
                    return; // Destination must be empty
                }
                if (!isAdjacent(selectedSquare, i)) {
                    return; // Must move to adjacent square
                }
                // Special rule: If player has a piece in the center
                const hasCenter = squares[4] === currentPlayer;
                if (hasCenter) {
                    if (selectedSquare === 4) {
                        // Must vacate center or win
                        // Check if moving from center leads to a win
                        const newSquares = squares.slice();
                        newSquares[selectedSquare] = null;
                        newSquares[i] = currentPlayer;
                        if (calculateWinner(newSquares) === currentPlayer) {
                            setSquares(newSquares);
                            setXIsNext(!xIsNext);
                            setSelectedSquare(null);
                            return;
                        } else {
                            // Must vacate center
                            setSquares(newSquares);
                            setXIsNext(!xIsNext);
                            setSelectedSquare(null);
                            return;
                        }
                    } else {
                        // Check if moving another piece leads to a win
                        const newSquares = squares.slice();
                        newSquares[selectedSquare] = null;
                        newSquares[i] = currentPlayer;
                        if (calculateWinner(newSquares) === currentPlayer) {
                            // Moving this piece leads to a win
                            setSquares(newSquares);
                            setXIsNext(!xIsNext);
                            setSelectedSquare(null);
                            return;
                        } else {
                            // Cannot move other pieces unless it leads to a win
                            return;
                        }
                    }
                }
                // Move the piece normally if no center piece restrictions
                const newSquares = squares.slice();
                newSquares[selectedSquare] = null;
                newSquares[i] = currentPlayer;
                setSquares(newSquares);
                setXIsNext(!xIsNext);
                setSelectedSquare(null);
            }
        }
    }

    // Correctly define 'winner' as a const after handleClick
    const winnerFinal = calculateWinner(squares);
    let status;
    if (winnerFinal) {
        status = 'Winner: ' + winnerFinal;
    } else {
        const currentPlayer = xIsNext ? 'X' : 'O';
        const playerPlacementCount = placementCounts[currentPlayer];
        const isPlacementPhase = playerPlacementCount < 3;
        status = isPlacementPhase
            ? 'Next player: ' + currentPlayer
            : 'Next player: ' + currentPlayer + ' (move a piece)';
    }

    // Determine if in Movement Phase
    const totalPlacements = placementCounts['X'] + placementCounts['O'];
    const isMovementPhase = totalPlacements >= 6;

    return (
        <div className="game">
            <h1>Chorus Lapilli</h1>
            <div className='status'>{status}</div>
            <div className="board">
                {[0, 1, 2].map(row => (
                    <div key={row} className="board-row">
                        {[0, 1, 2].map(col => {
                            const index = row * 3 + col;
                            return (
                                <Square
                                    key={index}
                                    value={squares[index]}
                                    onSquareClick={() => handleClick(index)}
                                    isSelected={selectedSquare === index}
                                />
                            );
                        })}
                    </div>
                ))}
            </div>
            {isMovementPhase && selectedSquare !== null && (
                <div className="instructions">
                    Select a destination square for your selected piece.
                </div>
            )}
            <button
                className="reset-button"
                onClick={() => {
                    setSquares(Array(9).fill(null));
                    setXIsNext(true);
                    setSelectedSquare(null);
                    setPlacementCounts({ X: 0, O: 0 });
                }}
            >
                Reset Game
            </button>
        </div>
    );
}

function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ];
    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a];
        }
    }
    return null;
}
