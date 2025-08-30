import numpy as np

def softmax(logits: list[float], T=1.0):
    """
    Calcule le softmax avec une température donnée
    P(i) = exp(𝑧𝑖/𝑇)/ ∑𝑗exp(𝑧𝑗/𝑇)
    Args: 
       logits (float): vecteur de scores pour chaque token / mot
    """
    logits = np.array(logits) / T
    exp = np.exp(logits - np.max(logits))  # stabilité numérique
    return exp / exp.sum()
