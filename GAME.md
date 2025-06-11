
# 🎮 Game Objective: Catch the Bombs!

## 🧠 General Concept

**Catch the Bombs!** is a turn-based multiplayer game where bombs fall from the top of a grid, and players must position themselves to catch them before they reach the bottom.

## 🕹️ Objective

Each player controls an avatar at the bottom of the board. On each turn:

* A bomb may be dropped from the top of the board.
* Players send a move: left, right, or stay in place.
* Bombs fall down by one row.

### 🎯 Goal:

**Catch as many bombs as possible** before the game ends.


## 🧩 Game Rules

* The board is **10 cells wide** and **10 rows high**.
* The game is played with **2 or more players**.
* A bomb is dropped every **3 turns**.
* Players remain on the bottom row and can only move left or right (with wrap-around).
* A bomb is **caught** if it lands on the same cell as a player.


## 🔢 Scoring

* Each caught bomb gives the player **1 point**.
* The game ends after a total number of turns: `max_turns * number_of_players`.


## 💻 Technical Components

* `display.py`: manages the game server, rendering, and game logic (bomb drops, scoring, etc.).
* `player.py`: client script used to send a player's moves.
