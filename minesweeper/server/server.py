#!/usr/bin/env python3
import asyncio
import json
import logging
import websockets
import random
import uuid
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)

# Game state
class MinesweeperGame:
    def __init__(self, width=10, height=10, mines=15):
        self.width = width
        self.height = height
        self.mines = mines
        self.board = None
        self.revealed = None
        self.flagged = None
        self.game_over = False
        self.win = False
        self.initialize_board()
    
    def initialize_board(self):
        # Create empty board
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Place mines randomly
        mine_positions = set()
        while len(mine_positions) < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            mine_positions.add((x, y))
        
        # Set mines and calculate adjacent mine counts
        for x, y in mine_positions:
            self.board[y][x] = -1  # -1 represents a mine
            
            # Update adjacent cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.board[ny][nx] != -1:
                        self.board[ny][nx] += 1
    
    def reveal(self, x: int, y: int) -> List[Tuple[int, int, int]]:
        """Reveal a cell and return list of revealed cells with their values"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return []
        
        if self.revealed[y][x] or self.flagged[y][x]:
            return []
            
        revealed_cells = []
        
        # If it's a mine, game over
        if self.board[y][x] == -1:
            self.game_over = True
            self.revealed[y][x] = True
            revealed_cells.append((x, y, -1))
            return revealed_cells
            
        # Reveal current cell
        self.revealed[y][x] = True
        revealed_cells.append((x, y, self.board[y][x]))
        
        # If it's an empty cell, reveal adjacent cells recursively
        if self.board[y][x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and not self.revealed[ny][nx]:
                        revealed_cells.extend(self.reveal(nx, ny))
        
        # Check if player has won
        self.check_win()
        
        return revealed_cells
    
    def toggle_flag(self, x: int, y: int) -> bool:
        """Toggle flag on a cell and return new flag state"""
        if not (0 <= x < self.width and 0 <= y < self.height) or self.revealed[y][x]:
            return False
            
        self.flagged[y][x] = not self.flagged[y][x]
        return self.flagged[y][x]
    
    def check_win(self):
        """Check if all non-mine cells are revealed"""
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != -1 and not self.revealed[y][x]:
                    return False
        self.win = True
        self.game_over = True
        return True
    
    def get_state(self, include_mines=False):
        """Get current game state for sending to clients"""
        state = {
            "width": self.width,
            "height": self.height,
            "mines": self.mines,
            "game_over": self.game_over,
            "win": self.win,
            "cells": []
        }
        
        for y in range(self.height):
            for x in range(self.width):
                cell = {
                    "x": x,
                    "y": y,
                    "flagged": self.flagged[y][x],
                }
                
                if self.revealed[y][x] or (include_mines and self.game_over):
                    cell["value"] = self.board[y][x]
                    cell["revealed"] = True
                else:
                    cell["revealed"] = False
                
                state["cells"].append(cell)
                
        return state

# Game rooms
class GameManager:
    def __init__(self):
        self.games: Dict[str, MinesweeperGame] = {}
        self.players: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
    
    def create_game(self, width=10, height=10, mines=15) -> str:
        """Create a new game and return its ID"""
        game_id = str(uuid.uuid4())
        self.games[game_id] = MinesweeperGame(width, height, mines)
        self.players[game_id] = set()
        return game_id
    
    def join_game(self, game_id: str, websocket: websockets.WebSocketServerProtocol) -> bool:
        """Add a player to a game"""
        if game_id not in self.games:
            return False
        self.players[game_id].add(websocket)
        return True
    
    def leave_game(self, game_id: str, websocket: websockets.WebSocketServerProtocol) -> None:
        """Remove a player from a game"""
        if game_id in self.players and websocket in self.players[game_id]:
            self.players[game_id].remove(websocket)
            # Clean up empty games
            if not self.players[game_id]:
                del self.players[game_id]
                del self.games[game_id]
    
    async def broadcast_state(self, game_id: str, include_mines=False) -> None:
        """Send game state to all players in a game"""
        if game_id not in self.games or game_id not in self.players:
            return
            
        game = self.games[game_id]
        state = game.get_state(include_mines)
        
        message = json.dumps({
            "type": "state",
            "game_id": game_id,
            "state": state
        })
        
        websockets_to_remove = set()
        for websocket in self.players[game_id]:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
        
        # Clean up closed connections
        for websocket in websockets_to_remove:
            self.leave_game(game_id, websocket)

# Initialize game manager
game_manager = GameManager()

async def handle_websocket(websocket, path):
    current_game_id = None
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")
                
                if action == "create_game":
                    width = data.get("width", 10)
                    height = data.get("height", 10)
                    mines = data.get("mines", 15)
                    
                    # Validate input
                    width = max(5, min(30, width))
                    height = max(5, min(30, height))
                    mines = max(1, min(width * height // 3, mines))
                    
                    game_id = game_manager.create_game(width, height, mines)
                    current_game_id = game_id
                    game_manager.join_game(game_id, websocket)
                    
                    await websocket.send(json.dumps({
                        "type": "game_created",
                        "game_id": game_id
                    }))
                    
                    await game_manager.broadcast_state(game_id)
                
                elif action == "join_game":
                    game_id = data.get("game_id")
                    if game_manager.join_game(game_id, websocket):
                        current_game_id = game_id
                        await websocket.send(json.dumps({
                            "type": "game_joined",
                            "game_id": game_id
                        }))
                        await game_manager.broadcast_state(game_id)
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Game not found"
                        }))
                
                elif action == "reveal":
                    if not current_game_id or current_game_id not in game_manager.games:
                        continue
                        
                    game = game_manager.games[current_game_id]
                    x = data.get("x")
                    y = data.get("y")
                    
                    if game.game_over:
                        continue
                        
                    game.reveal(x, y)
                    await game_manager.broadcast_state(current_game_id, game.game_over)
                
                elif action == "flag":
                    if not current_game_id or current_game_id not in game_manager.games:
                        continue
                        
                    game = game_manager.games[current_game_id]
                    x = data.get("x")
                    y = data.get("y")
                    
                    if game.game_over:
                        continue
                        
                    game.toggle_flag(x, y)
                    await game_manager.broadcast_state(current_game_id)
                
                elif action == "restart":
                    if not current_game_id or current_game_id not in game_manager.games:
                        continue
                        
                    game = game_manager.games[current_game_id]
                    width = game.width
                    height = game.height
                    mines = game.mines
                    
                    game_manager.games[current_game_id] = MinesweeperGame(width, height, mines)
                    await game_manager.broadcast_state(current_game_id)
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if current_game_id:
            game_manager.leave_game(current_game_id, websocket)

async def main():
    host = "0.0.0.0"
    port = 8765
    
    logging.info(f"Starting Minesweeper server on {host}:{port}")
    
    async with websockets.serve(handle_websocket, host, port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
