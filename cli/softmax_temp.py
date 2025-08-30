# Exemple de logits (scores bruts du modèle pour 3 tokens)
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.softmax import softmax

logits = [2.0, 1.0, 0.1]
tokens = ["chat", "chien", "dragon"]

# Différentes températures à tester
temperatures = [0.1, 0.5, 1.0, 2.0, 5.0, 1000000]

for T in temperatures:
    probs = softmax(logits, T)    
    print(f"\nTempérature = {T}")
    for token, p in zip(tokens, probs):
        print(f"{token:>7} : {p:.3f}")        