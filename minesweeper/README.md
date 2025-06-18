# Minesweeper Online

A multiplayer Minesweeper game with a Python WebSocket server and Alpine.js HTML client.

## Features

- Create custom Minesweeper games with adjustable width, height, and mine count
- Multiplayer support - share your game ID with friends to play together
- Real-time updates across all connected clients
- Classic Minesweeper gameplay with left-click to reveal and right-click to flag

## Requirements

- Python 3.7+
- WebSockets library for Python

## Installation

1. Clone this repository
2. Install the required Python packages:

```bash
cd server
pip install -r requirements.txt
```

## Running the Game

1. Start the WebSocket server:

```bash
cd server
python server.py
```

2. In a separate terminal, start the HTTP server:

```bash
cd server
python http_server.py
```

3. Open your browser and navigate to:

```
http://localhost:8080
```

## How to Play

1. Set your desired board size and mine count, then click "New Game"
2. Left-click to reveal a cell
3. Right-click to flag/unflag a cell
4. To play with friends, share the Game ID displayed on your screen
5. Friends can join by entering the Game ID and clicking "Join"

## Game Rules

- The goal is to reveal all cells that don't contain mines
- Numbers indicate how many mines are adjacent to that cell
- Flag cells you suspect contain mines
- If you reveal a mine, the game is over
- If you reveal all non-mine cells, you win!

## Technical Details

- The server uses Python's WebSockets library to handle real-time communication
- The client uses Alpine.js for reactive UI updates
- Game state is managed on the server and synchronized to all connected clients

## License

MIT
