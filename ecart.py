import numpy as np
import matplotlib.pyplot as plt

# Définir la moyenne (mu) et l'écart type (sigma)
mu = 12.93  # Moyenne
sigma = 2.8  # Écart type
note = 12  # La note à afficher

# Générer une série de valeurs de x autour de la moyenne
x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)

# Calculer la fonction de densité de la distribution normale
y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

# Calculer la densité pour la note 17
y_note = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((note - mu) / sigma) ** 2)

# Tracer le graphique
plt.plot(x, y, label="Distribution Normale")
plt.axvline(note, color='r', linestyle='--', label=f"Note {note} (y={y_note:.4f})")
plt.title(f"Distribution Normale (µ={mu}, σ={sigma})")
plt.xlabel("Valeurs")
plt.ylabel("Densité de probabilité")
plt.legend()
plt.show()
