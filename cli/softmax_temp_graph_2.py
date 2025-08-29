import numpy as np
import matplotlib.pyplot as plt

def softmax(logits, T=1.0):
    """
    Calcule le softmax avec une température donnée
    """
    logits = np.array(logits) / T
    exp = np.exp(logits - np.max(logits))  # stabilité numérique
    return exp / exp.sum()

# Exemple de logits (scores bruts du modèle pour 3 tokens)
logits = [2.0, 1.0, 0.1]
tokens = ["chat", "chien", "dragon"]

# Gamme de températures (continue)
temperatures = np.linspace(0.1, 5, 100)  # de 0.1 à 5

# Calculer les probabilités pour chaque température
probs_by_token = {token: [] for token in tokens}

for T in temperatures:
    probs = softmax(logits, T)
    for token, p in zip(tokens, probs):
        probs_by_token[token].append(p)

# Tracer les courbes
plt.figure(figsize=(8, 5))
for token in tokens:
    plt.plot(temperatures, probs_by_token[token], label=token)

plt.xlabel("Température")
plt.ylabel("Probabilité")
plt.title("Évolution des probabilités selon la température (softmax)")
plt.ylim(0, 1)
plt.legend()
plt.grid(True)
plt.show()
