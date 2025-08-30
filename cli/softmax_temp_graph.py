import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.softmax import softmax

# Exemple de logits (scores bruts du modèle pour 3 tokens)
logits = [2.0, 1.0, 0.1]
tokens = ["chat", "chien", "dragon"]

# Différentes températures à tester
temperatures = [0.1, 0.5, 1.0, 2.0, 5.0, 1000000]

# Affichage console tokens / probabilités selon la T°
for T in temperatures:
    probs = softmax(logits, T)
    print(f"\nTempérature = {T}")
    for token, p in zip(tokens, probs):
        print(f"{token:>7} : {p:.3f}") 

# Calculer toutes les distributions
results = {T: softmax(logits, T) for T in temperatures}

# Création du graphique comparatif
x = np.arange(len(tokens))  # positions des tokens
width = 0.18                # largeur des barres

plt.figure(figsize=(8, 5))

for i, T in enumerate(temperatures):
    plt.bar(x + i*width, results[T], width, label=f"T={T}")

# Mise en forme
plt.xticks(x + width * (len(temperatures) - 1) / 2, tokens)
plt.ylabel("Probabilité")
plt.title("Effet de la température sur le softmax")
plt.ylim(0, 1)
plt.legend()
plt.show()
