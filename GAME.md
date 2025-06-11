# 🎮 But du jeu : Catch the Bombs!

## 🧠 Principe général

**Catch the Bombs!** est un jeu multijoueur tour par tour où des bombes tombent du haut d'un plateau, et les joueurs doivent se positionner pour les attraper avant qu'elles n’atteignent le bas.

---

## 🕹️ Objectif

Chaque joueur contrôle un avatar en bas du plateau. À chaque tour :

* Une bombe peut être lâchée depuis le haut du plateau.
* Les joueurs envoient un déplacement : gauche, droite ou rester sur place.
* Les bombes tombent d’une ligne vers le bas.

### 🎯 Le but :

**Attraper un maximum de bombes** avant la fin du jeu.

---

## 🧩 Règles du jeu

* Le plateau fait **10 cases de large** et **10 lignes de haut**.
* Le jeu se joue avec **2 joueurs ou plus**.
* Une bombe est lâchée tous les **3 tours**.
* Les joueurs restent sur la ligne du bas et ne peuvent se déplacer qu’à gauche ou à droite (avec wrap-around).
* Une bombe est **attrapée** si elle atterrit sur la même case qu’un joueur.

---

## 🔢 Scoring

* Chaque bombe attrapée rapporte **1 point** au joueur.
* Le jeu s’arrête après un nombre de tours définis : `nb_max_tours * nb_joueurs`.

---

## 💻 Composants techniques

* `display.py` : gère le serveur de jeu, le rendu et la logique (chute des bombes, scoring…).
* `player.py` : script client pour envoyer les déplacements d’un joueur.
