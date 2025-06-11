# Multi-player fully distributed game

### Master 1 Informatique - UE Systèmes Distribués
### Université de Toulouse / Faculté des Sciences et de l'Ingénieur
### 2024–2025 Academic year

## Authors
- <a href="https://github.com/ibanlegi"><img src="https://github.com/ibanlegi.png" width="25" height="25" style="border-radius: 50%; vertical-align: middle;"/></a> LEGINYORA Iban

## Table of Contents
1. [Project Description](#project-description)
2. [Files Description](#files-description)
3. [Running with zellij](#running-with-zellij)
4. [Reference](#reference)

## Project Description
The objective of the project is to implement several synchronization algorithms. To achieve this, we use a small multiplayer game. The files `player.py` and `display.py` do not handle synchronization between players, which leads to a final state where each player has a different view of the results. Therefore, several algorithms have been implemented to solve this problem.

### Algorithm used
- Centralized approach:
A single coordinator is responsible for granting access to the critical section. Players must request permission from this central authority before making a move.

- Token-based approach:
A unique token circulates among players. Only the player holding the token can access the critical section, ensuring mutual exclusion.

- Ricart and Agrawala mutual exclusion:
A fully distributed algorithm where a player sends timestamped requests to all others and waits for replies before entering the critical section. This ensures total ordering of events.

- Naimi-Trehel approach:
An optimized token-based method where the token is passed along a dynamic logical tree based on request paths, reducing unnecessary message passing.

- Maekawa approach:
Each player communicates only with a predefined subset (quorum) of other players. Mutual exclusion is achieved when all members of the quorum grant permission, minimizing communication overhead.


## Files Description

### Project Structure

```
.
├── GAME.md
├── LICENSE
├── README.md
├── *.py
├── *.kdl
└── zellij
```

---

### Main Files

* **`GAME.md`**:
  Game-specific documentation explaining how it works and its rules.

* **`README.md`**:
  Main project description file. Presents the purpose and usage of the project.

---

### Python Files (Game Logic and Synchronization)

* **`display.py`**:
  Acts as the main game server. It uses `curses` to display the board, receives player actions, and applies game logic (movement, bombs, scoring…).

* **`player.py`**:
  Client script used by each player to send their moves to the server. Can simulate automatic (random) behavior.

* **`server.py`**:
  Basic version of the server **without synchronization**. Serves as a reference to understand consistency issues between players.

* **`server_jeton.py`**:
  Implements synchronization based on **token passing**.

* **`server_ricart.py`**:
  Implements the **Ricart and Agrawala mutual exclusion algorithm**, which uses timestamped distributed requests.

* **`server_naimi.py`**:
  Implements the **Naimi-Trehel method**, an optimized token-based algorithm using a logical tree structure.

* **`server_maekawa.py`**:
  Implements the **Maekawa algorithm**, which uses **quorums** to reduce the number of messages needed for mutual exclusion.

---

### Sprite Files (Display)

* **`sprites.py` / `sprites_bomb.py` / `sprites_micro.py` / `sprites_small.py`**:
  Contain variables or functions defining **ASCII sprites** or characters used to represent players, bombs, etc., on the screen.

---

### `.kdl` Files (Configuration)

* **`layout_server.kdl`** and variants (`layout_server_jeton.kdl`, etc.):
  Configuration files used to define the process/server layout for each algorithm version. The `.kdl` format structures logical topologies.

---

### Other

* **`zellij`**:
  File used to automate or manage terminal sessions with [Zellij](https://zellij.dev/), a terminal workspace manager.

---

## Running with zellij
To run the different synchronization approaches, simply execute the following command:

```bash
./zellij --layout layout_server.kdl
```
---

## Reference

* This work is inspired by content from the [Multi-player Fully Distributed Game Lab – IRIT](https://www.irit.fr/~Georges.Da-Costa/distributed-systems/), as well as lectures and guidance provided by **Georges DA-COSTA (IRIT)**.

* [Ricart–Agrawala Algorithm – Wikipedia](https://en.wikipedia.org/wiki/Ricart%E2%80%93Agrawala_algorithm)

* [Naimi–Trehel Algorithm – French Wikipedia](https://fr.wikipedia.org/wiki/Algorithme_de_Naimi-Trehel)

* [Maekawa's Algorithm – French Wikipedia](https://fr.wikipedia.org/wiki/Algorithme_de_Maekawa)

---

