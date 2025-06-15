# Algorithmic Approaches – Termination, Complexity, and Code References

## 1. Client-Server Algorithm

### **Associated Files**

* [`server.py`](./srv/server.py)
* [`layout_server.kdl`](./layout/layout_server.kdl)

### **Termination**

Uses a `for` loop that stops when the total number of moves (`nb_process * 10`) is reached.

### **Theoretical Complexity**

* **Notation:** `O(N × P)`
  (where `N` is the number of players and `P` the number of monitors)
* **Messages exchanged for 3 players:**
  `3 + 3 × 10 × 3 = 93` messages

---

## 2. Token Ring Algorithm

### **Associated Files**

* [`server_jeton.py`](./srv/server_jeton.py)
* [`layout_server_jeton.kdl`](./layout/layout_server_jeton.kdl)

### **Termination**

A server detects inactivity after 2 seconds and sends a `STOP` message to its neighbor. The `STOP` circulates in a ring, and when the original server receives it again, all servers stop.

### **Theoretical Complexity**

* **Notation:** `O(N²)`
* **Messages exchanged for 3 players:**

  * `1` `TOKEN_START` message
  * `3` circulating `TOKEN` messages
  * `60` actions sent
  * `3` `STOP` messages
    **Total: 67 messages**

---

## 3. Ricart–Agrawala Algorithm

### **Associated Files**

* [`server_ricart.py`](./srv/server_ricart.py)
* [`layout_ricart.kdl`](./layout/layout_server_ricart.kdl)

### **Termination**

Each server increments an action counter. When it reaches 10, it sends a `STOP` to all. Each server builds a list of completed servers. When the list size matches the system size, it stops.

### **Theoretical Complexity**

* **Notation:** `O(N³)`
* **Messages exchanged for 3 players:**
  `3 × (2 + 2 + 2 + 10 × 2) = 78` messages

---

## 4. Naimi–Trehel Algorithm

### **Associated Files**

* [`server_naimi.py`](./srv/server_naimi.py)
* [`layout_server_naimi.kdl`](./layout/layout_server_naimi.kdl)

### **Termination**

Each move sent increments a counter. The counter is transmitted with the token. When a server reaches the threshold (`nb_process * 10`), it sends a `STOP` to all other servers, which then stop.

### **Theoretical Complexity**

* **Notation:** `O(N × P)`
* **Messages exchanged for 3 players:**
  `3 × 11 = 33` messages

---

## 5. Maekawa Algorithm

### **Associated Files**

* [`server_maekawa.py`](./srv/server_maekawa.py)
* [`layout_server_maekawa.kdl`](./layout/layout_server_maekawa.kdl)

### **Termination**

Same mechanism as Ricart–Agrawala: sending `STOP` once each player has finished their 10 actions, and stopping when all servers have finished.

### **Theoretical Complexity**

* **Notation:** `O(N × q)`
  (where `q` is the quorum size)
* **Messages exchanged for 3 players:**

  * **Minimum:** `3 × (6 + 2 + 3 + 3) = 42`
  * **Maximum:** `3 × (6 + 2 + 3 + 3 + 2) = 48`