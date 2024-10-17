# Ecart-type +Plus
Cet outil permet de récupérer les résultats de colles sur +Plus pour afficher leur evolution dans de jolis graphiques.

## How to use

### Configuration, identifiants de connexion

Pour que le script puisse se connecter, il faut lui donner vos identifiants pou ca, créez un fichier nommé `.env` puis remplissez le.

```ini
ID=identifiant
PASSWORD=mot de passe
```

### Execution

Pour executer le code:
```sh
python ./main.py
```

Il faudra peut être télécharger des dépendances, voila la liste pour arch:
```sh
python-pandas python-dotenv python-playwright python-matplotlib python-numpy
```

### Exploitation
Le script génére un fichier `out.pdf` avec un récap de tous les résultats. Vous trouverez d'autres figures intéressantes dans `figures/` si vous activez le `plt.savefig` au début de `handle_data`.