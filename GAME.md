# 🎮 Treasure Flip - But du jeu

**Treasure Flip** est un jeu multijoueur en grille dans lequel chaque joueur contrôle un pion et tente de marquer un maximum de points en se déplaçant stratégiquement sur le plateau.

## 🧠 Objectif

Collecter le plus de **points** possible en **explorant** la grille et en **interagissant** avec les différentes cases.

## 🧩 Règles du jeu

- Le plateau est une grille carrée contenant différentes cases :
  - 🪙 **Coffre** (`0`) : rapporte **+1 point** s’il est activé.
  - 🔄 **Flip vertical** (`1`) : retourne tout le plateau **verticalement**.
  - 🔁 **Flip horizontal** (`2`) : retourne tout le plateau **horizontalement**.

- Chaque case a un **temps de recharge** (cooldown). Lorsqu’un joueur active une case, elle devient temporairement inutilisable.

- Les joueurs se déplacent **en tour par tour** et peuvent se déplacer dans les 4 directions :
  - Haut, Bas, Gauche, Droite (déplacements cycliques sur la grille).

- Lorsqu’un joueur marche sur une case :
  - Si le cooldown est à zéro, l’effet de la case est appliqué.
  - Sinon, rien ne se passe.

## 🎯 Conditions de victoire

- Le jeu dure un nombre fixe de tours (`nb_moves` par joueur).
- À la fin de la partie, le joueur avec le **score le plus élevé** gagne.

## 🔒 Intégrité

- Tous les déplacements sont enregistrés dans un journal.
- Un **hash MD5** du journal permet de garantir l'intégrité de la partie.

---

⚠️ Le plateau change dynamiquement si un joueur active un flip, ce qui peut inverser la position des objets et joueurs. **Anticipez bien vos mouvements !**

