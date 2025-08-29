import numpy as np

def softmax(logits, T=1.0):
    """
    Calcule le softmax avec une température donnée
    P(i)=∑j​ezj​/Tezi​/T​
    """
    logits = np.array(logits) / T
    exp = np.exp(logits - np.max(logits))  # pour stabilité numérique
    return exp / exp.sum()

# Exemple de logits (scores bruts du modèle pour 3 tokens)
logits = [2.0, 1.0, 0.1]
tokens = ["chat", "chien", "dragon"]

# Différentes températures à tester
temperatures = [0.1, 0.5, 1.0, 2.0, 5.0, 1000000]

for T in temperatures:
    probs = softmax(logits, T)
    print(f"\nTempérature = {T}")
    for token, p in zip(tokens, probs):
        print(f"{token:>7} : {p:.3f}")        